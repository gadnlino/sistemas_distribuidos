import socket
import json
import sys
import select
import threading
from communication_layer import CommunicationLayer
from interpretation_layer import InterpretationLayer
from models.models import Command, CommandType

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
        main_sock = self.__init_socket()

        inputs = [sys.stdin, main_sock]

        while(True):
            print("Avaiable commands:")

            for key, value in self.commands.items():
                print(key + ' : ' + value['description'])

            print()
            print()

            rlist, _, _ = select.select(inputs, [], [])

            for input_rlist in rlist:
                if(input_rlist == main_sock):
                    pass
                elif(input_rlist == sys.stdin):
                    command_str = input()
                    command, error = self.interpretation_layer.decode_command(command_str)
                    
                    if(error == None):
                        if(command.type in self.commands):
                            if(command.type != CommandType.QUIT.name):
                                worker_thread = threading.Thread(target=self.commands[command.type]['callback'], args=(command,main_sock))
                                worker_thread.start()
                            else:
                                self.commands[command.type]['callback'](command, main_sock)
                    else:
                        print('Error: ' + error)

    def __start_message_exchange(self, command: Command, socket):
        print('Start message exchange')
        print(command)

        command_result = self.communication_layer.send_command(command, socket)

    def __stop_message_exchange(self, command: Command, socket):
        print('Stop message exchange')
        print(command)

        self.communication_layer.send_command(command, socket)
        command_result = self.communication_layer.receive_command_result(command, socket)

    def __ask_for_peers(self, command: Command, socket):
        print('Ask for peers')
        print(command)

        command_result = self.communication_layer.send_command(command, socket)

    def __send_message(self, command: Command, socket):
        print('Sending message')
        print(command)

        command_result = self.communication_layer.send_command(command, socket)

    def __list_messages(self, command: Command, socket):
        print('List received messages')
        print(command)

        command_result = self.communication_layer.send_command(command, socket)
    
    def __quit(self, command: Command, socket):
        print('Quit')
        print(command)

        command_result = self.communication_layer.send_command(command, socket)
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

if(__name__ == '__main__'):
    client = Client('localhost', 10001)
    client.run()