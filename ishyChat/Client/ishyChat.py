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
from twisted.internet import tksupport, reactor, ssl
from twisted.internet.protocol import ReconnectingClientFactory
from twisted.protocols.basic import LineReceiver

##The last 3 imports are local files.
#import message packer/unpacker
import ishyChat.Utils.Packer as Pk

#import the encryption/decryption stuff
import ishyChat.Utils.Encryptor as Encryptor

#These are messages to display to the user
import ishyChat.Utils.Messages as Messages
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
        self.factory = Factory(key)
        
        #Link the two together
        self.frame.factory = self.factory
        self.factory.frame = self.frame
        
        #Set up reactor
        reactor.connectSSL(address, port, self.factory, ssl.ClientContextFactory())
        
        #Let's get this show on the road!
        reactor.run()


class Frame(ttk.Frame):
    #Our Tkinter application stuff is held in this.
    def __init__(self, root, key, *args, **kwargs):
        ttk.Frame.__init__(self, root, *args, **kwargs)
        self.root = root
        
        #We will store all the messages here.
        self.msgs = []
        # This is -ve when a previous message is being displayed on screen,
        # having been brought up with the up and down keys
        self.curr_hist_msg = 0
        
        #Set up the encryption-to get rid of this line
        self.encryptor = Encryptor.Encryptor(key)
        
        #Set up widgets
        self._textboxSetUp()
        self._entryboxSetUp()
        
        #Pack widgets
        self.textbox.pack(fill=tk.BOTH, expand=1)
        self.entrybox.pack(fill=tk.X, expand=1, padx=3, pady=3)
        
        self.entrybox.focus_set() # set focus on entrybox

    def _textboxSetUp(self):
        self.textbox = ScrolledText.ScrolledText(self, wrap=tk.WORD, width=50, height=20)
        #Set up some tags for printing bold and coloured text.
        self.textbox.bold = tkFont.Font(weight=tkFont.BOLD)
        self.textbox.normal = tkFont.Font(underline = 0)
        self.textbox.link = font=tkFont.Font(underline = 1)
        self.textbox.tag_config("bold", font=self.textbox.bold)
        self.textbox.tag_config("normal", font=self.textbox.normal)
        self.textbox.tag_config("a", foreground = "blue", font = self.textbox.link)

    def _entryboxSetUp(self):
        self.entrybox = ttk.Entry(self, width=50)
        self.entrybox.bind("<Return>", self.sendStringFromEntrybox)
        self.entrybox.bind("<Up>", self._getNextOldMsg)
        self.entrybox.bind("<Down>", self._getNextOldMsg)

    def sendStringFromEntrybox(self, event):
        """Gets whatever is in the entrybox and works out what to do

        with it. This may be sending it, or running some other function.
        """
         # Refactor:
         # Pass the string to the line.sendLine(string_to_send)
        self.curr_hist_msg = 0 
        string_to_send = self.entrybox.get()
        if not string_to_send:              # don't want to be sending nothing!
            return
        self.entrybox.delete(0, tk.END)     # Erase entrybox
        if self._command_parser(string_to_send): # Check if there are any commands to run.
            return
        self._scrollToBottom()              # Scroll textbox to the bottom
        if self.factory.state != "NOT CONNECTED":
            self.factory.line.sendLine(string_to_send)

    def _command_parser(self, str_to_check):
        """This function is only called by sendStringFromMessageBox.

        It checks for any commands in string, and executes them."""
        if not str_to_check.startswith('/'):
            return False
        str_to_check = str_to_check[1:].lower()
        
        # Quit command is here, so that the user can quit the program
        # even if the ClientConnection instance does not exist ie when
        # the chat client is not connected.
        if any((str_to_check == 'q', str_to_check == 'quit')):
            reactor.stop()  # This line ends the program (but on some systems it crashes it, which is a bit bizarre...)
        if any((str_to_check == 'help', str_to_check == 'h')):
            self.addString(Messages.gui_help_message)
            return True
        elif str_to_check.isdigit():  # see docstring of history_printer below.
            self._command_history_printer(int(str_to_check))
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
    
    def _getNextOldMsg(self, event):
        if event.keysym == 'Down':
            if -len(self.msgs) > self.curr_hist_msg or self.curr_hist_msg >= 0:
                return
            self.curr_hist_msg += 1
        elif event.keysym == 'Up':
            if -len(self.msgs) >= self.curr_hist_msg or self.curr_hist_msg > 0:
                return

            # Hard to explain what this does: basically, try
            # typing something in the entrybox when the program
            # is running, and then press and hold the up key.
            # Then, press and hold the down key, and you'll see
            # that the message you typed at the beginnning pops
            # up again. That's what this thing does (with line *
            # a bit further down too).
            if self.curr_hist_msg == 0:
                self.temp_first_old_msg = self.entrybox.get()
            self.curr_hist_msg -= 1
        else: return
        msg_to_send = ''
        self.entrybox.delete(0, tk.END)
        if -len(self.msgs) <= self.curr_hist_msg < 0:
            msg_to_send = self.msgs[self.curr_hist_msg]
        # Lines *, as referenced in the last comment
        elif self.curr_hist_msg == 0:
            msg_to_send = self.temp_first_old_msg
       
        self.entrybox.insert(0, msg_to_send)

    def addString(self, string_to_add, name = ''):
        """Adds string to the textbox (well, the parameter 'string' should actually
        
        be a dict in the form of a JSON string, but this dict/JSON string thingy
        contains the message to be added to the textbox).
        If required, the message is also decrypted before being printed to the
        screen.
        This function checks who sent the message, and any metadata attached to
        the message. Based on who sent the message and what the metadata is,
        decryption may not be done, or something else might happen.
        
        If the message was sent by the server then it is not decrypted.
        If the message was sent by the server and has 'pong' in its
        metadata, then this is interpreted as a reply to a ping message
        that this client would have sent earlier (to time the roundtrip
        time between client and server)."""

        #  adds string to textbox, makes it look nice. If there is a name, then it adds that too.
        if not string_to_add:
            return  # If we haven't been given anything, then we don't do anything.
        if isinstance(string_to_add, tuple):
            string_to_add, name = string_to_add
        self.msgs.append(string_to_add)
        if name:
            self.textbox.insert(tk.END, ''.join(('<', name, '>',)), "bold")
        self.textbox.insert(tk.END, string_to_add + '\n', "normal") # This will be the entry point for implementing bold/colour text highlighting.
        self._scrollToBottom()
        self.textbox.bell() # Yes, this line is just here for the fun of it...

    def _scrollToBottom(self):
        """Scroll the textbox to the bottom"""
        self.textbox.yview(tk.END)


class ClientConnection(LineReceiver):
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



def getArgs():
    parser = argparse.ArgumentParser(description="A simple encrypted chat client")
    parser.add_argument("--host", help="This is the address of the server you want to connect to")
    parser.add_argument("--port", help="This is the port to connect to on the server", type=int)
    parser.add_argument("--key", help="This is the key that will be used for encryption and decryption of messages.")
    return parser.parse_args()

def main():
    args = getArgs()
    address, port, key = args.host, args.port, args.key
    
    # Work on this section, make it simpler
    if not address:
        address = raw_input("What address do you want to connect to?")
    if not port:
        port = int(raw_input("What port do you want to connect on?"))
    if not key:
        key = getpass("Please enter the key")
    
    Application(address, port, key)

if __name__ == "__main__":
    main()
