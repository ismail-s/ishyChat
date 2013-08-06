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

import base64, json
class gb:
    standard_dict = {'message': None, 'name': 'server', 'metadata': []}
    pong_dict = dict(standard_dict)
    pong_dict['metadata'] = ['pong']


class PubProtocol(basic.LineReceiver):
    def __init__(self, factory):
        self.clients = factory
        self.name = None
        self.state = "GETNAME"

    def connectionMade(self):
        msg_to_send = "Welcome to ishyChat!\n{} other people present.\nWhat's your name?".format(len(self.clients))
        dict_to_send = dict(gb.standard_dict)
        dict_to_send['message'] = msg_to_send
        dict_to_send['metadata'] = ['getname']
        self.sendLine(base64.b64encode(json.dumps(dict_to_send)))

    def connectionLost(self, reason):
        if self.name in self.clients.keys():
            del self.clients[self.name]
        line = "{} has left. {} people/person still here.".format(self.name, len(self.clients))
        dict_to_send = dict(gb.standard_dict)
        dict_to_send['message'] = line
        for name, client in self.clients.iteritems():
            client.sendLine(base64.b64encode(json.dumps(dict_to_send)))
        print self.name, "has left.", len(self.clients), "clients connected."

    def lineReceived(self, line):
        if 'ping' in json.loads(base64.b64decode(line))['metadata']:
            self.sendLine(base64.b64encode(json.dumps(gb.pong_dict)))
            return
        if self.state == "GETNAME":
            self.handle_GETNAME(json.loads(base64.b64decode(line))['name'])
        elif self.state == "CHAT":
            self.handle_CHAT(line)
        else:
            pass

    def handle_GETNAME(self, name):
        if name in self.clients.keys():
            dict_to_send = dict(gb.standard_dict)
            dict_to_send['message'] = "Name taken. Please choose another name"
            self.sendLine(base64.b64encode(json.dumps(dict_to_send)))
            return
        dict_to_send = dict(gb.standard_dict)
        dict_to_send['message'] = "Hiya {}, or at least, that's what I think you're called!".format(name)
        dict_to_send['metadata'] = ['gotname']
        self.sendLine(base64.b64encode(json.dumps(dict_to_send)))
        self.name = name
        self.clients[name] = self
        print name, "has been added.", len(self.clients), "clients connected."
        self.state = "CHAT"

    def handle_CHAT(self,line):
        #msg = "<{}> {}".format(self.name, line)
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
    reactor.listenTCP(1025, PubFactory())
    reactor.run()

if __name__ == '__main__':
	main()
