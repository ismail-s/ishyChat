import argparse
from getpass import getpass
from ishyChat.Client.Client import Application as TkinterApp
from ishyChat.Server.Server import main as ServerApp

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
    args = parser.parse_args()
    args.func(args)
    
    
def runClient(args):
    address, port, key = args.host, args.port, args.key
    
    # Work on this section, make it simpler, and include checks on the values
    # inputted-here and in runServer
    if not address:
        address = raw_input("What address do you want to connect to?")
    if not port:
        port = int(raw_input("What port do you want to connect on?"))
    if not key:
        key = getpass("Please enter the key")
    TkinterApp(address, port, key)

def runServer(args):
    if not args.port:
        port = int(raw_input("What port do you want to listen on?"))
    port = args.port
    ServerApp(port)

if __name__ == '__main__':
    main()
