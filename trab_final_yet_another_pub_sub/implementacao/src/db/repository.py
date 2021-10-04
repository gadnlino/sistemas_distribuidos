import sqlite3

from models.models import Subscription, Topic, User

class Repository:
	def __init__(self, db_location: str):
		self.db_location = db_location
	
	def get_user(self, user: User) -> User:
		result = None
		try:
			sql = "select user_id, user_name, logged_in from user where user_name = ? limit 1;"

			db_connection = sqlite3.connect(self.db_location)
			cursor = db_connection.cursor()
			
			cursor.execute(sql, (user.user_id,))
			result = cursor.fetchone()
			
			cursor.close()
			db_connection.close()

			if(result != None):
				r_user = User(result[1], logged_in=bool(result[2]))
				return r_user

			return None
		except Exception as e:
			raise e

	def insert_user(self, user: User):
		try:
			sql = "insert into user (user_name, logged_in) values(?,?);"

			db_connection = sqlite3.connect(self.db_location)
			cursor = db_connection.cursor()

			cursor.executemany(sql, [(user.user_id, user.logged_in)])
			db_connection.commit()

			cursor.close()
			db_connection.close()
		except Exception as e:
			raise e
	
	def update_user(self, user: User):
		try:
			sql = "update user set user_name = ?, logged_in = ? where user_name = ?;"
			
			db_connection = sqlite3.connect(self.db_location)
			cursor = db_connection.cursor()

			cursor.executemany(sql, [(user.user_id, user.logged_in, user.user_id)])
			db_connection.commit()

			cursor.close()
			db_connection.close()
		except Exception as e:
			raise e

	def get_topic(self, topic: Topic):
		sql = "select topic_name, enabled from topic where topic_name = ? limit 1;"

		db_connection = sqlite3.connect(self.db_location)
		cursor = db_connection.cursor()
		
		cursor.execute(sql, (topic.topic_id,))
		result = cursor.fetchone()
		
		cursor.close()
		db_connection.close()

		if(result != None):
			r_topic = Topic(result[0], enabled=bool(result[1]))
			return r_topic

		return None

	def get_topic_creator(self, topic: Topic):
		sql = "select u.user_name, u.logged_in \
				from user u join topic t on u.user_id = t.creator_id \
				where t.topic_name = ?;"

		db_connection = sqlite3.connect(self.db_location)
		cursor = db_connection.cursor()
		
		cursor.execute(sql, (topic.topic_id,))
		result = cursor.fetchone()
		
		cursor.close()
		db_connection.close()

		if(result != None):
			user = User(result[0], logged_in=bool(result[1]))
			return user

		return None

	def insert_topic(self, topic: Topic):
		try:
			sql = "insert into topic(topic_name, creator_id, enabled) values (\
				?,\
				(select user_id from user where user_name = ?),\
				?);"
			
			db_connection = sqlite3.connect(self.db_location)
			cursor = db_connection.cursor()

			cursor.executemany(sql, [(topic.topic_id, topic.creator.user_id, topic.enabled, )])
			db_connection.commit()

			cursor.close()
			db_connection.close()
		except Exception as e:
			raise e
	
	def get_all_enabled_topics(self)-> 'list[Topic]':
		topics = []

		try:
			sql = "select topic_name from topic where enabled = 1;"

			db_connection = sqlite3.connect(self.db_location)
			cursor = db_connection.cursor()

			cursor.execute(sql)

			result = cursor.fetchall()

			cursor.close()
			db_connection.close()

			for row in result:
				topics.append(Topic(row[0]))
			
			return topics
		except Exception as e:
			raise e
	
	def disable_topic(self, topic: Topic):
		try:
			sql = "update topic set\
					topic_name = ?,\
					old_topic_name = ?,\
					enabled = ?\
					where topic_name = ?;"

			db_connection = sqlite3.connect(self.db_location)
			cursor = db_connection.cursor()

			cursor.executemany(sql, [(topic.topic_id, topic.old_topic_name, topic.enabled, topic.old_topic_name)])
			db_connection.commit()

			cursor.close()
			db_connection.close()
		except Exception as e:
			raise e

	def insert_subscription(self, subscription: Subscription):
		try:
			sql = "insert into subscription(topic_id, subscriber_id)\
				 	values(\
					(select topic_id from topic where topic_name = ?),\
					(select user_id from user where user_name = ?));"

			db_connection = sqlite3.connect(self.db_location)
			cursor = db_connection.cursor()

			cursor.executemany(sql, [(subscription.topic_id, subscription.subscriber.user_id,)])
			db_connection.commit()

			cursor.close()
			db_connection.close()
		except Exception as e:
			raise e

	def delete_subscription(self, subscription: Subscription):
		try:
			sql = "delete from subscription\
					where topic_id = \
					(select topic_id from topic where topic_name = ?) \
					and subscriber_id = \
					(select user_id from user where user_name = ?);"
			
			db_connection = sqlite3.connect(self.db_location)
			cursor = db_connection.cursor()

			cursor.executemany(sql, [(subscription.topic_id, subscription.subscriber.user_id,)])
			db_connection.commit()

			cursor.close()
			db_connection.close()
		except Exception as e:
			raise e

	def create_publication(self, publication):
		pass

	def create_message(self, messsage):
		pass