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
#
from twisted.internet import reactor, protocol
from twisted.protocols import basic

import Packer
from Packer import makeDictAndPack

class PubProtocol(basic.LineReceiver):
    def __init__(self, factory):
        self.clients = factory
        self.name = None
        self.state = "GETNAME"

    def connectionMade(self):
        msg_to_send = "Welcome to ishyChat!\n{} other people present.\nWhat's your name?".format(len(self.clients))
        self.sendLine(makeDictAndPack(msg = msg_to_send, name = 'server', metadata = ['getname']))

    def connectionLost(self, reason):
        if self.name in self.clients.keys():
            del self.clients[self.name]
        people = 'person' if (len(self.clients)-1) == 1 else 'people'
        line = "{} has left. {} other {} still here.".format(self.name, len(self.clients)-1, people)
        for name, client in self.clients.iteritems():
            client.sendLine(makeDictAndPack(msg = line, name = 'server', metadata = ['lostclient']))
        print self.name, "has left.", len(self.clients), "clients connected."

    def lineReceived(self, line):
        if 'ping' in (Packer.packDown(line))['metadata']:
            self.sendLine(makeDictAndPack(name = 'server', metadata = ['pong']))
            return
        if self.state == "GETNAME":
            self.handle_GETNAME((Packer.packDown(line))['name'])
        elif self.state == "CHAT":
            self.handle_CHAT(line)
        else:
            pass

    def handle_GETNAME(self, name):
        if name in self.clients.keys():
            message = "Name taken. Please choose another name"
            self.sendLine(makeDictAndPack(name = 'server', msg = message))
            return
        message = "Hiya {}, or at least, that's what I think you're called!".format(name)
        self.sendLine(makeDictAndPack(name = 'server', metadata = ['gotname'], msg = message))
        self.name, self.clients[name], self.state = name, self, "CHAT"
        print name, "has been added.", len(self.clients), "clients connected."
        message = "{} has joined the chat.".format(name)
        string = makeDictAndPack(name = 'server', metadata = ['newclient'], msg = message)
        for names, client in self.clients.iteritems():
            if names != self.name:
                self.sendLine(string)

    def handle_CHAT(self,line):
        for name, client in self.clients.iteritems():
            client.sendLine(line)

class PubFactory(protocol.Factory):
    def __init__(self):
        #this is a dict of nameTheClientChose: ClientClass
        self.clients = {}
        print "Server up and running."

    def buildProtocol(self, addr):
        #self.clients is passed so each client instance can send messages to the others.
        return PubProtocol(self.clients)

def main():
    reactor.listenTCP(int(raw_input("Please enter a port. ")), PubFactory())
    reactor.run()

if __name__ == '__main__':
	main()
