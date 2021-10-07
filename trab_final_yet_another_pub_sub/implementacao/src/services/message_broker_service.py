import rpyc
import uuid
from db.repository import Repository
from models.models import Publication, Subscription, Topic, CommandType, User
from threading import Thread
import time


class MessageBrokerService(rpyc.Service):
    conn = None
    __topics = []
    __logged_users = []
    _DB_LOCATION = 'C:\sqlite\dbs\pubsub.db'
    __repository = Repository(_DB_LOCATION)

    def __print_command(self, *args):
        command_print: str = '' + str(self.conn) + ': ' + ' '.join(args)
        print(command_print)

    def __publish_to_subscribers(self, subscribers: 'list[User]', publication: Publication):
        for i in range(0, len(subscribers)):
            subscriber = subscribers[i]
            publication_str = publication.to_json()
            subscriber.on_publication_callback(publication_str)

            delivery_timestamp = time.time()

            self.__repository.update_message_delivery_timestamp(
                publication.message.message_hash, subscriber, delivery_timestamp)

    def __get_current_user(self) -> User:
        users = list(filter(lambda x: x.connection ==
                            self.conn, self.__logged_users))

        if(len(users) > 0):
            return self.__logged_users[0]

        return None

    def on_connect(self, conn):
        self.conn = conn

    def on_disconnect(self, conn):
        self.conn = None

    def exposed_login(self, user_json: str, on_publication_callback):
        try:
            user: User = User.from_json(user_json)

            self.__print_command(CommandType.LOGIN.name, user.user_id)

            result = None
            error = None

            existant_user = self.__repository.get_user(user)

            if(existant_user == None):
                user.connection = self.conn
                user.logged_in = True
                user.on_publication_callback = rpyc.async_(
                    on_publication_callback)
                self.__repository.insert_user(user)
                self.__logged_users.append(user)
                result = 'Logged in successfuly'
            else:
                existant_user.logged_in = True
                existant_user.connection = self.conn
                existant_user.on_publication_callback = rpyc.async_(
                    on_publication_callback)
                if(existant_user in self.__logged_users):
                    self.__logged_users.remove(existant_user)
                self.__logged_users.append(existant_user)
                self.__repository.update_user(existant_user)
                result = 'Logged in successfuly'

            return result, error
        except Exception as e:
            print(e)

    def exposed_logout(self, user_json: str):
        try:
            user: User = User.from_json(user_json)

            self.__print_command(CommandType.LOGOUT.name, user.user_id)

            result = None
            error = None

            if(user not in self.__logged_users):
                error = 'User is not logged in'
            else:
                user.logged_in = False
                self.__logged_users.remove(user)
                self.__repository.update_user(user)

                result = 'Logged out successfuly'

            return result, error
        except Exception as e:
            print(e)

    def exposed_publish(self, publication_json: str):
        try:
            publication: Publication = Publication.from_json(publication_json)
            self.__print_command(CommandType.PUB.name,
                                 publication.topic_id, publication.message.body)

            result = None
            error = None

            topic = self.__repository.get_topic(Topic(publication.topic_id))

            if(topic == None):
                error = 'Topic does not exist'
            else:
                subscribers = self.__repository.get_topic_subscribers(topic)

                logged_subscribers = list(map(lambda y: list(filter(lambda w: y == w, self.__logged_users))[0], filter(
                    lambda x: x in self.__logged_users, subscribers)))

                self.__repository.create_publication(publication)

                for recipient in subscribers:
                    self.__repository.create_message_delivery(
                        publication.message.message_hash, recipient)

                t = Thread(target=lambda: self.__publish_to_subscribers(
                    logged_subscribers, publication))
                t.start()

                result = 'Published successfully'

            # topics: list[Topic] = \
            # 		list(filter(lambda t: t.topic_id == publication.topic_id, self.__topics))

            # if(len(topics) < 1):
            # 	error = 'Topic does not exist'
            # else:
            # 	topic = topics[0]

            # 	subscribers = [x for x in topic.subscribers if x != publication.publisher]

            # 	if(len(subscribers) < 1):
            # 		result = 'Topic does not have subscribers'
            # 	else:

            # 		t = Thread(target=lambda :
            # 			self.__publish_to_subscribers(subscribers, publication))
            # 		t.start()

            # 		result = 'Published successfully'

            return result, error
        except Exception as e:
            print(e)

    def exposed_subscribe(self, subscription_json: str):
        try:
            subscription: Subscription = Subscription.from_json(
                subscription_json)
            self.__print_command(CommandType.SUB.name, subscription.topic_id)

            result = None
            error = None

            existant_topic = self.__repository.get_topic(
                Topic(subscription.topic_id))

            if(existant_topic == None):
                error = 'Topic does not exist'
            else:
                current_user = list(
                    filter(lambda x: x == subscription.subscriber, self.__logged_users))[0]

                subscription.subscriber = current_user
                subscription.topic_id = existant_topic.topic_id

                if (not self.__repository.subscription_exists(subscription)):
                    self.__repository.insert_subscription(subscription)

                    result = 'Subscription created successfully'
                else:
                    error = 'Susbscription already exists'

            return result, error
        except Exception as e:
            print(e)

    def exposed_unsubscribe(self, subscription_json: str):
        try:
            subscription: Subscription = Subscription.from_json(
                subscription_json)
            self.__print_command(CommandType.UNSUB.name, subscription.topic_id)

            result = None
            error = None

            existant_topic = self.__repository.get_topic(
                Topic(subscription.topic_id))

            if(existant_topic == None):
                error = 'Topic does not exist'
            else:
                current_user = self.__get_current_user()

                subscription.subscriber = current_user
                subscription.topic_id = existant_topic.topic_id

                self.__repository.delete_subscription(subscription)

                result = 'Subscription deleted successfully'

            return result, error
        except Exception as e:
            print(e)

    def exposed_create_topic(self, topic_json: str):
        try:
            topic: Topic = Topic.from_json(topic_json)
            self.__print_command(CommandType.CREATE.name, topic.topic_id)

            result = None
            error = None

            existant_topic = self.__repository.get_topic(topic)

            if(existant_topic == None):
                topic_creator = self.__get_current_user()
                topic.creator = topic_creator
                self.__repository.insert_topic(topic)
                result = 'Topic added successfully'
            else:
                error = 'Topic has already been created'

            return result, error
        except Exception as e:
            print(e)

    def exposed_delete_topic(self, topic_json: str):
        try:
            topic: Topic = Topic.from_json(topic_json)
            self.__print_command(CommandType.DELETE.name, topic.topic_id)

            result = None
            error = None

            existant_topic = self.__repository.get_topic(topic)

            if(topic != None):
                topic_creator = self.__repository.get_topic_creator(topic)
                current_user = self.__get_current_user()

                if(topic_creator != current_user):
                    error = 'User is not authorized to delete topic'
                else:
                    existant_topic.old_topic_name = existant_topic.topic_id
                    existant_topic.topic_id = str(uuid.uuid1())
                    existant_topic.enabled = False
                    self.__repository.disable_topic(existant_topic)
                    result = 'Topic removed successfully'
            else:
                error = 'Topic does not exist'

            return result, error
        except Exception as e:
            print(e)

    def exposed_list_topics(self):
        try:
            self.__print_command(CommandType.LIST.name)
            enabled_topics = self.__repository.get_all_enabled_topics()

            return list(map(lambda x: x.to_json(), enabled_topics)), None
        except Exception as e:
            print(e)
