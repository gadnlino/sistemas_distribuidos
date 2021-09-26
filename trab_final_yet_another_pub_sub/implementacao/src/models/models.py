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

@dataclass_json
@dataclass
class Process:
	id: str
	ip_addr: str
	port: int

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
	subscriber: Process

	def __init__(self, topic_id, subscriber=None):
		self.topic_id = topic_id
		self.subscriber = subscriber

@dataclass_json
@dataclass
class Publication:
	topic_id: str
	publisher: Process
	message: Message

	def __init__(self, topic_id, message, publisher=None) -> None:
		self.topic_id = topic_id
		self.message = message
		self.publisher = publisher

@dataclass_json
@dataclass
class Topic:
	topic_id: str
	subscribers: List[Process]
	publications: List[Publication]
	publishers: List[Process]

	def __init__(self, topic_id, publishers=[], publications=[], subscribers=[]):
		self.topic_id = topic_id
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