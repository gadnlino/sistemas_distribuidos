import rpyc
from models.models import Publication, Subscription, Topic, CommandType, User
from threading import Thread

class MessageBrokerService(rpyc.Service):
	conn = None
	__topics = []
	__users = []

	def __print_command(self, *args):
		command_print : str = '' + str(self.conn) + ': ' + ' '.join(args)
		print(command_print)

	def __publish_to_subscribers(self, subscribers: 'list[User]', publication: Publication):
		for i in range(0, len(subscribers)):
			subscriber = subscribers[i]
			publication_str = publication.to_json()
			subscriber.on_publication_callback(publication_str)

	def on_connect(self, conn):
		self.conn = conn

	def on_disconnect(self, conn):
		self.conn = None
	
	def exposed_login(self, user_json: str):
		user: User = User.from_json(user_json)

		self.__print_command(CommandType.LOGIN.name, user.user_id)

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

		self.__print_command(CommandType.LOGOUT.name, user.user_id)

		result = None
		error = None

		if(user not in self.__users):
			error = 'User is not logged in'
		else:
			self.__users.remove(user)

			for topic in self.__topics:
				if(user in topic.subscribers):
					topic.subscribers.remove(user)

			result = 'Logged out successfuly'
		
		return result, error

	def exposed_publish(self, publication_json: str):
		publication : Publication = Publication.from_json(publication_json)
		self.__print_command(CommandType.PUB.name, publication.topic_id, publication.message.body)

		result = None
		error = None

		topics: list[Topic] = \
				list(filter(lambda t: t.topic_id == publication.topic_id, self.__topics))
		
		if(len(topics) < 1):
			error = 'Topic does not exist'
		else:
			topic = topics[0]

			subscribers = [x for x in topic.subscribers if x != publication.publisher]

			if(len(subscribers) < 1):
				result = 'Topic does not have subscribers'
			else:
				
				t = Thread(target=lambda : 
					self.__publish_to_subscribers(subscribers, publication))
				t.start()
				
				result = 'Published successfully'

		return result, error
	
	def exposed_subscribe(self, subscription_json: str, on_publication_callback):
		subscription: Subscription = Subscription.from_json(subscription_json)
		self.__print_command(CommandType.SUB.name, subscription.topic_id)

		result = None
		error = None

		topics: list[Topic] = \
				list(filter(lambda t: t.topic_id == subscription.topic_id, self.__topics))

		if(len(topics) < 1):
			error = 'Topic does not exist'
		else:
			topic = topics[0]

			users : list[User] = \
				list(filter(lambda u: u.connection == self.conn, self.__users))

			if(len(users) < 1):
				error = 'User is not logged in'
			else:
				user = users[0]
				user.on_publication_callback = rpyc.async_(on_publication_callback)
				topic.subscribers.append(user)

				result = 'Subscription created successfully'

		return result, error
	
	def exposed_unsubscribe(self, subscription_json: str):
		subscription: Subscription = Subscription.from_json(subscription_json)
		self.__print_command(CommandType.UNSUB.name, subscription.topic_id)

		result = None
		error = None
		
		topics: list[Topic] = \
				list(filter(lambda t: t.topic_id == subscription.topic_id, self.__topics))

		if(len(topics) < 1):
			error = 'Topic does not exist'
		else:
			topic = topics[0]

			users : list[User] = \
				list(filter(lambda u: u.connection == self.conn, self.__users))

			if(len(users) < 1):
				error = 'User is not logged in'
			else:
				user = users[0]
				topic.subscribers.remove(user)

				result = 'Subscription deleted successfully'

		return result, error
	
	def exposed_create_topic(self, topic_json: str):		
		topic : Topic = Topic.from_json(topic_json)
		self.__print_command(CommandType.CREATE.name, topic.topic_id)

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
		self.__print_command(CommandType.DELETE.name, topic.topic_id)

		result = None
		error = None

		if(topic in self.__topics):
			self.__topics.remove(topic)
			result = 'Topic removed successfully'
		else:
			error = 'Topic does not exist'
		
		return result, error

	def exposed_list_topics(self):
		self.__print_command(CommandType.LIST.name)
		return list(map(lambda t: t.topic_id ,self.__topics)), None