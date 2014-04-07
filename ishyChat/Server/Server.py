#!/usr/bin/env python
# -*- coding: utf-8 -*-

from twisted.internet import reactor, protocol, ssl
from twisted.protocols import basic
import sys
import ishyChat.Utils.Packer as Packer
from ishyChat.Utils.Packer import makeDictAndPack

class PubProtocol(basic.LineReceiver):
    def __init__(self, factory):
        self.clients = factory
        self.name = None
        self.state = "GETNAME"
        self.setLineMode()

    def connectionMade(self):
        msg_to_send = "Welcome to ishyChat!\n{} other people present.\nWhat's your name?".format(len(self.clients))
        self.sendLine(makeDictAndPack(msg = msg_to_send, name = 'server', metadata = {'getname': None}))

    def connectionLost(self, reason):
        if self.name in self.clients.keys():
            del self.clients[self.name]
        people = 'person' if (len(self.clients)-1) == 1 else 'people'
        line = "{} has left. {} other {} still here.".format(self.name, len(self.clients)-1, people)
        for name, client in self.clients.iteritems():
            client.sendLine(makeDictAndPack(msg = line, name = 'server', metadata = {'lostclient': None}))
        print self.name, "has left.", len(self.clients), "clients connected."

    def lineReceived(self, line):
        if 'ping' in (Packer.packDown(line))['metadata']:
            self.sendLine(makeDictAndPack(name = 'server', metadata = {'pong': None}))
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
        message = "Hiya {}!".format(name)
        self.sendLine(makeDictAndPack(name = 'server', metadata = {'gotname': None}, msg = message))
        self.name, self.clients[name], self.state = name, self, "CHAT"
        print name, "has been added.", len(self.clients), "clients connected."
        message = "{} has joined the chat.".format(name)
        string = makeDictAndPack(name = 'server', metadata = ['newclient'], msg = message)
        for names, client in self.clients.iteritems():
            if names != self.name:
                client.sendLine(string)

    def handle_CHAT(self,line):
        # Maybe these next 2 lines should be moved into lineReceived
        if 'getusers' in Packer.packDown(line)['metadata']:
            self.sendLine(makeDictAndPack(name = 'server', metadata = {'gotusers': self.clients.keys()}))
            return
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

def main(port):
    ssl_context_factory = ssl.DefaultOpenSSLContextFactory('ishyChat/Server/keys/server.pem', 'ishyChat/Server/keys/cert.pem')
    reactor.listenSSL(port, PubFactory(), ssl_context_factory)
    reactor.run()


if __name__ == '__main__':
    print """This is no longer intended to be run directly!
Instead, run main.py in the highest directory (2 directories up)."""
