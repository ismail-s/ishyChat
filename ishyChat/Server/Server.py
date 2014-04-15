#!/usr/bin/env python
# -*- coding: utf-8 -*-

from twisted.internet import reactor, protocol, ssl
from twisted.protocols import basic
import sys
import ishyChat.Utils.Packer as Packer
from ishyChat.Utils.Packer import makeDictAndPack
from ishyChat.Server.BaseServer import BaseServer

class PubProtocol(BaseServer, basic.LineReceiver):
    def __init__(self, clients):
        BaseServer.__init__(self, clients)
        self.setLineMode()

    def write(self, line):
        self.sendLine(line)

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
