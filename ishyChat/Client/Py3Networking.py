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


import asyncio
##The last 3 imports are local files.
#import message packer/unpacker
import ishyChat.Utils.Packer as Pk

#import ishyChat.Utils.Encryptor as Encryptor
#These are messages to display to the user
import ishyChat.Utils.Messages as Messages
################
###End imports##
################


class ClientConnection(asyncio.Protocol):
    """This class handles sending and receiving messages
    
    to/from the server. It also deals with some metadata
    and commands issued by the user, and handles them, for
    non-view-dependent things (eg sending and receiving pings,
    which don't depend on what sort of GUI or CLI interface
    you're using)."""
    def __init__(self, factory, application, *args, **kwargs):
        # LineReceiver.__init__(self, *args, **kwargs)
        self.factory = factory
        self.app = application
        #Set up the encryption-getting rid of this
        #self.encryptor = Encryptor.Encryptor(key)

    def connection_made(self, transport):
        self.data_received(Messages.start_message)
        self.factory.state = "CONNECTED"
        self.transport = transport

    def data_received(self, line):
        if not line: return  # If we haven't been given anything, then we don't do anything.
        if isinstance(line, bytes):
            line = line.decode()
        # Note that line has '\r\n' at the end of it,
        # but that doesn't seem to cause any problems
        # with json decoding
        #while not line.endswith('}'):
            #line = line[:-1]
        dict_obj = Pk.packDown(line)
        name, msg, metadata = dict_obj['name'], dict_obj['message'], dict_obj['metadata']
        name_tag = ''
        if 'server' == name:
            if 'getname' in metadata:
                self.factory.state = "GET NAME"
            elif 'gotname' in metadata:
                self.factory.state = "CONNECTED"
                self.getUsers()
                self.app.addClient(self.name)
            elif 'pong' in metadata:
                msg = 'ping time: ' + str(time.clock() - self.ping_start)
            elif 'newclient' in metadata:
                new_name = msg[:msg.find(' ')]
                self.app.addClient(new_name)
            elif 'lostclient' in metadata:
                name_to_remove = msg[:msg.find(' ')]
                self.app.removeClient(name_to_remove)
            elif 'gotusers' in metadata:
                list_of_users = metadata['gotusers']
                self.app.addClients(*list_of_users)
                msg = 'Users in chatroom: ' + ' '.join(list_of_users)
        
        elif 'client' != name:
            name_tag = name
        self.app.addString(msg, name_tag)

    def sendLine(self, line):
        return self.send_data(line)

    def send_data(self, line):
        """Sends line, but only after checking to see
        
        if anything special need to be done (this is
        what self._command_parser does)."""
        state = self.factory.state
        if any((not line,
               self._command_parser(line),
               state == "NOT CONNECTED")): return
        
        if state == "GET NAME":
            self.name = line
            #self.name_enc = self.encryptor.encrypt_ECB(self.name)
            dict_to_send = Pk.makeDict(name=self.name, metadata={'newname': None})
        elif state == "CONNECTED":
            #iv, message = self.encryptor.encrypt(line)
            dict_to_send = Pk.makeDict(name=self.name, msg=line)
        line = Pk.packUp(dict_to_send)
        self.write(line)
    
    def write(self, line):
        if isinstance(line, str):
            line = line.encode()
        if not line.endswith(b'\r\n'):
            line += b'\r\n'
        self.transport.write(line)

    def _command_parser(self, line):
        """Checks if there are any commands in line.
        
        If there are, then they are dealt with. Note that
        GUI specific commands should have been dealt with
        already.
        
        If this function return True, then that means that
        the calling function should not print line.
        If it returns False, then the calling function
        *should* print line to the screen (ie insert it
        into the entrybox)."""
        if not line.startswith('/'): return
        line = line[1:].lower()
        if line == 'warning':
            self.line_received(Messages.warning_message)
            return True
        elif line == 'ping':
            if self.factory.state == "CONNECTED":
                self.write(Messages.ping_message)
                self.ping_start = time.clock()
                return True
        elif any((line == 'list', line == 'listusers')):
            if self.factory.state == "CONNECTED":
                self.getUsers()
                return True
        return False

    def getUsers(self):
        """Asks the server for a list of people in the chatroom"""
        self.write(Messages.getusers_message)


class Factory(object):
    def __init__(self):
        # The state is either "NOT CONNECTED" or "CONNECTED or GET NAME"
        # at different times.
        self.state = "NOT CONNECTED"
        self.loop = asyncio.get_event_loop()

    def run_reactor(self, address, port):
        # Need to add ssl to this, and repeatedly try to connect as well.
        self.line = ClientConnection(self, self.app)
        coro = self.loop.create_connection(lambda: self.line, host = address, port = port)
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
