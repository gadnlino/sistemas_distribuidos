import sqlite3

from models.models import Topic, User

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
				user = User(result[1], logged_in=bool(result[2]))
				return user

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

	def insert_topic(self, topic: Topic):
		pass
	
	def create_message(self, messsage):
		pass

	def create_publication(self, publication):
		pass

	def create_subscription(self, subscription):
		pass

	def delete_subscription(self, subscription):
		pass