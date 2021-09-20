from models.models import CommandType, Message, Subscription, Publication, Topic, Command

class InterpretationLayer:

    def decode_command(self, command_str: str):
        try:
            argv = command_str.split(' ')
        
            command = argv[0].upper()

            if(command == CommandType.PUB.name):
                topic_id = argv[1]
                message_body = ' '.join(argv[2:])

                message = Message(message_body)
                publication = Publication(topic_id, message)

                command = Command(type = CommandType.PUB.name, data=publication)

                return command, None
            elif(command == CommandType.SUB.name):
                topic_id = argv[1]

                subscription = Subscription(topic_id)

                command = Command(type = CommandType.SUB.name, data=subscription)

                return command, None
            elif(command == CommandType.UNSUB.name):

                topic_id = argv[1]

                subscription = Subscription(topic_id)

                command = Command(type = CommandType.UNSUB.name, data=subscription)

                return command, None
            elif(command == CommandType.CREATE.name):
                topic_id = argv[1]

                topic = Topic(topic_id)
                
                command = Command(type = CommandType.CREATE.name, data=topic)
                
                return command, None
            elif(command == CommandType.DELETE.name):
                topic_id = argv[1]

                topic = Topic(topic_id)

                command = Command(type = CommandType.DELETE.name, data=topic)
                
                return command, None
            elif(command == CommandType.LIST.name):

                command = Command(type = CommandType.LIST.name, data=None)

                return command, None
            else:
                return None, 'Invalid command'
        except Exception as e:
            return None, e.__class__

    # def encode_command(self, command: Command):
    #     encoded_command = ''

    #     try:
    #         if(command.type == CommandType.HELLO.name):
    #             user : User = command.data
    #             encoded_command = CommandType.HELLO.name + ' ' + user.username
    #             return encoded_command, None
    #         elif(command.type == CommandType.BYE.name):
    #             encoded_command = CommandType.BYE.name
    #             return encoded_command, None
    #         elif(command.type == CommandType.PEERS.name):
    #             encoded_command = CommandType.PEERS.name
    #             return encoded_command, None
    #         elif(command.type == CommandType.MESSAGE.name):
    #             message : Message = command.data
    #             encoded_command = CommandType.MESSAGE.name + ' ' + message.user.username + ' ' + message.message_body
    #             return encoded_command, None
    #         elif(command.type == CommandType.LIST.name):
    #             encoded_command = CommandType.LIST.name
    #             return encoded_command, None
    #         elif(command.type == CommandType.QUIT.name):
    #             encoded_command = CommandType.QUIT.name
    #             return encoded_command, None
    #     except Exception as e:
    #         return None, e.__class__

if __name__ == '__main__':
    i = InterpretationLayer()
    # command = Command(CommandType.MESSAGE.name, data=Message(User('gadnlino'), 'Ola', 1888773))
    # encoded_command, error = i.encode_command(command)

    # if(error == None):
    #     print(encoded_command)
    # else:
    #     print(error)

    print('Digite um comando: ')
    command = input()
    decoded_command, error = i.decode_command(command)
    if(error == None):
        json_string=decoded_command.to_json()
        # json_string=json.dumps(decoded_command, cls=EnhancedJSONEncoder)
        print(json_string)
    else:
        print(error)


