#!/usr/bin/env python
# -*- coding: utf-8 -*-

import urwid

# These are messages to display to the user
import ishyChat.Utils.Messages as Messages

import ishyChat.Utils.Constants as Const
from ishyChat.Utils.Filepath import path_to

###################
# TODO
# Make the app look nicer-work on PALETTE
# Look into making this also work with asyncio
###################

###################
# Colour definitions

#Make sure these are all bold or standout a bit!
PALETTE_COLOURS_TUPLE = [('black', '', '', ''),
('dark red', '', '', ''),
('dark green', '', '', ''),
('brown', '', '', ''),
('dark blue', '', '', ''),
('dark magenta', '', '', ''),
('dark cyan', '', '', ''),
('dark gray', '', '', ''),
('light red', '', '', ''),
('light green', '', '', ''),
('light blue', '', '', ''),
('light magenta', '', '', ''),
('light cyan', '', '', ''),
('light gray', '', '', ''),
('yellow', '', '', ''),
('white', '', '', '')]

PALETTE = [('edit', '', '', 'standout'), # What text in the edit box should look like
('message', '', '', '') # What messages sent/received should look like
] + PALETTE_COLOURS_TUPLE

PALETTE_COLOURS = [e[0] for e in PALETTE_COLOURS_TUPLE]
###################

class Application(object):
    """This is the main application class holding the chat client.

    All other classes are instantiated within this one."""
    def __init__(self, factory):
        """Sets up this application and factory, linking
        the two together."""

        # Set up application
        self.frame = InnerFrame()

        # Set up factory
        self.factory = factory()

        #Link the two together
        self.frame.factory = self.factory
        self.factory.app = self.frame

    def run(self, address, port):
        """
        Runs the program, connecting to the supplied address:port.
        Unlike in other cases, here the final call to run the reactor is
        made, not in the networking library, but over here."""
        reactor = self.factory.install_urwid_support_and_connect_ssl(address, port)
        event_loop = urwid.TwistedEventLoop(reactor = reactor)
        self.frame.loop = urwid.MainLoop(self.frame,
                              palette = PALETTE,
                              # How should unhandled input be handled, if at all?
                              #unhandled_input = lambda :raise urwid.ExitMainLoop(),
                              event_loop = event_loop)
        self.frame.loop.run()


class InnerFrame(urwid.Frame):
    """This is the frame inside the root Tkinter widget. This frame
    holds the textbox and entrybox."""
    def __init__(self):
        """Initialises the frame, setting up the textbox and entrybox,
        and linking up to the messageDB and the clientDB"""
        self.msgdb = MessageDB()

        #Set up widgets
        self._textboxSetUp()
        self._entryboxSetUp(self.msgdb)

        super(InnerFrame, self).__init__(self.textbox, footer = self.entrybox)

        # This line must be called after _textboxSetUp()
        # There must be shorter/better way of doing this...
        self.clientdb = ClientDB()
        self.addClient = self.clientdb.addClient
        self.removeClient = self.clientdb.removeClient
        self.addClients = self.clientdb.addClients
        self.getColour = self.clientdb.getColour
        self.changeClientName = self.clientdb.changeClientName

        self.set_focus_on_entrybox()

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
        self.listwalker = urwid.SimpleListWalker([])
        self.textbox = urwid.ListBox(self.listwalker)

    def _entryboxSetUp(self, msgdb):
        # Here, msgdb is passed in even though it is under self.msgdb,
        # as this makes it obvious that this method uses msgdb, so
        # msgdb needs to be created before running this method.
        """
        Set up entrybox, along with the send button, putting the
        two into a frame. Bindings are added to the
        Enter, Up and Down keys for the entrybox, and the button is
        also given a callback that's the same as that for the
        Enter key."""
        self.entrybox = Entrybox(msgdb)

    def keypress(self, size, key):
        if key == 'enter':
            self.sendStringFromEntrybox()
        else:
            super(InnerFrame, self).keypress(size, key)

    def sendStringFromEntrybox(self, *args):
        """Gets whatever is in the entrybox and works out what to do

        with it. This may be sending it, or running some other function.
        This function should be called whenever the user presses Enter
        in the textbox, but can be called separately."""
        self.set_focus_on_entrybox()
        self.msgdb.reset()
        string_to_send = self.entrybox.get_edit_text()
        self.entrybox.set_edit_text(u'')     # Erase entrybox

        # Make sure we're not sending nothing.
        if any([not string_to_send, string_to_send == '',
                string_to_send.isspace()]): 
            return

        # Check if there are any commands to run.
        if self._command_parser(string_to_send):
            return
        self._scrollToBottom()  # Scroll textbox to the bottom
        if self.factory.state != Const.STATE_NOT_CONNECTED:
            self.factory.line.send_data(string_to_send)

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
            # self.factory.stop_reactor()
            raise urwid.ExitMainLoop()

        # Help message
        if any((str_to_check == 'help', str_to_check == 'h')):
            self.addString(Messages.gui_help_message)
            return True

        # see docstring of history_printer below to understand this.
        elif str_to_check.isdigit():
            msg = self.msgdb.command_history_printer(int(str_to_check))
            if msg:
                self.entrybox.set_edit_text(msg)
            return True

        #insert more options here
        return False

    

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
        name_tag = ('', '')
        if name:
            self.addClient(name) # The clientName may/may not be
            # known-this call just makes sure-should this call
            # be moved into ClientDB class?
            #self.textbox.insert(tk.END,
                                #''.join(('<', name, '>',)),
                                #("bold", "client_" + name))
            name_tag = (self.getColour(name), ''.join(('<', name, '>',)))
        
        # This next line will be the entry point for implementing
        # bold/colour text highlighting.
        final_string_thing_to_add_to_textbox = [name_tag, ('message', string_to_add)]
        self.listwalker.append(urwid.Text(final_string_thing_to_add_to_textbox))
        self._scrollToBottom()

        # TEMPORARY!
        try:
            self.loop.draw_screen()
        except AttributeError as e:
            pass

    def _scrollToBottom(self):
        """Scroll the textbox to the bottom"""
        self.textbox.set_focus(len(self.listwalker) - 1)
        self.set_focus_on_entrybox()

    def set_focus_on_entrybox(self):
        self.focus_position = 'footer'


