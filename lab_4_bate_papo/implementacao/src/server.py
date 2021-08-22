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
from models.models import Command, CommandResult, CommandType, User

class Server:
    def __init__(self, host, port) -> None:
        self.MAX_CONCURRENT_CONNECTIONS = 5
        self.HOST = host
        self.PORT = port

        self.interpretation_layer = InterpretationLayer()
        self.communication_layer = CommunicationLayer()

        self.client_threads = [] #armazena as threads criadas para fazer join
        self.avaiable_clients = {}
        self.commands = {} # lista de comandos disponíveis no servidor

        #registrando comandos do servidor, e suas respsctivas funções de callback
        # self.register_command(
        #     'list_connections()',
        #     'Lista as conexões ativas com esse servidor',
        #     lambda : print(str(self.active_connections.values())))
        self.register_command(
            CommandType.HELLO.name, 
            'Register a client avaiable to exchange messages',
            self.__start_message_exchange)

        self.register_command(
            CommandType.QUIT.name, 
            'Stop this application',
            self.__quit)
        # self.register_command(
        #     'list_files()',
        #     'Lista os arquivos disponiveis para busca no servidor', 
        #     lambda: print(self.file_fetcher.list_files_in_directory(self.FILES_DIRECTORY)))

    def run(self):
        '''Inicializa e implementa o loop principal (infinito) do servidor'''

        main_socket = self.__init_socket()

        print('Started listening at ' + str(self.HOST) + ':' + str(self.PORT))
        print()
        print()

        print("Avaiable commands:")

        for key, value in self.commands.items():
            print(key + ' : ' + value['description'])

        print()
        print()

        inputs = [sys.stdin, main_socket]

        while True:
            #espera por qualquer entrada de interesse
            rlist, _, _ = select.select(inputs, [], [])
            #tratar todas as entradas prontas
            for input_rlist in rlist:
                if input_rlist == main_socket:  #pedido novo de conexao
                    clisock, addr = self.__accept_incoming_connection(main_socket)
                    print ('New connection: ', addr)

                    command = self.communication_layer.receive_command(clisock)

                    if(command.type in self.commands):
                        worker_thread = threading.Thread(target=self.commands[command.type]['callback'], args=(command, clisock, addr))
                        worker_thread.start()

                    #cria nova thread para atender o cliente
                    # client_thread = threading.Thread(target=self.handle_incoming_connection, args=(clisock,addr))
                    # client_thread.start()
                    # self.client_threads.append(client_thread) #armazena a referencia da thread para usar com join()
                elif input_rlist == sys.stdin: #entrada padrao
                    cmd = input()

                    if cmd == CommandType.QUIT.name:
                        self.commands[cmd]['callback']()
                        print()
                    else:
                        print('Invalid command.')

    def __start_message_exchange(self, command: Command, socket, addr):
        print('Start message exchange')
        print(command)

        user : User = command.data
        self.avaiable_clients[addr] = user

        command_result = CommandResult(user.username +  ' loggeg in successfully', None)
        self.communication_layer.send_command_result(command_result, socket)

    def __stop_message_exchange(self, command: Command, socket, addr):
        print('Stop message exchange')
        print(command)

        command_result = self.communication_layer.send_command(command, socket)

    def __ask_for_peers(self, command: Command, socket, addr):
        print('Ask for peers')
        print(command)

        command_result = self.communication_layer.send_command(command, socket)

    def __send_message(self, command: Command, socket, addr):
        print('Sending message')
        print(command)

        command_result = self.communication_layer.send_command(command, socket)

    def __list_messages(self, command: Command, socket, addr):
        print('List received messages')
        print(command)

        command_result = self.communication_layer.send_command(command, socket)

    def __quit_client(self, command: Command, socket, addr):
        print('List received messages')
        print(command)

        command_result = self.communication_layer.send_command(command, socket)

    def __quit(self):
        for c in self.client_threads: #aguarda todas as threads terminarem
            c.join()
        self.main_socket.close()
        sys.exit()

    def register_command(self, command, description, callback):
        '''Registra um comando a ser executado via linha de comando'''
        if(command not in self.commands):
            self.commands[command] = {
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

    def __accept_incoming_connection(self, sock):
        '''Aceita o pedido de conexao de um cliente
        Entrada: o socket do servidor
        Saida: o novo socket da conexao e o endereco do cliente'''

        # estabelece conexao com o proximo cliente
        clisock, endr = sock.accept()

        return clisock, endr

    def handle_incoming_connection(self, clisock, addr):
        '''Recebe mensagens e as envia de volta para o cliente (ate o cliente finalizar)
        Entrada: socket da conexao e endereco do cliente
        Saida(exemplo): {"filename": "ola.txt", "term": "ola mundo", "occurrences": null, "error": "File does not exist."}'''

        while True:
            #recebe dados do cliente
            request_bytes = clisock.recv(self.MAX_BUFFER_SIZE) 

            if not request_bytes: # dados vazios: cliente encerrou
                print(str(addr) + '-> encerrou')
                clisock.close() # encerra a conexao com o cliente
                return

            request_str = str(request_bytes, encoding='utf-8')
            print(str(addr) + ': ' + request_str)

            request_json = json.loads(request_str)

            filename = request_json['filename']
            term = request_json['term']

            file_path = self.FILES_DIRECTORY + '/' + filename

            occurrences, error = self.file_parser.count_occurences_of_term(file_path, term)

            response_message = json.dumps({
                'filename':filename,
                'term':term,
                'occurrences':occurrences,
                'error':error
            })

            print(response_message)

            clisock.send(response_message.encode(encoding="utf-8")) # ecoa os dados para o cliente

server = Server('localhost', 10001)
server.run()