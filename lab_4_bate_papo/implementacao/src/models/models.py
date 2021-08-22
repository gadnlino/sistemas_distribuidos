from dataclasses import dataclass
from dataclasses_json import dataclass_json
from enum import Enum
from typing import Any
import time

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
    timestamp: int = time.time()

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