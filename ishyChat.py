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
#This module allows us to not show the key when it is entered.
from getpass import getpass
#This module is used to parse command-line arguments and to provide
#a nice command-line interface.
import argparse
#Tkinter related imports
import Tkinter as tk
import ScrolledText
import ttk
import tkFont
#Twisted imports. Twisted is used to connect to the server
#and send and receive messages.
from twisted.internet import tksupport, reactor
from twisted.internet.protocol import ReconnectingClientFactory
from twisted.protocols.basic import LineReceiver
##The last 3 imports are local files.
#import message packer/unpacker
import Packer as Pk
#import the encryption/decryption stuff
import Encryptor
#These are messages to display to the user
import Messages
################
###End imports##
################

class Application(tk.Tk):
    """This is the main application class holding the chat client.

    All other classes are instantiated within this one."""
    def __init__(self, address, port, key):
        tk.Tk.__init__(self)
        self.protocol('WM_DELETE_WINDOW', reactor.stop)
        self.wm_title("ishyChat")
        #Set up application
        self.frame = Frame(self, key)
        self.frame.pack(fill = tk.BOTH, expand = 1)
        tksupport.install(self)
        #Set up factory
        self.factory = Factory()
        #Link the two together
        self.frame.factory = self.factory
        self.factory.frame = self.frame
        #Set up reactor
        reactor.connectTCP(address, port, self.factory)
        #Let's get this show on the road!
        reactor.run()


class Frame(ttk.Frame):
    #Our Tkinter application stuff is held in this.
    def __init__(self, root, key, *args, **kwargs):
        ttk.Frame.__init__(self, root, *args, **kwargs)
        self.root = root
        #We will store all the messages here.
        self.msgs = []
        #this is either "NOT CONNECTED" or "CONNECTED or GET NAME"
        self.state = "NOT CONNECTED"
        #Set up the encryption
        self.encryptor = Encryptor.Encryptor(key)
        #Set up widgets
        self._textboxSetUp()
        self._entryboxSetUp()
        #Pack widgets
        self.textbox.pack(fill=tk.BOTH, expand=1)
        self.entrybox.pack(fill=tk.X, expand=1, padx=3, pady=3)

    def _textboxSetUp(self):
        self.textbox = ScrolledText.ScrolledText(self, wrap=tk.WORD, width=50, height=20)
        #Set up some tags for printing bold and coloured text.
        self.textbox.tag_config("bold", font=tkFont.Font(weight=tkFont.BOLD))
        self.textbox.tag_config("normal", font=tkFont.Font())
        self.textbox.tag_config("a", foreground="blue", font=tkFont.Font(underline=1))

    def _entryboxSetUp(self):
        self.entrybox = ttk.Entry(self, width=50)
        self.entrybox.bind("<Return>", self.sendStringFromEntrybox)

    def sendStringFromEntrybox(self, event):
        """Gets whatever is in the entrybox and works out what to do

        with it. This may be sending it, or running some other function.
        """
        string_to_send = self.entrybox.get()
        if not string_to_send:              # don't want to be sending nothing!
            return
        self.entrybox.delete(0, tk.END)     # Erase entrybox
        if self._command_parser(string_to_send): # Check if there are any commands to run.
            return
        self._scrollToBottom()              # Scroll textbox to the bottom
        if self.state == "NOT CONNECTED":
            return
        if self.state == "GET NAME":        # Names are encrypted in ECB mode.
            self.name = string_to_send
            self.name_enc = self.encryptor.encrypt_ECB(self.name)
            dict_to_send = Pk.makeDict(name=self.name_enc, metadata=['name'])
        elif self.state == "CONNECTED":
            iv, message = self.encryptor.encrypt(string_to_send)
            dict_to_send = Pk.makeDict(name=self.name_enc, iv=iv, msg=message)
        string_to_send = Pk.packUp(dict_to_send)
        self.factory.line.sendLine(string_to_send)

    def _command_parser(self, string):
        """This function is only called by sendStringFromMessageBox.

        It checks for any commands in string, and executes them."""
        if not string.startswith('/'):
            return False
        string_to_check = string[1:]  # get rid of the / at the start of the string.
        if string_to_check == 'q' or string_to_check == 'quit':
            reactor.stop()  # This line ends the program (but on some systems it crashes it, which is a bit bizarre...)
        elif string_to_check == 'test':  # just a test string.
            self.addString(Messages.test_message)
            return True
        elif string_to_check == 'help' or string_to_check == 'h':
            self.addString(Messages.help_message)
            return True
        elif string_to_check == 'warning':
            self.addString(Messages.warning_message)
            return True
        elif string_to_check == 'ping':
            if self.state == "CONNECTED":
                self.factory.line.sendLine(Messages.ping_message)
                self.ping_start = time.clock()
            return True
        elif string_to_check.isdigit():  # see docstring of history_printer below.
            self._command_history_printer(int(string_to_check))
            return True
        #insert more options here
        return False

    def _command_history_printer(self, index):
        """Prints out one of the last messages received in the entrybox.

        e.g. if index is 1, then the last message received is printed.
        if index is 2, the second-to-last message received is printed.
        """
        if index > len(self.msgs) or index < 1:
            return
        msg_to_print = self.msgs[-index]
        self.entrybox.insert(0, msg_to_print)

    def addString(self, string):
        """Adds string to the textbox. This docstring is outdated.

        If required, string is also decrypted.
        If string starts with /serv or /client, then no decryption is
        attempted. If decryption is attempted and string is not
        encrypted, then errors will be thrown up."""
        if not string:
            return
        dict_object = Pk.packDown(string)
        if 'server' == dict_object['name']:
            string_to_add = dict_object['message']
            if 'getname' in dict_object['metadata']:
                self.state = "GET NAME"
            elif 'gotname' in dict_object['metadata']:
                self.state = "CONNECTED"
            elif 'pong' in dict_object['metadata']:
                string_to_add = 'ping time: ' + str(time.clock() - self.ping_start)
        elif 'client' == dict_object['name']:
            string_to_add = dict_object['message']
        else:
            msg_to_add = self.encryptor.decrypt(dict_object['iv'], dict_object['message'])
            self.msgs.append(msg_to_add)
            name = '<' + self.encryptor.decrypt_ECB(dict_object['name']) + '> '
            self.textbox.insert(tk.END, name, "bold")
            string_to_add = msg_to_add
        string_to_add = string_to_add + '\n'
        self.textbox.insert(tk.END, string_to_add, "normal") # This will be the entry point for implementing bold/colour text highlighting.
        self._scrollToBottom()
        self.textbox.bell() # Yes, this line is just here for the fun of it...

    def _scrollToBottom(self):
        """Scroll the textbox to the bottom"""
        self.textbox.yview(tk.END)


