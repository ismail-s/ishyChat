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

#Twisted imports. Twisted is used to connect to the server
#and send and receive messages.
from twisted.internet import  reactor, ssl
from twisted.internet.protocol import ReconnectingClientFactory
from twisted.protocols.basic import LineReceiver

from twisted.internet import tksupport
##The last 3 imports are local files.

#import ishyChat.Utils.Encryptor as Encryptor
#These are messages to display to the user
import ishyChat.Utils.Messages as Messages

import ishyChat.Utils.Constants as Const
from ishyChat.Client.BaseNetworking import BaseConnection
################
###End imports##
################


class ClientConnection(BaseConnection, LineReceiver):
    """This class handles sending and receiving messages
    
    to/from the server. It also deals with some metadata
    and commands issued by the user, and handles them, for
    non-view-dependent things (eg sending and receiving pings,
    which don't depend on what sort of GUI or CLI interface
    you're using)."""
    def __init__(self, factory, application, *args, **kwargs):
        BaseConnection.__init__(self, factory, application, *args, **kwargs)

    def write(self, line):
        LineReceiver.sendLine(self, line)

class Factory(ReconnectingClientFactory):
    """Sets up a connection, repeatedly trying to remake
    
    the connection if the connection fails."""
    def __init__(self, *args, **kwargs):
        self.maxRetries = 10
        #self.key = key

        # The state is either "NOT CONNECTED" or "CONNECTED or GET NAME"
        # at different times.
        self.state = Const.STATE_NOT_CONNECTED

    def startedConnecting(self, connector):
        self.app.addString(Messages.starting_conn)
        self.resetDelay()

    def buildProtocol(self, address):
        self.line = ClientConnection(self, self.app)
        return self.line

    def clientConnectionLost(self, connector, reason):
        self.app.addString(Messages.conn_lost)
        self.state = Const.STATE_NOT_CONNECTED
        ReconnectingClientFactory.clientConnectionLost(self, connector, reason)

    def clientConnectionFailed(self, connector, reason):
        self.app.addString(Messages.conn_failed)
        self.state = Const.STATE_NOT_CONNECTED
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

    def install_urwid_support_and_connect_ssl(self, address, port):
        reactor.connectSSL(address, port, self, ssl.ClientContextFactory())
        return reactor
