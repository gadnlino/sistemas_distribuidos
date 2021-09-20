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

	def __init__(self, body):
		self.body = body
		self.timestamp = time.time()

@dataclass_json
@dataclass
class Subscription:
	topic_id: str
	subscriber: Process

	def __init__(self, topic_id):
		self.topic_id = topic_id
		self.subscriber = None

@dataclass_json
@dataclass
class Publication:
	topic_id: str
	publisher: Process
	message: Message

	def __init__(self, topic_id, message) -> None:
		self.topic_id = topic_id
		self.message = message
		self.publisher = None

@dataclass_json
@dataclass
class Topic:
	topic_id: str
	subscribers: List[Process]
	publications: List[Publication]
	publishers: List[Process]

	def __init__(self, topic_id):
		self.topic_id = topic_id
		self.subscribers = []
		self.publications = []
		self.publishers = []

@dataclass_json
@dataclass
class Command:
    type: str
    data: Any