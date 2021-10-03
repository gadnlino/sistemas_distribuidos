from rpyc.utils.server import ThreadedServer
from services.message_broker_service import MessageBrokerService

PORT = 65535

if __name__ == '__main__':
	broker_svc = ThreadedServer(MessageBrokerService, port=PORT)

	try:
		print('Starting server')
		broker_svc.start()
	except KeyboardInterrupt:
		print('Stopping server...')
		broker_svc.close()
	except Exception as e:
		print('Server stopped abnormally: ', e)
		broker_svc.close()