import socket
import json
from file_utilities.file_utilities import FileParser

HOST = ''    # '' possibilita acessar qualquer endereco alcancavel da maquina local
PORTA = 5000  # porta onde chegarao as mensagens para essa aplicacao
FILES_DIRECTORY = './files/'
MAX_CONCURRENT_CONNECTIONS = 5
MAX_BUFFER_SIZE = 1024000

def run_server():
    # cria um socket para comunicacao
    sock = socket.socket() # valores default: socket.AF_INET, socket.SOCK_STREAM  

    # vincula a interface e porta para comunicacao
    sock.bind((HOST, PORTA))

    # define o limite maximo de conexoes pendentes e coloca-se em modo de espera por conexao
    sock.listen(MAX_CONCURRENT_CONNECTIONS)

    print('Started listening at ' + str(HOST) + ':' + str(PORTA))

    # aceita a primeira conexao da fila (chamada pode ser BLOQUEANTE)
    novoSock, endereco = sock.accept() # retorna um novo socket e o endereco do par conectado
    print ('New connection: ', endereco)

    while True:
        # depois de conectar-se, espera uma mensagem (chamada pode ser BLOQUEANTE))
        request_bytes = novoSock.recv(MAX_BUFFER_SIZE) # argumento indica a qtde maxima de dados
        
        if not request_bytes: 
            break 
        
        request_str = str(request_bytes,  encoding='utf-8')
        
        request_json = json.loads(request_str)

        filename = request_json['filename']
        term = request_json['term']

        parser = FileParser()
        occurrences, error = parser.count_occurences_of_term(FILES_DIRECTORY + filename, term)

        response_message = json.dumps({
            'filename':filename,
            'term':term,
            'occurrences':occurrences,
            'error':error
        })

        print(response_message)

        novoSock.send(response_message.encode(encoding="utf-8"))

    # fecha o socket da conexao
    novoSock.close() 

    # fecha o socket principal
    sock.close() 

run_server()