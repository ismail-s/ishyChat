#!/usr/bin/env python
# -*- coding: utf-8 -*-

import ishyChat.Utils.Packer as Packer
from ishyChat.Utils.Packer import makeDictAndPack
import ishyChat.Utils.Constants as Const

class BaseServer(object):
    def __init__(self, clients):
        self.clients = clients
        self.name = None
        self.state = Const.STATE_GETNAME
        #self.setLineMode()

    def connectionMade(self):
        return self.connection_made()

    def connection_made(self):
        msg_to_send = "Welcome to ishyChat!\n{} other people present.\nWhat's your name?".format(len(self.clients))
        self.write(makeDictAndPack(msg = msg_to_send, name = 'server',
                                    metadata = {'getname': None}))

    def connectionLost(self, reason):
        return self.connection_lost(reason)

    def connection_lost(self, reason):
        if self.name in self.clients.keys():
            del self.clients[self.name]
        people = 'person' if (len(self.clients)-1) == 1 else 'people'
        line = "{} has left. {} other {} still here.".format(self.name,
                                                            len(self.clients)-1,
                                                            people)
        self.broadcast(makeDictAndPack(msg = line, name = 'server',
                                        metadata = {'lostclient': None}))
        to_print = ' '.join((self.name, "has left.", str(len(self.clients)),
                            "clients connected."))
        print(to_print)

    def lineReceived(self, line):
        return self.data_received(line)

    def data_received(self, line):
        if 'ping' in (Packer.packDown(line))['metadata']:
            self.write(makeDictAndPack(name = 'server',
                                    metadata = {'pong': None}))
            return
        if self.state == Const.STATE_GETNAME:
            self.handle_GETNAME((Packer.packDown(line))['name'])
        elif self.state == Const.STATE_CHAT:
            self.handle_CHAT(line)
        else:
            pass

    def handle_GETNAME(self, name):
        if name in self.clients.keys():
            message = "Name taken. Please choose another name"
            self.write(makeDictAndPack(name = 'server', msg = message))
            return
        message = "Hiya {}!".format(name)
        self.write(makeDictAndPack(name = 'server',
                                    metadata = {'gotname': None},
                                    msg = message))
        self.name, self.clients[name], self.state = name, self, Const.STATE_CHAT

        to_print = ' '.join((name, "has been added.",
        str(len(self.clients)),
        "client{} connected.".format('' if len(self.clients)  == 1 else 's')))

        print(to_print)
        message = "{} has joined the chat.".format(name)
        string = makeDictAndPack(name = 'server', metadata = ['newclient'],
                                msg = message)
        self.broadcast(string, also_send_to_self = False)
        
    def handle_CHAT(self,line):
        # Maybe these next 2 lines should be moved into data_received
        metadata = Packer.packDown(line)['metadata']
        if 'getusers' in metadata:
            self.write(makeDictAndPack(name = 'server',
                            metadata = {'gotusers': list(self.clients.keys())}))
            return
        # Need to work on this command so that everyone is alerted when someone
        # changes their name
        if 'newname' in metadata:
            new_name = metadata['newname']
            if new_name not in self.clients.keys():
                del self.clients[self.name]
                old_name = self.name
                self.name, self.clients[new_name] = new_name, self
                line_to_send_back = makeDictAndPack(name = 'server',
                                            metadata = {'newname': self.name})
                
                self.broadcast(makeDictAndPack(name = 'server',
                            metadata = {'changename': [old_name, self.name]}),
                            also_send_to_self = False)
                print('{} has changed name to {}.'.format(old_name, self.name))
            else:
                line_to_send_back = makeDictAndPack(name = 'server',
                                    metadata = {'newname': self.name})
            self.write(line_to_send_back)
            return
        self.broadcast(line)

    def broadcast(self, line, also_send_to_self = True):
        if also_send_to_self:
            for name, client in self.clients.items():
                client.write(line)
        else:
            for name, client in self.clients.items():
                if name != self.name:
                    client.write(line)
