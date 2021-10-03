from dataclasses import dataclass
from dataclasses_json import dataclass_json
from enum import Enum
from typing import List, Any
import time

class CommandType(Enum):
	PUB=1
	SUB=2
	UNSUB=3
	CREATE = 4
	DELETE=5
	LIST = 6
	LOGIN = 7
	LOGOUT = 8

@dataclass_json
@dataclass
class User:
	user_id: str
	logged_in: bool
	connection: Any
	on_publication_callback: Any

	def __init__(self, user_id, logged_in=False, connection = None, on_publication_callback = None):
		self.user_id = user_id
		self.logged_in = logged_in
		self.connection = connection
		self.on_publication_callback = on_publication_callback
	
	def __eq__(self, o: object) -> bool:
		if(isinstance(o, User)):
			return o.user_id == self.user_id
		
		return False

@dataclass_json
@dataclass
class Message:
	body: str
	timestamp: float

	def __init__(self, body, timestamp = time.time()):
		self.body = body
		self.timestamp = timestamp

@dataclass_json
@dataclass
class Subscription:
	topic_id: str
	subscriber: User

	def __init__(self, topic_id, subscriber=None):
		self.topic_id = topic_id
		self.subscriber = subscriber

@dataclass_json
@dataclass
class Publication:
	topic_id: str
	publisher: User
	message: Message

	def __init__(self, topic_id, message, publisher=None) -> None:
		self.topic_id = topic_id
		self.message = message
		self.publisher = publisher

@dataclass_json
@dataclass
class Topic:
	topic_id: str
	creator: User
	subscribers: List[User]
	publications: List[Publication]
	publishers: List[User]

	def __init__(self, topic_id, creator =  None, publishers=[], publications=[], subscribers=[]):
		self.topic_id = topic_id
		self.creator = creator
		self.subscribers = subscribers
		self.publications = publications
		self.publishers = publishers
	
	def __eq__(self, o: object) -> bool:
		if isinstance(o, Topic):
			return o.topic_id == self.topic_id
		
		return False

@dataclass_json
@dataclass
class Command:
    type: str
    data: Any