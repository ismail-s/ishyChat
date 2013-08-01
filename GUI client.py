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

#Tkinter related imports
import Tkinter as tk
import ScrolledText

#Twisted imports. Twisted is used to connect to the server
#and send and receive messages.
from twisted.internet import tksupport, reactor
from twisted.internet.protocol import ReconnectingClientFactory
from twisted.protocols.basic import LineReceiver

#This module allows us to not show the key when it is entered.
import getpass

#import the encryption/decryption stuff
import Encryptor

class Application(tk.Frame):
    #Our Tkinter application stuff is held in this.
    def __init__(self, root, factory, key, *args, **kwargs):
        tk.Frame.__init__(self, root, *args, **kwargs)
        self.root = root
        self.factory = factory
        self.msgs = []  #We will store all the messages here.
        self.state = "NOT CONNECTED"  #this is either "NOT CONNECTED" or "CONNECTED"

        #Set up the encryption
        self.encryptor = Encryptor.Encryptor(key)

        #Set up widgets
        self.textboxSetUp()
        self.entryboxSetUp()

        #Pack widgets
        self.textbox.pack(fill = tk.BOTH, expand = 1)
        self.entrybox.pack(fill = tk.X, expand = 1, padx = 3, pady = 3)

        #Pack the frame
        self.pack(fill = tk.BOTH, expand = 1)

    def textboxSetUp(self):
        self.textbox = ScrolledText.ScrolledText(self, wrap = tk.WORD, width = 50, height = 20)

    def entryboxSetUp(self):
        self.entrybox = tk.Entry(self, width = 50)
        self.entrybox.bind("<Return>", self.sendStringFromEntrybox)

    def sendStringFromEntrybox(self, event):
        string_to_send = self.entrybox.get()
        if not string_to_send:  #don't want to be sending nothing!
            return
        self.entrybox.delete(0, tk.END)  #Erase entrybox
        if self.command_parser(string_to_send):
            return
        self._scrollToBottom()  #Scroll textbox to the bottom
        if self.state == "NOT CONNECTED":
            return
        string_to_send = self.encryptor.encrypt(string_to_send)
        self.factory.line.sendLine(string_to_send)

    def command_parser(self, string):
        if not string.startswith('/'):
            return False
        string_to_check = string[1:]  #get rid of the / at the start of the string.
        if string_to_check == 'q':    #'/q' is one way of exiting.
            reactor.stop()
        elif string_to_check == 'test':  #just a test string.
            self.addString('/clientTesting...')
            return True
        elif string_to_check == 'help':
            self.command_help()
            return True
        elif string_to_check == str(int(string_to_check)):  #see docstring of history_printer below.
            self.command_history_printer(int(string_to_check))
            return True
        #insert more options here
        return False

    def command_history_printer(self, index):
        """Prints out one of the last messages received in the entrybox.
e.g. if index is 1, then the last message received is printed.
if index is 2, the second-to-last message received is printed.
"""
        msgs_length = len(self.msgs)
        if index > msgs_length or index < 1:
            return
        msg_location = -index
        msg_to_print = self.msgs[msg_location]
        self.entrybox.insert(0, msg_to_print)
    
    def command_help(self):
        """Prints a help string in the textbox."""

    def addString(self, string):
        #This is a string used by the server
        #when it sends its own messages to clients.
        SERVER_STRING = "/serv"
        
        #This is a string used to identify internal messages
        CLIENT_STRING = "/client"
        
        if not string:
            return
        if string.startswith(SERVER_STRING):
            decrypted_string = string[len(SERVER_STRING):]
        elif string.startswith(CLIENT_STRING):
            decrypted_string = string[len(CLIENT_STRING):]
        else:
            print string
            decrypted_string = self.encryptor.decrypt(string)
            self.msgs.append(decrypted_string[decrypted_string.find('>') + 2:])
        string_to_add = decrypted_string + '\n'
        self.textbox.insert(tk.END, string_to_add)
        self._scrollToBottom()

    def _scrollToBottom(self):
        """Scroll the textbox to the bottom"""
        self.textbox.yview(tk.END)


class clientConnection(LineReceiver):
    def connectionMade(self):
        start_message = """/clientConnection established.
Please note that I have no way of knowing if you typed the key correctly. If it was typed incorrectly, then you will quite soon see some mumbo-jumbo text on-screen instead of messages from other users.
All messages are encrypted using the key you entered at the beginning. This key should have been the same one everyone else is using, otherwise the chat won't work. The key should have been ideally 32 characters long to make it more secure.
Also note that the server only receives an encrypted version of the client's names.
The server will now speak to you, so please follow its instructions.


"""
        self.factory.app.addString(start_message)
        self.factory.app.state = "CONNECTED"

    def lineReceived(self, line):
        self.factory.app.addString(line)


class Factory(ReconnectingClientFactory):
    def __init__(self, key, *args, **kwargs):
        #ReconnectingClientFactory.__init__(self, *args, **kwargs)
        self.maxRetries = 10
        self.root = tk.Tk()
        self.root.protocol('WM_DELETE_WINDOW', reactor.stop)
        self.root.wm_title("ishyChat")
        self.app = Application(self.root, self, key)
        tksupport.install(self.root)

    def startedConnecting(self, connector):
        self.app.addString("/clientStarted to connect.")
        self.resetDelay()

    def buildProtocol(self, address):
        self.line = clientConnection()
        self.line.factory = self
        return self.line

    def clientConnectionLost(self, connector, reason):
        self.app.addString("/clientConnection lost. Attempting to re-establish connection.")
        self.app.state = "NOT CONNECTED"
        ReconnectingClientFactory.clientConnectionLost(self, connector, reason)

    def clientConnectionFailed(self, connector, reason):
        self.app.addString("/clientConnection failed. Attempting to re-establish connection.")
        self.app.state = "NOT CONNECTED"
        ReconnectingClientFactory.clientConnectionFailed(self, connector, reason)

def getInfo():
    address = raw_input("What address do you want to connect to?")
    port = int(raw_input("What port do you want to connect on?"))
    key = getpass.getpass("Please enter the key")
    return address, port, key

def main():
    address, port, key = getInfo()
    reactor.connectTCP(address, port, Factory(key))
    reactor.run()

if __name__ == "__main__":
    main()
