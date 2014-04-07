#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
This is the main client file for isyChat. It contains code for making
The application and setting up and managing the connection to the
server.
Run this file to run ishyChat client.
"""

########################
###Imports##############
########################
#This is for timing pings.
import time
import ssl

import asyncio
##The last 3 imports are local files.
#import message packer/unpacker
import ishyChat.Utils.Packer as Pk

#import ishyChat.Utils.Encryptor as Encryptor
#These are messages to display to the user
import ishyChat.Utils.Messages as Messages

from ishyChat.Client.BaseNetworking import BaseConnection
################
###End imports##
################


class ClientConnection(BaseConnection, asyncio.Protocol):
    """This class handles sending and receiving messages
    
    to/from the server. It also deals with some metadata
    and commands issued by the user, and handles them, for
    non-view-dependent things (eg sending and receiving pings,
    which don't depend on what sort of GUI or CLI interface
    you're using)."""
    def __init__(self, factory, application, *args, **kwargs):
        BaseConnection.__init__(self, factory, application, *args, **kwargs)

    def connection_made(self, transport):
        BaseConnection.connection_made(self)
        self.transport = transport

    def data_received(self, line):
        if isinstance(line, bytes):
            line = line.decode()
        # Note that line has '\r\n' at the end of it,
        # but that doesn't seem to cause any problems
        # with json decoding
        #while not line.endswith('}'):
            #line = line[:-1]
        BaseConnection.data_received(self, line)

    def write(self, line):
        if isinstance(line, str):
            line = line.encode()
        if not line.endswith(b'\r\n'):
            line += b'\r\n'
        self.transport.write(line)


class Factory(object):
    def __init__(self):
        # The state is either "NOT CONNECTED" or "CONNECTED or GET NAME"
        # at different times.
        self.state = "NOT CONNECTED"
        self.loop = asyncio.get_event_loop()

    def run_reactor(self, address, port):
        # Need to add ssl to this, and repeatedly try to connect as well.
        self.line = ClientConnection(self, self.app)
        sslcontext = ssl.SSLContext(ssl.PROTOCOL_SSLv23)
        sslcontext.load_verify_locations(cafile = 'ishyChat/Server/keys/cert.pem')
        coro = self.loop.create_connection(lambda: self.line, host = address, port = port, ssl = sslcontext)
        # The below commented out code maybe should be worked on-the
        # idea is that, like in Netoworking.py, we can try and reconnect
        # to the server whenever the connection fails. But, this try-
        # except clause should be extended to the nearly all the below
        # code in this method
        #while 1:
            #try:
                #self.loop.run_until_complete(coro)
            #except ConnectionRefusedError as e:
                #self.app.addString(Messages.conn_failed)
                #continue
            #break
        self.loop.run_until_complete(coro)
        self.loop.run_forever()
        self.loop.close()

    def stop_reactor(self, *args, **kwargs):
        self.loop.stop()

    def install_tk_support(self, root, ms = 10.0):
        time_to_wait = ms/1000.0
        
        def callback():
            root.update()
            self.loop.call_later(time_to_wait, callback)

        self.loop.call_later(time_to_wait, callback)