class ClientConnection(LineReceiver):
    def connectionMade(self):
        self.factory.frame.addString(Messages.start_message)
        self.factory.frame.state = "CONNECTED"

    def lineReceived(self, line):
        self.factory.frame.addString(line)


class Factory(ReconnectingClientFactory):
    def __init__(self, *args, **kwargs):
        self.maxRetries = 10

    def startedConnecting(self, connector):
        self.frame.addString(Messages.starting_conn)
        self.resetDelay()

    def buildProtocol(self, address):
        self.line = ClientConnection()
        self.line.factory = self
        return self.line

    def clientConnectionLost(self, connector, reason):
        self.frame.addString(Messages.conn_lost)
        self.frame.state = "NOT CONNECTED"
        ReconnectingClientFactory.clientConnectionLost(self, connector, reason)

    def clientConnectionFailed(self, connector, reason):
        self.frame.addString(Messages.conn_failed)
        self.frame.state = "NOT CONNECTED"
        ReconnectingClientFactory.clientConnectionFailed(self, connector, reason)

def getInfo():
    address = raw_input("What address do you want to connect to?")
    port = int(raw_input("What port do you want to connect on?"))
    key = getpass("Please enter the key")
    return address, port, key

def main():
    parser = argparse.ArgumentParser(description="A simple encrypted chat client")
    parser.add_argument("--host", help="This is the address of the server you want to connect to")
    parser.add_argument("--port", help="This is the port to connect to on the server", type=int)
    parser.add_argument("--key", help="This is the key that will be used for encryption and decryption of messages.")
    args = parser.parse_args()
    address, port, key = args.host, args.port, args.key
    if not address:
        address = raw_input("What address do you want to connect to?")
    if not port:
        port = int(raw_input("What port do you want to connect on?"))
    if not key:
        key = getpass("Please enter the key")
    #address, port, key = getInfo()
    Application(address, port, key)

if __name__ == "__main__":
    main()