class Entrybox(urwid.Edit):
    def __init__(self, msgdb):
        self.msgdb = msgdb
        super(Entrybox, self).__init__(caption = u'Message: ')

    def keypress(self, size, key):
        if key in ('up', 'down'):
            self._getNextOldMsg
        else:
            super(Entrybox, self).keypress(size, key)

    def _getNextOldMsg(self, key):
        if key in ('Up', 'up' 'Down', 'down'):
            res = self.msgdb.getNextOldMsg(event.keysym,
                                        self.entrybox.get())
        else:
            return
        if res == -1:
            return
        self.set_edit_text(res)


class MessageDB(object):
    """
    This class holds all messages in the textbox on screen
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
        """
        Prints out one of the last messages received in the entrybox.
        e.g. if index is 1, then the last message received is printed.
        if index is 2, the second-to-last message received is printed.
        """
        if index > len(self.msgs) or index < 1:
            return
        msg_to_print = self.msgs[-index]
        return msg_to_print

    def getNextOldMsg(self, event, curr_msg):
        """
        This takes in a string, either 'Up' or 'Down',
        and returns some corresponding previous message."""
        if event in ('Down', 'down'):
            if -len(self.msgs) > self.curr_hist_msg or self.curr_hist_msg >= 0:
                return -1
            self.curr_hist_msg += 1
        elif event in ('Up', 'up'):
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
    """
    Holds a list of all the people currently in the
    chatroom we're connnected to, and for each person,
    we have a corresponding colour"""
    def __init__(self):
        # Create a dict to hold the names of all the clients
        # and their corresponding colour. If they don't yet
        # have a colour, then this is ''.
        self.db = {}
        self.colours = PALETTE_COLOURS

    def addClients(self, *args, **kwargs):
        "Adds a list of clients, by repeatedly callling addClient."
        for client in args:
            self.addClient(client)
        for client in kwargs.values():
            self.addClient(client)

    def addClient(self, new_name):
        """
        Adds new_name to the database of clients, making sure there's
        no duplicates. Then, a tag is created for new_name ie a colour
        is given to it. Then, whenever we get messages from new_name,
        we can colour their name in the colour we've assigned to them.
        """
        if new_name in self.db:
            return

        self.db[new_name] = ''

        flat_name = new_name.lower()
        # First, we try to see if new_name matches any of the available
        # colours, and if it does, then it's given that colour.
        for e, entry in enumerate(self.colours):
            if flat_name in entry and entry not in self.db.values():
                self.db[new_name] = entry
                return
        for entry in self.colours:
            if entry not in self.db.values():
                self.db[new_name] = entry
                return
        self.db[new_name] = random.choice(self.colours)
        return

    def removeClient(self, name_to_delete):
        del self.db[name_to_delete]

    def changeClientName(self, old_name, new_name):
        self.removeClient(old_name)
        self.addClient(new_name)

    def getColour(self, name):
        return self.db[name]
