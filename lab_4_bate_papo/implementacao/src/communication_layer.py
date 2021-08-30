import json
from models.models import Command, CommandResult, CommandType, User
from helpers.json_encoder import EnhancedJSONEncoder
import socket

class CommunicationLayer:
    def __init__(self):
        self.HEADER_MESSAGE_SIZE_BYTES_LEN = 64
        self.DEFAULT_ENCODING = 'utf-8'

    def send_command(self, command: Command, sock: socket):
        command_json = json.dumps(command, cls=EnhancedJSONEncoder)
        command_encoded = command_json.encode(encoding=self.DEFAULT_ENCODING)
        command_len_str = str(len(command_encoded))
        leading_zeroes = command_len_str.zfill(self.HEADER_MESSAGE_SIZE_BYTES_LEN)
        
        #Base 10 string representation of message size
        message_size_encoded = leading_zeroes.encode(encoding=self.DEFAULT_ENCODING)

        sock.send(message_size_encoded + command_encoded)
    
    def receive_command(self, sock: socket)-> Command:
        command_size_encoded = sock.recv(self.HEADER_MESSAGE_SIZE_BYTES_LEN)

        if(not command_size_encoded):
            return None
        
        command_size_str = str(command_size_encoded, encoding=self.DEFAULT_ENCODING).lstrip('0')
        
        #Converting base 10 representation of message size to integer
        command_size = int(command_size_str)
        
        command_encoded = sock.recv(command_size)

        command_encoded_str = str(command_encoded, encoding=self.DEFAULT_ENCODING)

        command = Command.from_json(command_encoded_str)
        
        return command
    
    def send_command_result(self, command_result: CommandResult, sock: socket):
        command_result_json = command_result.to_json()
        command_result_encoded = command_result_json.encode(encoding=self.DEFAULT_ENCODING)
        command_result_len_str = str(len(command_result_encoded))
        leading_zeroes = command_result_len_str.zfill(self.HEADER_MESSAGE_SIZE_BYTES_LEN)
        
        #Base 10 string representation of message size
        command_result_size_encoded = leading_zeroes.encode(encoding=self.DEFAULT_ENCODING)

        sock.send(command_result_size_encoded + command_result_encoded)
    
    def receive_command_result(self, sock: socket)-> CommandResult:
        result_size_encoded = sock.recv(self.HEADER_MESSAGE_SIZE_BYTES_LEN)
        result_size_str = str(result_size_encoded, encoding=self.DEFAULT_ENCODING).lstrip('0')
        
        #Converting base 10 representation of message size to integer
        message_size = int(result_size_str)
        
        command_result_encoded = sock.recv(message_size)

        command_result_encoded_str = str(command_result_encoded, encoding=self.DEFAULT_ENCODING)

        command_result = CommandResult.from_json(command_result_encoded_str)

        return command_result

if __name__ == '__main__':
    HOST = 'localhost' # maquina onde esta o par passivo
    PORT = 10001
    sock = socket.socket() 
    sock.connect((HOST, PORT)) 

    c = CommunicationLayer()
    c.send_command(Command(CommandType.HELLO.name, User('gadnlino')), sock)
    c.receive_command_result(sock)

    sock.close()