import socket
import json

HOST = 'localhost' # maquina onde esta o par passivo
PORTA = 5000        # porta que o par passivo esta escutando
MAX_BUFFER_SIZE = 1024000

# cria socket
sock = socket.socket() # default: socket.AF_INET, socket.SOCK_STREAM 

# conecta-se com o par passivo
sock.connect((HOST, PORTA)) 

while True:
    print('Enter \'quit()\' to exit the program.')
   
    print('Enter the filename: ')
    filename = input()

    if filename == "quit()":
        # encerra a conexao
        sock.close()
        break
    
    print('Enter the search term: ')
    term = input()

    if term == "quit()":
        # encerra a conexao
        sock.close()
        break
    
    message = json.dumps({
        'filename':filename,
        'term': term
    })

    # envia uma mensagem para o par conectado
    sock.send(message.encode(encoding="utf-8"))

    #espera a resposta do par conectado (chamada pode ser BLOQUEANTE)
    response_bytes = sock.recv(MAX_BUFFER_SIZE) # argumento indica a qtde maxima de bytes da mensagem
    response_str = str(response_bytes,  encoding='utf-8')

    print(response_str)

    #response_json = json.loads(response_str)

    # if(response_json['error']):
    #     print('Error: ' + response_json['error'])
    # else:
    #     print('Occurences: ' + str(response_json['occurrences']))
    
    print()
    print('-----------------------------------------------------------------------------------------------------')
    print()