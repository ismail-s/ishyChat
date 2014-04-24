# This file implements the Tkinter GUI
#!/usr/bin/env python
# -*- coding: utf-8 -*-
import json
#Tkinter related imports
import sys, os
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


# These are messages to display to the user
import ishyChat.Utils.Messages as Messages

import ishyChat.Utils.Constants as Const
from ishyChat.Utils.Filepath import path_to
# All the allowed Tkinter colours for printing coloured text
dark_colours_path = path_to('ishyChat/Client/Views/dark_colours.json')
COLOURS = json.load(open(dark_colours_path, 'r'))


class Application(tk.Tk):
    """This is the main application class holding the chat client.

    All other classes are instantiated within this one."""
    def __init__(self, factory):
        """Sets up this application and factory, linking
        the two together."""
        tk.Tk.__init__(self)
        self.wm_title("ishyChat")

        # Set up application
        self.frame = Frame(self)
        self.frame.pack(fill = tk.BOTH, expand = 1)
        
        # Resize the window to a decent size
        self.geometry('400x300')

        # Set up factory
        self.factory = factory()
        self.factory.install_tk_support(self)
        self.protocol('WM_DELETE_WINDOW', self.factory.stop_reactor)

        #Link the two together
        self.frame.factory = self.factory
        self.factory.app = self.frame

    def run(self, address, port):
        """Runs the program, connecting to the supplied address:port."""
        self.factory.run_reactor(address, port)


