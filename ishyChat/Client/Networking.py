#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  untitled.py
#
#  Copyright 2013 pt-id.tk
#
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.
#
#  Also, this software should only be used for good and not evil.
#
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

##The last 3 imports are local files.
#import message packer/unpacker
import ishyChat.Utils.Packer as Pk


#These are messages to display to the user
import ishyChat.Utils.Messages as Messages
################
###End imports##
################

def runReactor(address, port, factory):
    """Sets up the reactor and runs it.
    
    Basically, once the application has been set up,
    this function is called to start the application."""
    reactor.connectSSL(address, port, factory, ssl.ClientContextFactory())
    
    #Let's get this show on the road!
    reactor.run()

def stopReactor(*args, **kwargs):
    reactor.stop()


class ClientConnection(LineReceiver):
    """This class handles sending and receiving messages
    
    to/from the server. It also deals with some metadata
    and commands issued by the user, and handles them, for
    non-view-dependent things (eg sending and receiving pings,
    which don't depend on what sort of GUI or CLI interface
    you're using)."""
    def __init__(self, factory, key, *args, **kwargs):
        # LineReceiver.__init__(self, *args, **kwargs)
        self.factory = factory
        self.frame = self.factory.frame
        #Set up the encryption
        self.encryptor = Encryptor.Encryptor(key)
    
    def connectionMade(self):
        self.lineReceived(Messages.start_message)
        self.factory.state = "CONNECTED"

    def lineReceived(self, line):
        if not line: return  # If we haven't been given anything, then we don't do anything.
        dict_obj = Pk.packDown(line)
        name, msg, metadata = dict_obj['name'], dict_obj['message'], dict_obj['metadata']
        name_tag = ''
        if 'server' == name:
            string_to_add = msg
            if 'getname' in metadata:
                self.factory.state = "GET NAME"
            elif 'gotname' in metadata:
                self.factory.state = "CONNECTED"
            elif 'pong' in metadata:
                string_to_add = 'ping time: ' + str(time.clock() - self.ping_start)
        elif 'client' == name:
            string_to_add = msg
        else:
            name_tag = self.encryptor.decrypt_ECB(name)
            string_to_add = self.encryptor.decrypt(dict_obj['iv'], msg)
        self.frame.addString(string_to_add, name_tag)
    
    def sendLine(self, line):
        """Sends line, but only after checking to see
        
        if anything special need to be done (this is
        what self._command_parser does)."""
        state = self.factory.state
        if any((not line,
               self._command_parser(line),
               state == "NOT CONNECTED")): return
        
        if state == "GET NAME":        # Names are encrypted in ECB mode.
            self.name = line
            self.name_enc = self.encryptor.encrypt_ECB(self.name)
            dict_to_send = Pk.makeDict(name=self.name_enc, metadata=['name'])
        elif state == "CONNECTED":
            iv, message = self.encryptor.encrypt(line)
            dict_to_send = Pk.makeDict(name=self.name_enc, iv=iv, msg=message)
        line = Pk.packUp(dict_to_send)
        LineReceiver.sendLine(self, line)
        
    def _command_parser(self, line):
        """Checks if there are any commands in line.
        
        If there are, then they are dealt with. Note that
        GUI specific commands should have been dealt with
        already."""
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
        return False


class Factory(ReconnectingClientFactory):
    """Sets up a connection, repeatedly trying to remake
    
    the connection if the connection fails."""
    def __init__(self, key, *args, **kwargs):
        self.maxRetries = 10
        self.key = key
        
        # The state is either "NOT CONNECTED" or "CONNECTED or GET NAME"
        # at different times.
        self.state = "NOT CONNECTED"

    def startedConnecting(self, connector):
        self.frame.addString(Messages.starting_conn)
        self.resetDelay()

    def buildProtocol(self, address):
        self.line = ClientConnection(self, self.key)
        return self.line

    def clientConnectionLost(self, connector, reason):
        self.frame.addString(Messages.conn_lost)
        self.state = "NOT CONNECTED"
        ReconnectingClientFactory.clientConnectionLost(self, connector, reason)

    def clientConnectionFailed(self, connector, reason):
        self.frame.addString(Messages.conn_failed)
        self.state = "NOT CONNECTED"
        ReconnectingClientFactory.clientConnectionFailed(self, connector, reason)


if __name__ == "__main__":
    print """This is no longer intended to be run directly!
Instead, run main.py in the highest directory (2 directories up)."""
