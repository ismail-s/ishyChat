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

class PubProtocol(basic.LineReceiver):
    def __init__(self, factory):
        self.clients = factory
        self.name = None
        self.state = "GETNAME"

    def connectionMade(self):
        self.sendLine("/servWelcome to ishyChat!")
        self.sendLine("/serv{} other people present.".format(len(self.clients)))
        self.sendLine("/serv/nameWhat's your name?")

    def connectionLost(self, reason):
        if self.name in self.clients.keys():
            del self.clients[self.name]
        line = "/serv{} has left. {} people/person still here.".format(self.name, len(self.clients))
        for name, client in self.clients.iteritems():
            client.sendLine(line)
        print self.name, "has left.", len(self.clients), "clients connected."

    def lineReceived(self, line):
        if line == '/ping':
            self.sendLine('/serv/pong')
            return
        if self.state == "GETNAME":
            self.handle_GETNAME(line)
        elif self.state == "CHAT":
            self.handle_CHAT(line)
        else:
            pass

    def handle_GETNAME(self, name):
        if name in self.clients.keys():
            self.sendLine("/servName taken. Please choose another name")
            return
        self.sendLine("/serv/gotnameHiya {}, or at least, that's what I think you're called!".format(name))
        self.name = name
        self.clients[name] = self
        print name, "has been added.", len(self.clients), "clients connected."
        self.state = "CHAT"

    def handle_CHAT(self,line):
        msg = "<{}> {}".format(self.name, line)
        for name, client in self.clients.iteritems():
            client.sendLine(msg)

class PubFactory(protocol.Factory):
    def __init__(self):
        #this is a dict of nameTheClientChose: ClientClass
        self.clients = {}
        print "Server up and running."

    def buildProtocol(self, addr):
        #self.clients is passed so each client instance can send messages to the others.
        return PubProtocol(self.clients)

def main():
    reactor.listenTCP(1025, PubFactory())
    reactor.run()
    return 0

if __name__ == '__main__':
	main()
