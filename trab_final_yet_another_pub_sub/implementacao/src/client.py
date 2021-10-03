from services.client_service import ClientService

SERVER_LOCATION = 'localhost'
PORT = 65535

if __name__ == "__main__":
	client_service = ClientService(SERVER_LOCATION, PORT)
	client_service.start()