class Frame(ttk.Frame):
    """This is the frame inside the root Tkinter widget. This frame
    holds the textbox and entrybox."""
    def __init__(self, root, *args, **kwargs):
        """Initialises the frame, setting up the textbox and entrybox,
        and linking up to the messageDB and the clientDB"""
        ttk.Frame.__init__(self, root, *args, **kwargs)
        self.root = root

        #Set up widgets
        self._textboxSetUp()
        self._entryboxSetUp()

        self.msgdb = MessageDB()

        # This line must be called after _textboxSetUp()
        # There must be shorter/better way of doing this...
        self.clientdb = ClientDB(self.textbox)
        self.addClient = self.clientdb.addClient
        self.removeClient = self.clientdb.removeClient
        self.addClients = self.clientdb.addClients
        self.changeClientName = self.clientdb.changeClientName

        #Pack widgets
        self.textbox.pack(fill=tk.BOTH, expand=1)
        self.entrybox_frame.pack(fill = tk.X,
                                expand = 0,
                                padx=3,
                                pady=3)

        self.entrybox.focus_set() # set cursor focus on entrybox

    def _textboxSetUp(self):
        """Set up textbox with some tags for printing normal/bold text
        and links."""
        # Here, the height is set to 1, not because we want the
        # window to be 1 high, but as a hack, as it means that
        # the geometry manager is configured to make the
        # window look nice for any size >= the size specified
        # here. Then, above, in the Application class, we
        # resize the window to a larger size.
        # If that doesn't make sense, then change 'height = 1'
        # to eg 'height = 20', and start the program and try
        # resizing the window.
        self.textbox = ScrolledText.ScrolledText(self, wrap = tk.WORD,
                                                width = 40, height = 1)

        #Set up some tags for printing bold and coloured text.
        self.textbox.bold = tkFont.Font(weight=tkFont.BOLD)
        self.textbox.normal = tkFont.Font(underline = 0)
        self.textbox.link = font=tkFont.Font(underline = 1)
        self.textbox.tag_config("bold", font=self.textbox.bold)
        self.textbox.tag_config("normal", font=self.textbox.normal)
        self.textbox.tag_config("a", foreground = "blue",
                                font = self.textbox.link)

    def _entryboxSetUp(self):
        self.entrybox_frame = ttk.Frame(self)
        self.entrybox = ttk.Entry(self.entrybox_frame, width=40)
        self.send_button = ttk.Button(self.entrybox_frame,
                                text = "Send",
                                command = self.sendStringFromEntrybox)
        self.entrybox.bind("<Return>", self.sendStringFromEntrybox)
        self.entrybox.bind("<Up>", self._getNextOldMsg)
        self.entrybox.bind("<Down>", self._getNextOldMsg)
        self.entrybox.pack(side = tk.LEFT, fill=tk.X, expand=1)
        self.send_button.pack(side = tk.LEFT, fill= tk.X, expand = 0)

    def sendStringFromEntrybox(self, *args):
        """Gets whatever is in the entrybox and works out what to do

        with it. This may be sending it, or running some other function.
        This function should be called whenever the user presses Enter
        in the textbox, but can be called separately."""
        self.entrybox.focus_set()
        self.msgdb.reset()
        string_to_send = self.entrybox.get()
        self.entrybox.delete(0, tk.END)     # Erase entrybox

        # Make sure we're not sending nothing.
        if any([not string_to_send, string_to_send == '',
                string_to_send.isspace()]): 
            return

        # Check if there are any commands to run.
        if self._command_parser(string_to_send):
            return
        self._scrollToBottom()  # Scroll textbox to the bottom
        if self.factory.state != Const.STATE_NOT_CONNECTED:
            self.factory.line.sendLine(string_to_send)

    def _command_parser(self, str_to_check):
        """This function is only called by sendStringFromMessageBox.

        It checks for any commands in str_to_check, and executes them.
        """
        if not str_to_check.startswith('/'):
            return False
        str_to_check = str_to_check[1:].lower()

        # Quit command is here, and not in Networking, so that the user
        # can quit the program even if the ClientConnection instance
        # does not exist ie when the chat client is not connected.
        if any((str_to_check == 'q', str_to_check == 'quit')):
            self.factory.stop_reactor()

        # Help message
        if any((str_to_check == 'help', str_to_check == 'h')):
            self.addString(Messages.gui_help_message)
            return True

        # see docstring of history_printer below to understand this.
        elif str_to_check.isdigit():
            msg = self.msgdb.command_history_printer(int(str_to_check))
            if msg:
                self.entrybox.insert(0, msg)
            return True

        #insert more options here
        return False

    def _getNextOldMsg(self, event):
        if event.keysym in ('Up', 'Down'):
            res = self.msgdb.getNextOldMsg(event.keysym,
                                        self.entrybox.get())
        else: return
        if res == -1: return
        self.entrybox.delete(0, tk.END)
        self.entrybox.insert(0, res)

    def addString(self, string_to_add, name = ''):
        """Adds string_to_add to the textbox, with optional name.
        
        if string_to_add is a tuple, then this is interpreted as
        (string_to_add, name), and dealt with as such."""

        # If we haven't been given anything, then we don't do anything.
        if not string_to_add:
            return  
        if isinstance(string_to_add, tuple):
            string_to_add, name = string_to_add
        self.msgdb.append(string_to_add)
        if name:
            self.addClient(name) # The clientName may/may not be
            # known-this call just makes sure-should this call
            # be moved into ClientDB class?
            self.textbox.insert(tk.END,
                                ''.join(('<', name, '>',)),
                                ("bold", "client_" + name))
        
        # This next line will be the entry point for implementing
        # bold/colour text highlighting.
        self.textbox.insert(tk.END, string_to_add + '\n', "normal")
        self._scrollToBottom()

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

        # This is -ve when a previous message is being displayed on
        # screen, having been brought up with the up and down keys.
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
        self.colours_l = [e.lower() for e in self.colours]
        self.textbox = textbox

    def addClients(self, *args, **kwargs):
        "Adds a list of clients, by repeatedly callling addClient."
        for client in args:
            self.addClient(client)
        for client in kwargs.values():
            self.addClient(client)

    def addClient(self, new_name):
        """Adds new_name to the database of clients, making sure there's
        
        no duplicates. Then, a tag is created for new_name ie a colour
        is given to it. Then, whenever we get messages from new_name,
        we can colour their name in the colour we've assigned to them.
        """
        if new_name in self.db:
            return

        # A little hack to get around 'black' not being
        # a standard named tkinter/tk colour.
        if 'black' in new_name.lower():
            self.addClient('gray')
            colour = self.db['gray']
            self.textbox.tag_delete('client_' + 'gray')
            self.textbox.tag_config('client_' + new_name,
                                    foreground = colour)
            del self.db['gray']
            self.db[new_name] = colour
            return

        self.db[new_name] = ''

        flat_name = new_name.lower()
        # First, we try to see if new_name matches any of the available
        # colours, and if it does, then it's given that colour.
        for e, entry in enumerate(self.colours_l):
            if flat_name in entry and self.colours[e] not in self.db.values():
                self.db[new_name] = self.colours[e]
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

    def changeClientName(self, old_name, new_name):
        self.removeClient(old_name)
        self.addClient(new_name)

    def getColour(self, name):
        return self.db[name]
