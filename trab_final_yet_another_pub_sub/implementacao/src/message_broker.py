import rpyc
from rpyc.utils.server import ThreadedServer
from models.models import Publication, Subscription, Topic

class MessageBroker(rpyc.Service):
	def on_connect(self, conn):
		print(conn)

	def on_disconnect(self, conn):
		print(conn)

	def exposed_publish(self, publication: Publication):
		pass
	
	def exposed_subscribe(self, subscription: Subscription):
		pass
	
	def exposed_unsubscribe(self, subscription: Subscription):
		pass
	
	def exposed_create_topic(self, topic: Topic):
		pass
	
	def exposed_delete_topic(self, topic: Topic):
		pass

	def exposed_list_topics(self):
		pass

if __name__ == '__main__':
	pass