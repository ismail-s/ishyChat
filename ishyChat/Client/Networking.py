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


#Twisted imports. Twisted is used to connect to the server
#and send and receive messages.
from twisted.internet import  reactor, ssl
from twisted.internet.protocol import ReconnectingClientFactory
from twisted.protocols.basic import LineReceiver

from twisted.internet import tksupport
##The last 3 imports are local files.
#import message packer/unpacker
import ishyChat.Utils.Packer as Pk

#import ishyChat.Utils.Encryptor as Encryptor
#These are messages to display to the user
import ishyChat.Utils.Messages as Messages
################
###End imports##
################


class ClientConnection(LineReceiver):
    """This class handles sending and receiving messages
    
    to/from the server. It also deals with some metadata
    and commands issued by the user, and handles them, for
    non-view-dependent things (eg sending and receiving pings,
    which don't depend on what sort of GUI or CLI interface
    you're using)."""
    def __init__(self, factory, application, *args, **kwargs):
        self.factory = factory
        self.app = application
        #Set up the encryption-getting rid of this
        #self.encryptor = Encryptor.Encryptor(key)

    def connectionMade(self):
        self.lineReceived(Messages.start_message)
        self.factory.state = "CONNECTED"

    def lineReceived(self, line):
        if not line: return  # If we haven't been given anything, then we don't do anything.
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
        LineReceiver.sendLine(self, line)

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
            self.lineReceived(Messages.warning_message)
            return True
        elif line == 'ping':
            if self.factory.state == "CONNECTED":
                LineReceiver.sendLine(self, Messages.ping_message)
                self.ping_start = time.clock()
                return True
        elif any((line == 'list', line == 'listusers')):
            if self.factory.state == "CONNECTED":
                self.getUsers()
                return True 
        return False

    def getUsers(self):
        """Asks the server for a list of people in the chatroom"""
        LineReceiver.sendLine(self, Messages.getusers_message)


class Factory(ReconnectingClientFactory):
    """Sets up a connection, repeatedly trying to remake
    
    the connection if the connection fails."""
    def __init__(self, *args, **kwargs):
        self.maxRetries = 10
        #self.key = key
        
        # The state is either "NOT CONNECTED" or "CONNECTED or GET NAME"
        # at different times.
        self.state = "NOT CONNECTED"

    def startedConnecting(self, connector):
        self.app.addString(Messages.starting_conn)
        self.resetDelay()

    def buildProtocol(self, address):
        self.line = ClientConnection(self, self.app)
        return self.line

    def clientConnectionLost(self, connector, reason):
        self.app.addString(Messages.conn_lost)
        self.state = "NOT CONNECTED"
        ReconnectingClientFactory.clientConnectionLost(self, connector, reason)

    def clientConnectionFailed(self, connector, reason):
        self.app.addString(Messages.conn_failed)
        self.state = "NOT CONNECTED"
        ReconnectingClientFactory.clientConnectionFailed(self, connector, reason)

    def run_reactor(self, address, port):
        """Sets up the reactor and runs it.
        
        Basically, once the application has been set up,
        this function is called to start the application."""
        # Need to add authentication to this
        reactor.connectSSL(address, port, self, ssl.ClientContextFactory())

        #Let's get this show on the road!
        reactor.run()

    def stop_reactor(self, *args, **kwargs):
        reactor.stop()

    def install_tk_support(self, root):
        tksupport.install(root)
