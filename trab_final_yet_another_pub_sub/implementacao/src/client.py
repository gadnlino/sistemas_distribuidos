from models.models import CommandType, Publication, Subscription, Topic, User
from interpretation_layer import InterpretationLayer
import rpyc

SERVER_IP = 'localhost'
PORT = 65535

def main():
	interpretation_layer = InterpretationLayer()
	conn = rpyc.connect(SERVER_IP, PORT)

	logged_in = False

	try:
		while(True):
			user_id = input('Please type your user id: ')
			current_user = User(user_id)

			login_result, login_error = conn.root.exposed_login(current_user.to_json())

			if(login_error != None):
				print('Error while logging in: ', login_error)
			else:
				print(login_result)
				logged_in = True
				break

		while True:
			command_str = input('Please type a command: ')
			command, command_error = interpretation_layer.decode_command(command_str)

			if(command_error == None):
				result = None
				error = None

				if(command.type == CommandType.PUB.name):
					publication: Publication = command.data
					publication.publisher = current_user
					result, error = conn.root.exposed_publish(publication.to_json())
				elif(command.type == CommandType.SUB.name):
					subscription: Subscription = command.data
					subscription.subscriber = current_user
					result, error = conn.root.exposed_subscribe(subscription.to_json())
				elif(command.type == CommandType.UNSUB.name):
					subscription: Subscription = command.data
					subscription.subscriber = current_user
					result, error = conn.root.exposed_unsubscribe(subscription.to_json())
				elif(command.type == CommandType.CREATE.name):
					topic: Topic = command.data
					result, error = conn.root.exposed_create_topic(topic.to_json())
				elif(command.type == CommandType.DELETE.name):
					topic: Topic = command.data
					result, error = conn.root.exposed_delete_topic(topic.to_json())
				elif(command.type == CommandType.LIST.name):
					result, error = conn.root.exposed_list_topics()

				if(error != None):
					print('Error executing command: ', error)
				else:
					print(result)
			else:
				print('Error with command ', command_error)

	except KeyboardInterrupt:
		print('Stopping client...')

		if(logged_in):
			conn.root.exposed_logout(current_user.to_json())

		conn.close()
	except Exception as e:
		print('Client stopped abnormally: ', e)

		if(logged_in):
			conn.root.exposed_logout(current_user.to_json())

		conn.close()

# executa o cliente
if __name__ == "__main__":
	main()