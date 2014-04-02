# This file implements the Tkinter GUI
#!/usr/bin/env python
# -*- coding: utf-8 -*-
import json
#Tkinter related imports
import sys
if sys.version_info >= (3, 0):
    import tkinter as tk
    import tkinter.scrolledtext as ScrolledText
    import tkinter.ttk as ttk
    import tkinter.font as tkFont
else:
    import Tkinter as tk
    import ScrolledText
    import ttk
    import tkFont


#These are messages to display to the user
import ishyChat.Utils.Messages as Messages

import ishyChat.Client.Networking as Networking

#import the encryption/decryption stuff-seeing if I can remove this
#import ishyChat.Utils.Encryptor as Encryptor

# All the allowed Tkinter colours for printing coloured text
COLOURS = json.load(open('ishyChat//Client//Views//Colours.json', 'r'))



class Application(tk.Tk):
    """This is the main application class holding the chat client.

    All other classes are instantiated within this one."""
    def __init__(self):
        tk.Tk.__init__(self)
        self.protocol('WM_DELETE_WINDOW', Networking.stopReactor)
        self.wm_title("ishyChat")
        
        #Set up application
        self.frame = Frame(self)
        self.frame.pack(fill = tk.BOTH, expand = 1)
        
        #Set up factory
        self.factory = Networking.Factory()
        self.factory.install_tk_support(self)
        
        #Link the two together
        self.frame.factory = self.factory
        self.factory.app = self.frame
    
    def run(self, address, port):
        self.factory.run_reactor(address, port, self.factory)


class Frame(ttk.Frame):
    #Our Tkinter application stuff is held in this.
    def __init__(self, root, *args, **kwargs):
        ttk.Frame.__init__(self, root, *args, **kwargs)
        self.root = root
        
        #Set up widgets
        self._textboxSetUp()
        self._entryboxSetUp()
        
        self.msgdb = MessageDB()
        
        # This line must be called after _textboxSetUp() 
        self.clientdb = ClientDB(self.textbox)
        self.addClient = self.clientdb.addClient
        self.removeClient = self.clientdb.removeClient
        self.addClients = self.clientdb.addClients
        
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
        self.msgdb.reset() 
        string_to_send = self.entrybox.get()
        self.entrybox.delete(0, tk.END)     # Erase entrybox
        if any([not string_to_send, string_to_send == '',
                string_to_send.isspace()]): # don't want to be sending nothing!
            return
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
            self.factory.stop_reactor()
        if any((str_to_check == 'help', str_to_check == 'h')):
            self.addString(Messages.gui_help_message)
            return True
            
        elif str_to_check.isdigit():  # see docstring of history_printer below.
            msg = self.msgdb.command_history_printer(int(str_to_check))
            if msg:
                self.entrybox.insert(0, msg)
            return True
        #insert more options here
        return False

    def _getNextOldMsg(self, event):
        if event.keysym in ('Up', 'Down'):
            res = self.msgdb.getNextOldMsg(event.keysym, self.entrybox.get())
        else: return
        if res == -1: return
        self.entrybox.delete(0, tk.END)
        self.entrybox.insert(0, res)

    def addString(self, string_to_add, name = ''):
        """Adds string_to_add to the textbox, with optional name.
        
        if string_to_add is a tuple, then this is interpreted as
        (string_to_add, name), and dealt with as such."""

        #  adds string to textbox, makes it look nice. If there is a name, then it adds that too.
        if not string_to_add:
            return  # If we haven't been given anything, then we don't do anything.
        if isinstance(string_to_add, tuple):
            string_to_add, name = string_to_add
        self.msgdb.append(string_to_add)
        if name:
            self.addClient(name) # The clientName may/may not be known-this
            # call just makes sure
            self.textbox.insert(tk.END, ''.join(('<', name, '>',)), ("bold", "client_" + name))
        self.textbox.insert(tk.END, string_to_add + '\n', "normal") # This will be the entry point for implementing bold/colour text highlighting.
        self._scrollToBottom()
        self.textbox.bell() # Yes, this line is just here for the fun of it...

    def _scrollToBottom(self):
        """Scroll the textbox to the bottom"""
        self.textbox.yview(tk.END)

class MessageDB(object):
    """This class holds all messages in the textbox on screen

    and implements terminal-esque previous text printing (I
    have trouble explaining it better-read the code)."""
    def __init__(self):
        #We will store all the messages here
        self.msgs = []
        
        # This is -ve when a previous message is being displayed on screen,
        # having been brought up with the up and down keys
        self.curr_hist_msg = 0
        self.temp_first_old_msg = ''
    
    def append(self, string):
        if string:
            self.msgs.append(string)
            
    def reset(self):
        self.curr_hist_msg = 0
    
    def command_history_printer(self, index):
        """Prints out one of the last messages received in the entrybox.

        e.g. if index is 1, then the last message received is printed.
        if index is 2, the second-to-last message received is printed.
        """
        if index > len(self.msgs) or index < 1:
            return
        msg_to_print = self.msgs[-index]
        return msg_to_print
    
    def getNextOldMsg(self, event, curr_msg):
        """This takes in a string, either 'Up' or 'Down',
        
        and returns some corresponding previous message."""
        if event == 'Down':
            if -len(self.msgs) > self.curr_hist_msg or self.curr_hist_msg >= 0:
                return -1
            self.curr_hist_msg += 1
        elif event == 'Up':
            if -len(self.msgs) >= self.curr_hist_msg or self.curr_hist_msg > 0:
                return -1

            # Hard to explain what this does: basically, try
            # typing something in the entrybox when the program
            # is running, and then press and hold the up key.
            # Then, press and hold the down key, and you'll see
            # that the message you typed at the beginnning pops
            # up again. That's what this thing does (with line *
            # a bit further down too).
            if self.curr_hist_msg == 0:
                self.temp_first_old_msg = curr_msg
            self.curr_hist_msg -= 1
        else: return -1
        msg_to_send = ''
        #self.entrybox.delete(0, tk.END)
        if -len(self.msgs) <= self.curr_hist_msg < 0:
            msg_to_send = self.msgs[self.curr_hist_msg]
        # Line *, as referenced in the last comment
        elif self.curr_hist_msg == 0:
            msg_to_send = self.temp_first_old_msg
        
        return msg_to_send


class ClientDB(object):
    """Holds a list of all the people currently in the
    
    chatroom we're connnected to, and for each person,
    we have a corresponding colour"""
    def __init__(self, textbox):
        # Create a dict to hold the names of all the clients
        # and their corresponding colour. If they don't yet
        # have a colour, then this is ''.
        self.db = {}
        self.colours = COLOURS
        self.textbox = textbox
    
    def addClients(self, *args, **kwargs):
        "Adds a list of clients"
        for client in args:
            self.addClient(client)
        for client in kwargs.values():
            self.addClient(client)
    
    def addClient(self, new_name):
        if new_name in self.db:
            return
        self.db[new_name] = ''
        
        colour, flat_name = '', new_name.lower()
        for entry in self.colours:
            if flat_name in entry:
                self.db[new_name] = entry
                break
        if self.db[new_name] == '':
            for entry in self.colours:
                if entry not in self.db.values():
                    self.db[new_name] = entry
                    break
        self.textbox.tag_config('client_' + new_name,
                        foreground = self.db[new_name])
    
    def removeClient(self, name_to_delete):
        del self.db[name_to_delete]
    
    def getColour(self, name):
        return self.db[name]
