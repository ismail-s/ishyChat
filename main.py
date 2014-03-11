import argparse
from ishyChat.Client.ishyChat import Application as TkinterApp
prog_description = """ishyChat-A simple encrypted chat client over HTTPS with some additional (pointless, rubbish) encryption on top, just for the fun of it."""

def main():
    parser = argparse.ArgumentParser(description = prog_description)
    subparsers = parser.add_subparsers()
    
    # Set up arguments for the client
    client = subparsers.add_parser('client', help = "Run the (basic, simple, encrypted) chat client.")
    client.add_argument("--host", help="This is the address of the server you want to connect to")
    client.add_argument("--port", help="This is the port to connect to on the server", type=int)
    client.add_argument("--key", help="This is the key that will be used for encryption and decryption of messages.")
    client.set_defaults(func = runClient)
    
    # Set up arguments for the server
    server = subparsers.add_parser('server', help = "Run the server program that the chat clients connect to")
    server.add_argument("--port", help = "This is the port that the server will listen on.", type=int)
    server.set_defaults(func = runServer)
    args = parser.parse_args(['server', '-h'])
    args.func(args)
    
    
def runClient(args):
    address, port, key = args.host, args.port, args.key
    
    # Work on this section, make it simpler, and include checks on the values inputted
    if not address:
        address = raw_input("What address do you want to connect to?")
    if not port:
        port = int(raw_input("What port do you want to connect on?"))
    if not key:
        key = getpass("Please enter the key")
    TkinterApp(address, port, key)

def runServer(args):
    if not port:
        port = int(raw_input("What port do you want to listen on?"))
    # run server with given commands-need to sort this line out

if __name__ == '__main__':
    main()
