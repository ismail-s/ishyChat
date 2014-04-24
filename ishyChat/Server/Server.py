#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os

from twisted.internet import reactor, protocol, ssl
from twisted.protocols import basic
import ishyChat.Utils.Packer as Packer
from ishyChat.Utils.Packer import makeDictAndPack
from ishyChat.Utils.Filepath import path_to
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


    def buildProtocol(self, addr):
        #self.clients is passed so each client instance can send messages to the others.
        return PubProtocol(self.clients)

    def run_reactor(self, port):
        cert = path_to('ishyChat/Server/keys/cert.pem')
        keyfile = path_to('ishyChat/Server/keys/server.pem')
        ssl_context_factory = ssl.DefaultOpenSSLContextFactory(keyfile, cert)
        reactor.listenSSL(port, self, ssl_context_factory)
        print("Server up and running.")
        reactor.run()