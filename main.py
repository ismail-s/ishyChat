import sys, argparse
if sys.version_info >= (3, 0):
    from tkinter import Tk
    import tkinter.simpledialog as tkDialogs
else:
    from Tkinter import Tk
    import tkSimpleDialog as tkDialogs

prog_description = """ishyChat-A simple encrypted chat client over HTTPS."""

def main():
    parser = argparse.ArgumentParser(description = prog_description)
    subparsers = parser.add_subparsers()

    # Set up arguments for the client
    client = subparsers.add_parser('client', help = "Run the (basic, simple, encrypted) chat client.")
    client.add_argument("--host", help="This is the address of the server you want to connect to")
    client.add_argument("--port", help="This is the port to connect to on the server", type=int)
    view = client.add_mutually_exclusive_group(required = True)
    
    view.add_argument('-g', '--gui', action = 'store_true', help = 'Run the GUI version of the chat client')
    view.add_argument('-c', '--cli', action = 'store_true', help = 'Run the command-line version of the chat client (requires Urwid)')
    client.set_defaults(func = runClient)

    # Set up arguments for the server
    server = subparsers.add_parser('server', help = "Run the server program that the chat clients connect to")
    server.add_argument("--port", help = "This is the port that the server will listen on.", type=int)
    server.set_defaults(func = runServer)

    args = parser.parse_args()
    try:
        args.func(args)
    except AttributeError as e:
        print(e)
        parser.parse_args(['-h'])

def getInput(type_of_input, *args, **kwargs):
    root = Tk()
    root.withdraw()
    if type_of_input == str:
        func = tkDialogs.askstring
    elif type_of_input == int:
        func = tkDialogs.askinteger
    else: return
    res, count = '', 0

    # Basically, in this loop, we ask the user at most twice
    # for their input before assuming that they want to close
    # the application, and then we quit the program.
    while count < 2:
        res = func(*args, **kwargs)
        if res:
            root.destroy()
            return res
        else: count +=1
    sys.exit(1)

def runClient(args):
    address, port = args.host, args.port

    if not address:
        address = getInput(str, 'Address',
            'What address do you want to connect to?',)
    if not port:
        port = getInput(int, 'Port',
            'What port do you want to connect on?',
            minvalue=1,
            maxvalue=65535)
    if sys.version_info >= (3, 4):
        from ishyChat.Client.Py3Networking import Factory
    else:
        from ishyChat.Client.Networking import Factory
    if args.gui:
        from ishyChat.Client.Views.TkinterView import Application as App
    elif args.cli:
        from ishyChat.Client.Views.UrwidView import Application as App

    app = App(Factory)
    app.run(address, port)

def runServer(args):
    try:
        if sys.version_info >= (3, 4):
            from ishyChat.Server.Py3Server import PubFactory as ServerApp
        else:
            from ishyChat.Server.Server import PubFactory as ServerApp
    except (ImportError, SyntaxError) as e:
        print(e)
        print("Something went wrong with importing the server code.")
        sys.exit(1)
    if not args.port:
        port = getInput(int, "Port", "What port do you want to listen on?")
    else:
        port = args.port
    server = ServerApp()
    server.run_reactor(port)

if __name__ == '__main__':
    main()
