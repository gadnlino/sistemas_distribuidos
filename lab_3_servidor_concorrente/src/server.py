#servidor de echo: lado servidor
#com finalizacao do lado do servidor
#com multithreading (usa join para esperar as threads terminarem apos digitar 'fim' no servidor)
import socket
import select
import sys
import threading
import json
from file_utilities.file_utilities import FileParser, FileFetcher

class Server:
    def __init__(self, host, port) -> None:
        self.FILES_DIRECTORY = './src/files' # pasta contendo os arquivos para busca
        self.MAX_CONCURRENT_CONNECTIONS = 5
        self.MAX_BUFFER_SIZE = 1024000

        self.HOST = host
        self.PORT = port
        self.rlist = [sys.stdin]
        self.client_threads = [] #armazena as threads criadas para fazer join
        self.active_connections = {}
        self.commands = {} # lista de comandos disponíveis no servidor

        self.file_parser = FileParser()
        self.file_fetcher = FileFetcher()

        #registrando comandos do servidor, e suas respsctivas funções de callback
        self.register_command(
            'list_connections()',
            'Lista as conexões ativas com esse servidor',
            lambda : print(str(self.active_connections.values())))
        self.register_command('quit()','Encerra a execução do servidor', quit)
        self.register_command(
            'list_files()',
            'Lista os arquivos disponiveis para busca no servidor', 
            lambda: print(self.file_fetcher.list_files_in_directory(self.FILES_DIRECTORY)))

    def run(self):
        '''Inicializa e implementa o loop principal (infinito) do servidor'''

        self.init_main_socket()

        print('Started listening at ' + str(self.HOST) + ':' + str(self.PORT))
        print()
        print()

        print("Avaiable commands:")

        for key, value in self.commands.items():
            print(key + ' : ' + value['description'])

        print()
        print()

        while True:
            #espera por qualquer entrada de interesse
            rlist, _, _ = select.select(self.rlist, [], [])
            #tratar todas as entradas prontas
            for read in rlist:
                if read == self.main_socket:  #pedido novo de conexao
                    clisock, addr = self.accept_incoming_connection(self.main_socket)
                    print ('New connection: ', addr)
                    #cria nova thread para atender o cliente
                    client_thread = threading.Thread(target=self.handle_incoming_connection, args=(clisock,addr))
                    client_thread.start()
                    self.client_threads.append(client_thread) #armazena a referencia da thread para usar com join()
                elif read == sys.stdin: #entrada padrao
                    cmd = input()

                    if cmd in self.commands:
                        self.commands[cmd]['callback']()
                        print()
                    else:
                        print('Invalid command.')

    def quit(self):
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
    
    def init_main_socket(self):
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

        # inclui o socket principal na lista de entradas de interesse
        self.rlist.append(sock)

        self.main_socket = sock

    def accept_incoming_connection(self, sock):
        '''Aceita o pedido de conexao de um cliente
        Entrada: o socket do servidor
        Saida: o novo socket da conexao e o endereco do cliente'''

        # estabelece conexao com o proximo cliente
        clisock, endr = sock.accept()

        # registra a nova conexao
        self.active_connections[clisock] = endr 

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

server = Server('', 10001)
server.run()