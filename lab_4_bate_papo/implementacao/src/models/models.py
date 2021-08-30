from dataclasses import dataclass
from dataclasses_json import dataclass_json
from enum import Enum
from typing import Any
import time

class UserStatus(Enum):
    ONLINE=1
    INACTIVE=2
    OFFLINE=3

class CommandType(Enum):
    HELLO=1
    BYE=2
    PEERS=3
    MESSAGE = 4
    LIST=5
    QUIT = 6

@dataclass_json
@dataclass
class User:
    username: str

@dataclass_json
@dataclass
class Message:
    user : User
    message_body: str
    timestamp: float

    def __init__(self, user: User, message_body: str, timestamp: float = time.time()):
        self.message_body = message_body
        self.user = user
        self.timestamp = timestamp

@dataclass_json
@dataclass
class Command:
    type: str
    data: Any

@dataclass_json
@dataclass
class CommandResult:
    result: Any
    error: str