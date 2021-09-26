#Ver documentação em: https://rpyc.readthedocs.io/en/latest/

# Cliente de echo usando RPC
from models.models import CommandType, Publication, Subscription, Topic
from interpretation_layer import InterpretationLayer
import rpyc #modulo que oferece suporte a abstracao de RPC

SERVER_IP = 'localhost'
PORT = 65535

def main():
	interpretation_layer = InterpretationLayer()
	conn = rpyc.connect(SERVER_IP, PORT)
	
	try:
		while True:
			#interage com o servidor ate encerrar
			#fazRequisicoes(conn)

			command_str = input("Please type in a command: ")
			command, command_error = interpretation_layer.decode_command(command_str)

			if(command_error == None):
				result = None
				error = None

				if(command.type == CommandType.PUB.name):
					publication: Publication = command.data
					result, error = conn.root.exposed_publish(publication.to_json())
				elif(command.type == CommandType.SUB.name):
					subscription: Subscription = command.data
					result, error = conn.root.exposed_subscribe(subscription.to_json())
				elif(command.type == CommandType.UNSUB.name):
					subscription: Subscription = command.data
					result, error = conn.root.exposed_unsubscribe(subscription.to_json())
				elif(command.type == CommandType.CREATE.name):
					topic: Topic = command.data
					result, error = conn.root.exposed_create_topic(topic.to_json())
				elif(command.type == CommandType.DELETE.name):
					topic: Topic = command.data
					result, error = conn.root.exposed_delete_topic(topic.to_json())
				elif(command.type == CommandType.LIST.name):
					result, error = conn.root.exposed_list_topics()

				if(error != None):
					print('Error executing command: ', error)
				else:
					print(result)
			else:
				print('Error with command ', command_error)

	except KeyboardInterrupt:
		print('Stopping client...')
		conn.close()
	except Exception as e:
		print('Client stopped abnormally: ', e)
		conn.close()

# executa o cliente
if __name__ == "__main__":
	main()