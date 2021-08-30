#servidor de echo: lado servidor
#com finalizacao do lado do servidor
#com multithreading (usa join para esperar as threads terminarem apos digitar 'fim' no servidor)
import socket
import select
import sys
import threading
import json
from interpretation_layer import InterpretationLayer
from communication_layer import CommunicationLayer
from models.models import Command, CommandResult, CommandType, Message, User, UserStatus

class Server:
    def __init__(self, host, port) -> None:
        self.MAX_CONCURRENT_CONNECTIONS = 5
        self.HOST = host
        self.PORT = port

        self.interpretation_layer = InterpretationLayer()
        self.communication_layer = CommunicationLayer()

        self.main_socket = None
        self.inputs = None

        self.active_addreses = []   

        self.client_threads = [] #armazena as threads criadas para fazer join
        self.users = {}

        self.client_commands = {} # lista de comandos disponíveis para os clientes
        self.server_commands = {} # lista de comandos disponíveis para o servidor

        self.__register_client_command(
            CommandType.HELLO.name, 
            'Register a client avaiable to exchange messages',
            self.__start_message_exchange)

        self.__register_client_command(
            CommandType.BYE.name, 
            'Unregister a client from the avaiable clients to exchange messages',
            self.__stop_message_exchange)

        self.__register_client_command(
            CommandType.QUIT.name, 
            'Unregister a client from the active clients',
            self.__quit_client)

        self.__register_client_command(
            CommandType.LIST.name, 
            'List user messages',
            self.__list_messages)

        self.__register_client_command(
            CommandType.PEERS.name, 
            'List active users',
            self.__ask_for_peers)
        
        self.__register_client_command(
            CommandType.MESSAGE.name, 
            'Send message to a user',
            self.__send_message)




        self.__register_server_command(
            CommandType.QUIT.name, 
            'Stop this application',
            self.__quit_server)

    def run(self):
        '''Inicializa e implementa o loop principal (infinito) do servidor'''

        print('Started listening at ' + str(self.HOST) + ':' + str(self.PORT))
        print()
        print()

        print("Avaiable client commands:")

        for key, value in self.client_commands.items():
            print(key + ' : ' + value['description'])

        print()
        print()

        print("Avaiable server commands:")

        for key, value in self.server_commands.items():
            print(key + ' : ' + value['description'])

        print()
        print()

        self.main_socket = self.__init_socket()
        self.inputs = [sys.stdin, self.main_socket]

        while True:
            #espera por qualquer entrada de interesse
            rlist, _, _ = select.select(self.inputs, [], [])
            #tratar todas as entradas prontas
            for input_rlist in rlist:
                if input_rlist == self.main_socket:  #pedido novo de conexao

                    client_socket, client_address = self.main_socket.accept()

                    client_thread = threading.Thread(
                        target=self.__handle_client_connection, 
                        args=(client_socket, client_address))
                    client_thread.start()

                    self.client_threads.append(client_thread)
                elif input_rlist == sys.stdin: #entrada padrao
                    cmd_str = input()

                    decoded_command, error = self.interpretation_layer.decode_command(cmd_str)

                    if(error != None):
                        print('Invalid command.')
                    elif decoded_command.type in self.server_commands:
                        self.server_commands[decoded_command.type]['callback']()
                        print()
                    else:
                        print('Invalid command.')

    def __start_message_exchange(self, command: Command, client_socket, addr):
        self.active_addreses.append(addr)
        
        user: User = User.from_json(json.dumps(command.data))

        if not user.username in self.users:
            self.users[user.username] = {
                'user': user,
                'status': UserStatus.ONLINE.name,
                'address': addr,
                'socket': client_socket,
                'messages_sent' : [],
                'messages_received' : []
            }
        else:
            self.users[user.username]['status'] = UserStatus.ONLINE.name
            self.users[user.username]['address'] = addr

        command_result = CommandResult(user.username +  ' logged in successfully', None)
        self.communication_layer.send_command_result(command_result, client_socket)

    def __stop_message_exchange(self, command: Command, socket, addr):
        command_result = None

        if(addr in self.active_addreses):
            for (username, user_info) in self.users.items():
                if user_info['address'] == addr:
                    user : User = user_info['user']

                    user_info['status'] = UserStatus.INACTIVE.name

                    command_result = CommandResult(user.username +  
                        ' stopped exchanging messages successfully', None)
                    
                    break
        else:
            command_result = CommandResult(None, 'user is not logged in')
        
        self.communication_layer.send_command_result(command_result, socket)

    def __ask_for_peers(self, command: Command, socket, addr):
        command_result = None

        if(addr in self.active_addreses):
            current_user: User = None
            other_users : list[User] = []

            for (username, user_info) in self.users.items():
                if user_info['address'] == addr:
                    current_user = user_info['user']
                    break
            
            for (username, user_info) in self.users.items():
                if user_info['user'].username != current_user.username:
                    other_users.append(user_info['user'])
            
            command_result = CommandResult(other_users, None)
        else:
            command_result = CommandResult(None, 'user is not logged in')

        self.communication_layer.send_command_result(command_result, socket)

    def __send_message(self, command: Command, socket, addr):
        command_result = None

        if(addr in self.active_addreses):
            for (username, user_info) in self.users.items():
                if user_info['address'] == addr:
                    current_user: User = user_info['user']
                    message : Message = Message.from_json(json.dumps(command.data))

                    if(message.user.username in self.users and 
                        self.users[message.user.username]['status'] == UserStatus.ONLINE.name):
                        recipient_info = self.users[message.user.username]
                        recipient_socket = recipient_info['socket']
                        recipient_message = Message(
                            user=current_user, 
                            message_body=message.message_body, 
                            timestamp=  message.timestamp)

                        recipient_command = Command(type=CommandType.MESSAGE.name, data=recipient_message)
                        self.communication_layer.send_command(recipient_command, recipient_socket)

                        user_info['messages_sent'].append(message)
                        recipient_info['messages_received'].append(recipient_message)

                        command_result = CommandResult('Message sent successfully', None)
                    else:
                        command_result = CommandResult(None, str()+ ' is not logged in')

                    break
        else:
            command_result = CommandResult(None, 'user is not logged in')

        self.communication_layer.send_command_result(command_result, socket)

    def __list_messages(self, command: Command, socket, addr):
        print('List received messages')
        print(command)

        command_result = None

        if addr in self.active_addreses:
            for (username, user_info) in self.users.items():
                if user_info['address'] == addr:
                    messages_received: list[Message] = user_info['messages_received']

                    messages_received.sort(key=lambda x : x.timestamp)

                    command_result= CommandResult(messages_received, None)

                    break
        else:
            command_result = CommandResult(None, 'user is not logged in')

        self.communication_layer.send_command_result(command_result, socket)

    def __quit_client(self, command: Command, socket, addr):
        command_result = None

        if addr in self.active_addreses:
            for (username, user_info) in self.users.items():
                if 'address' in user_info and user_info['address'] == addr:
                    user : User = user_info['user']

                    user_info['status'] = UserStatus.OFFLINE.name

                    if 'address' in user_info:
                        del user_info['address']
                    if 'socket' in user_info:
                        del user_info['socket']

                    self.active_addreses.remove(addr)

                    command_result = CommandResult('ok', None)

                    break
        else:
            command_result= CommandResult(None, 'user is not logged in')
        
        self.communication_layer.send_command_result(command_result, socket)

    def __quit_server(self):
        print('Quitting server...')
        for c in self.client_threads: #aguarda todas as threads terminarem
            c.join()
        self.main_socket.close()
        sys.exit(0)

    def __register_client_command(self, command, description, callback):
        '''Registra um comando a ser executado via linha de comando'''
        if(command not in self.client_commands):
            self.client_commands[command] = {
                'command':command,
                'description': description,
                'callback': callback
            }
    
    def __register_server_command(self, command, description, callback):
        '''Registra um comando a ser executado via linha de comando'''
        if(command not in self.server_commands):
            self.server_commands[command] = {
                'command':command,
                'description': description,
                'callback': callback
            }
    
    def __init_socket(self):
        '''Cria um socket de servidor e o coloca em modo de espera por conexoes
        Saida: o socket criado'''
        # cria o socket 
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #Internet( IPv4 + TCP) 

        # vincula a localizacao do servidor
        sock.bind((self.HOST, self.PORT))

        # coloca-se em modo de espera por conexoes
        sock.listen(self.MAX_CONCURRENT_CONNECTIONS) 

        # configura o socket para o modo nao-bloqueante
        sock.setblocking(False)

        return sock

    def __handle_client_connection(self, client_socket, client_address):

        while True:
            command = self.communication_layer.receive_command(client_socket)

            if(command == None):
                client_socket.close()
                
                if(client_address in self.active_addreses):
                    self.active_addreses.remove(client_address)
                
                return
            elif(command.type in self.client_commands):
                self.client_commands[command.type]['callback'](
                    command, client_socket, client_address)
            else:
                self.communication_layer.send_command_result(
                    CommandResult(None, 'Invalid command'),
                    client_socket)

server = Server('localhost', 10001)
server.run()