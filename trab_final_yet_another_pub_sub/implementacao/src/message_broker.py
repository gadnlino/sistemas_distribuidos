import rpyc
from rpyc.utils.server import ThreadedServer
from models.models import Publication, Subscription, Topic, CommandType, User

PORT = 65535

class MessageBroker(rpyc.Service):
	conn = None
	__topics = []
	__users = []

	def on_connect(self, conn):
		self.conn = conn		

	def on_disconnect(self, conn):
		self.conn = None

	def exposed_login(self, user_json: str):
		user: User = User.from_json(user_json)

		self.print_command('LOGIN', user.user_id)

		result = None
		error = None

		if(user in self.__users):
			error = 'User is already logged in'
		else:
			user.connection = self.conn
			self.__users.append(user)
			result = 'Logged in successfuly'
		
		return result, error
	
	def exposed_logout(self, user_json: str):
		user: User = User.from_json(user_json)

		self.print_command('LOGOUT', user.user_id)

		result = None
		error = None

		if(user not in self.__users):
			error = 'User is not logged in'
		else:
			self.__users.remove(user)
			result = 'Logged out successfuly'
		
		return result, error

	def print_command(self, *args):
		command_print : str = '' + str(self.conn) + ': ' + ' '.join(args)
		print(command_print)

	def exposed_publish(self, publication_json: str):
		pass
	
	def exposed_subscribe(self, subscription_json: str):
		subscription: Subscription = Subscription.from_json(subscription_json)
		print(CommandType.SUB.name, ' ', subscription.topic_id)

		result = None
		error = None

		topics: list[Topic] = \
				list(filter(lambda t: t.topic_id == subscription.topic_id, self.__topics))

		if(len(topics) < 1):
			error = 'Topic does not exist'
		else:
			topic = topics[0]
			topic.subscribers.append()

		return result, error
	
	def exposed_unsubscribe(self, subscription_json: str):
		pass
	
	def exposed_create_topic(self, topic_json: str):		
		topic : Topic = Topic.from_json(topic_json)
		self.print_command(CommandType.CREATE.name, topic.topic_id)

		result = None
		error = None

		if(topic not in self.__topics):
			self.__topics.append(topic)
			result = 'Topic added successfully'
		else:
			error = 'Topic has already been created'
		
		return result, error
	
	def exposed_delete_topic(self, topic_json: str):
		topic : Topic = Topic.from_json(topic_json)
		self.print_command(CommandType.DELETE.name, topic.topic_id)

		result = None
		error = None

		if(topic in self.__topics):
			self.__topics.remove(topic)
			result = 'Topic removed successfully'
		else:
			error = 'Topic does not exist'
		
		return result, error

	def exposed_list_topics(self):
		self.print_command(CommandType.LIST.name)
		return list(map(lambda t: t.topic_id ,self.__topics)), None

if __name__ == '__main__':
	broker_svc = ThreadedServer(MessageBroker, port=PORT)

	try:
		print('Starting server')
		broker_svc.start()
	except KeyboardInterrupt:
		print('Stopping server...')
		broker_svc.close()
	except Exception as e:
		print('Server stopped abnormally: ', e)
		broker_svc.close()