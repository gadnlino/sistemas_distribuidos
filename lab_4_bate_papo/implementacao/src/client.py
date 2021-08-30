import socket
import json
import sys
import select
from datetime import datetime
from communication_layer import CommunicationLayer
from interpretation_layer import InterpretationLayer
from models.models import Command, CommandType, Message, User

class Client:
    def __init__(self, server_ip: str, server_port: int):
        self.SERVER_IP = server_ip
        self.SERVER_PORT = server_port
        self.interpretation_layer = InterpretationLayer()
        self.communication_layer = CommunicationLayer()
        self.commands = {}

        self._register_command(
            CommandType.HELLO.name, 
            'Tells the server that this client is avaiable to exchange messages',
             self.__start_message_exchange)

        self._register_command(
            CommandType.BYE.name, 
            'Tells the server that this client has stopped exchanging messages',
             self.__stop_message_exchange)

        self._register_command(
            CommandType.PEERS.name, 
            'Asks the server for avaiable peers for message exchange',
             self.__ask_for_peers)

        self._register_command(
            CommandType.MESSAGE.name, 
            'Send a message',
             self.__send_message)
        
        self._register_command(
            CommandType.LIST.name, 
            'List received messages',
             self.__list_messages)

        self._register_command(
            CommandType.QUIT.name, 
            'Stop this application',
             self.__quit)

    def run(self):
        print("Avaiable commands:")

        for key, value in self.commands.items():
            print(key + ' : ' + value['description'])

        print()
        print()

        main_sock = self.__init_socket()

        inputs = [sys.stdin, main_sock]

        while(True):
            rlist, _, _ = select.select(inputs, [], [])

            for input_rlist in rlist:
                if(input_rlist == main_sock):
                    command = self.communication_layer.receive_command(main_sock)

                    if(command.type == CommandType.MESSAGE.name):
                        message: Message = Message.from_json(json.dumps(command.data))
                        print(self.__get_beautified_message_str(message))
                        
                        for _ in range(0,5):
                            print()

                elif(input_rlist == sys.stdin):
                    command_str = input()
                    command, error = self.interpretation_layer.decode_command(command_str)
                    
                    if(error == None):
                        if(command.type in self.commands):
                            self.commands[command.type]['callback'](command, main_sock)

                            for _ in range(0,5):
                                print()
                            
                            print('-------------------------------------------------------------')
                        else:
                            print('Invalid command')
                    else:
                        print('Error: ' + error)

    def __start_message_exchange(self, command: Command, socket):
        self.communication_layer.send_command(command, socket)
        command_result = self.communication_layer.receive_command_result(socket)

        if(command_result.error != None):
            print('Error: ' + command_result.error)
        else:
            print(command_result.result)

    def __stop_message_exchange(self, command: Command, socket):
        self.communication_layer.send_command(command, socket)
        command_result = self.communication_layer.receive_command_result(socket)
        
        if(command_result.error != None):
            print('Error: ' + command_result.error)
        else:
            print(command_result.result)

    def __ask_for_peers(self, command: Command, socket):
        self.communication_layer.send_command(command, socket)

        command_result = self.communication_layer.receive_command_result(socket)

        if(command_result.error == None):
            peers : list[User] = command_result.result

            if(len(peers) > 0):
                for i in range(0, len(peers)):
                    user : User = User.from_json(json.dumps(peers[i]))
                    print('User: ' + user.username)
            else:
                print('No other peers found')
        else:
            print('Error: ' + str(command_result.error))

    def __send_message(self, command: Command, socket):
        print('Sending message')
        print(command)

        self.communication_layer.send_command(command, socket)
        command_result = self.communication_layer.receive_command_result(socket)

        if(command_result.error == None):
            print(str(command_result.result))
        else:
            print('Error: ' + str(command_result.error))

    def __list_messages(self, command: Command, socket):
        self.communication_layer.send_command(command, socket)

        command_result = self.communication_layer.receive_command_result(socket)

        print(command_result)

        if(command_result.error == None):
            messages_received : list[Message] = command_result.result

            if(len(messages_received) > 0):
                for message in messages_received:
                    print(self.__get_beautified_message_str(Message.from_json(json.dumps(message))))
            else:
                print('No messages received')
        else:
            print('Error: ' + str(command_result.error))
    
    def __quit(self, command: Command, socket):
        print('Quit')
        print(command)

        self.communication_layer.send_command(command, socket)
        #command_result = self.communication_layer.receive_command_result(socket)

        socket.close()
        
        sys.exit(0)

    def _register_command(self, command, description, callback):
        '''Register a command to be executed via command line'''
        if(command not in self.commands):
            self.commands[command] = {
                'command':command,
                'description': description,
                'callback': callback
            }       

    def __init_socket(self):
        sock = socket.socket() 
        sock.connect((self.SERVER_IP, self.SERVER_PORT))
        return sock

    def __get_beautified_message_str(self, message: Message):
        beutified_str = 'MESSAGE(user: ' + str(message.user.username) + ', time: ' + str(datetime.utcfromtimestamp(message.timestamp).strftime('%d/%m/%Y %H:%M:%S')) + ') ' + str(message.message_body)
        return beutified_str

if(__name__ == '__main__'):
    client = Client('localhost', 10001)
    client.run()