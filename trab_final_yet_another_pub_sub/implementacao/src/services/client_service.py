from helpers.interpretation_layer import InterpretationLayer
from models.models import CommandType, Publication, Subscription, Topic, User
import rpyc

class ClientService:
	def __init__(self, server_location, server_port):
		self.SERVER_LOCATION = server_location
		self.SERVER_PORT = server_port

	def __login(self):
		logged_in = False
		current_user = None

		while(not logged_in):
				user_id = input('Please type your user id: ')
				current_user = User(user_id)
				current_user_json = current_user.to_json()
				login_result, login_error = self.conn.root.exposed_login(current_user_json, self.__on_publication)

				if(login_error != None):
					print('Error while logging in: ', login_error)
				else:
					print(login_result)
					logged_in = True
		
		return logged_in, current_user
	
	def __handle_command_input(self, current_user):
		while True:
			command_str = input('Please type a command: ')
			command, command_error = self.interpretation_layer.decode_command(command_str)

			if(command_error == None):
				result = None
				error = None

				if(command.type == CommandType.PUB.name):
					publication: Publication = command.data
					publication.publisher = current_user
					result, error = self.conn.root.exposed_publish(publication.to_json())
				elif(command.type == CommandType.SUB.name):
					subscription: Subscription = command.data
					subscription.subscriber = current_user
					result, error = self.conn.root.exposed_subscribe(subscription.to_json())
				elif(command.type == CommandType.UNSUB.name):
					subscription: Subscription = command.data
					subscription.subscriber = current_user
					result, error = self.conn.root.exposed_unsubscribe(subscription.to_json())
				elif(command.type == CommandType.CREATE.name):
					topic: Topic = command.data
					result, error = self.conn.root.exposed_create_topic(topic.to_json())
				elif(command.type == CommandType.DELETE.name):
					topic: Topic = command.data
					result, error = self.conn.root.exposed_delete_topic(topic.to_json())
				elif(command.type == CommandType.LIST.name):
					result, error = self.conn.root.exposed_list_topics()

				if(error != None):
					print('Error executing command: ', error)
				else:
					print(result)
			else:
				print('Error with command ', command_error)

	def __on_publication(self, publication_json: str):
		publication : Publication = Publication.from_json(publication_json)

		print(publication.message.body)

	def start(self):
		self.interpretation_layer = InterpretationLayer()

		self.conn = rpyc.connect(self.SERVER_LOCATION, self.SERVER_PORT)
		bgsrv = rpyc.BgServingThread(self.conn) #https://rpyc.readthedocs.io/en/latest/api/utils_classic.html?highlight=BgServingThread#rpyc.utils.helpers.BgServingThread

		logged_in = False
		current_user = None

		try:
			logged_in, current_user = self.__login()
			self.__handle_command_input(current_user)

		except KeyboardInterrupt:
			print('Stopping client...')

			if(logged_in):
				self.conn.root.exposed_logout(current_user.to_json())

			bgsrv.stop()
			self.conn.close()
		except Exception as e:
			print('Client stopped abnormally: ', e)

			if(logged_in):
				self.conn.root.exposed_logout(current_user.to_json())

			bgsrv.stop()
			self.conn.close()