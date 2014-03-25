# This file implements the Tkinter GUI
#!/usr/bin/env python
# -*- coding: utf-8 -*-

#Tkinter related imports
import Tkinter as tk
import ScrolledText
import ttk
import tkFont

from twisted.internet import tksupport

#These are messages to display to the user
import ishyChat.Utils.Messages as Messages

import ishyChat.Client.Networking as Networking

#import the encryption/decryption stuff-seeing if I can remove this
#import ishyChat.Utils.Encryptor as Encryptor

# All the allowed Tkinter colours for printing coloured text
COLOURS = ['snow', 'ghost white', 'white smoke', 'gainsboro', 'floral white', 'old lace',
    'linen', 'antique white', 'papaya whip', 'blanched almond', 'bisque', 'peach puff',
    'navajo white', 'lemon chiffon', 'mint cream', 'azure', 'alice blue', 'lavender',
    'lavender blush', 'misty rose', 'dark slate gray', 'dim gray', 'slate gray',
    'light slate gray', 'gray', 'light grey', 'midnight blue', 'navy', 'cornflower blue', 'dark slate blue',
    'slate blue', 'medium slate blue', 'light slate blue', 'medium blue', 'royal blue',  'blue',
    'dodger blue', 'deep sky blue', 'sky blue', 'light sky blue', 'steel blue', 'light steel blue',
    'light blue', 'powder blue', 'pale turquoise', 'dark turquoise', 'medium turquoise', 'turquoise',
    'cyan', 'light cyan', 'cadet blue', 'medium aquamarine', 'aquamarine', 'dark green', 'dark olive green',
    'dark sea green', 'sea green', 'medium sea green', 'light sea green', 'pale green', 'spring green',
    'lawn green', 'medium spring green', 'green yellow', 'lime green', 'yellow green',
    'forest green', 'olive drab', 'dark khaki', 'khaki', 'pale goldenrod', 'light goldenrod yellow',
    'light yellow', 'yellow', 'gold', 'light goldenrod', 'goldenrod', 'dark goldenrod', 'rosy brown',
    'indian red', 'saddle brown', 'sandy brown',
    'dark salmon', 'salmon', 'light salmon', 'orange', 'dark orange',
    'coral', 'light coral', 'tomato', 'orange red', 'red', 'hot pink', 'deep pink', 'pink', 'light pink',
    'pale violet red', 'maroon', 'medium violet red', 'violet red',
    'medium orchid', 'dark orchid', 'dark violet', 'blue violet', 'purple', 'medium purple',
    'thistle', 'snow2', 'snow3',
    'snow4', 'seashell2', 'seashell3', 'seashell4', 'AntiqueWhite1', 'AntiqueWhite2',
    'AntiqueWhite3', 'AntiqueWhite4', 'bisque2', 'bisque3', 'bisque4', 'PeachPuff2',
    'PeachPuff3', 'PeachPuff4', 'NavajoWhite2', 'NavajoWhite3', 'NavajoWhite4',
    'LemonChiffon2', 'LemonChiffon3', 'LemonChiffon4', 'cornsilk2', 'cornsilk3',
    'cornsilk4', 'ivory2', 'ivory3', 'ivory4', 'honeydew2', 'honeydew3', 'honeydew4',
    'LavenderBlush2', 'LavenderBlush3', 'LavenderBlush4', 'MistyRose2', 'MistyRose3',
    'MistyRose4', 'azure2', 'azure3', 'azure4', 'SlateBlue1', 'SlateBlue2', 'SlateBlue3',
    'SlateBlue4', 'RoyalBlue1', 'RoyalBlue2', 'RoyalBlue3', 'RoyalBlue4', 'blue2', 'blue4',
    'DodgerBlue2', 'DodgerBlue3', 'DodgerBlue4', 'SteelBlue1', 'SteelBlue2',
    'SteelBlue3', 'SteelBlue4', 'DeepSkyBlue2', 'DeepSkyBlue3', 'DeepSkyBlue4',
    'SkyBlue1', 'SkyBlue2', 'SkyBlue3', 'SkyBlue4', 'LightSkyBlue1', 'LightSkyBlue2',
    'LightSkyBlue3', 'LightSkyBlue4', 'SlateGray1', 'SlateGray2', 'SlateGray3',
    'SlateGray4', 'LightSteelBlue1', 'LightSteelBlue2', 'LightSteelBlue3',
    'LightSteelBlue4', 'LightBlue1', 'LightBlue2', 'LightBlue3', 'LightBlue4',
    'LightCyan2', 'LightCyan3', 'LightCyan4', 'PaleTurquoise1', 'PaleTurquoise2',
    'PaleTurquoise3', 'PaleTurquoise4', 'CadetBlue1', 'CadetBlue2', 'CadetBlue3',
    'CadetBlue4', 'turquoise1', 'turquoise2', 'turquoise3', 'turquoise4', 'cyan2', 'cyan3',
    'cyan4', 'DarkSlateGray1', 'DarkSlateGray2', 'DarkSlateGray3', 'DarkSlateGray4',
    'aquamarine2', 'aquamarine4', 'DarkSeaGreen1', 'DarkSeaGreen2', 'DarkSeaGreen3',
    'DarkSeaGreen4', 'SeaGreen1', 'SeaGreen2', 'SeaGreen3', 'PaleGreen1', 'PaleGreen2',
    'PaleGreen3', 'PaleGreen4', 'SpringGreen2', 'SpringGreen3', 'SpringGreen4',
    'green2', 'green3', 'green4', 'chartreuse2', 'chartreuse3', 'chartreuse4',
    'OliveDrab1', 'OliveDrab2', 'OliveDrab4', 'DarkOliveGreen1', 'DarkOliveGreen2',
    'DarkOliveGreen3', 'DarkOliveGreen4', 'khaki1', 'khaki2', 'khaki3', 'khaki4',
    'LightGoldenrod1', 'LightGoldenrod2', 'LightGoldenrod3', 'LightGoldenrod4',
    'LightYellow2', 'LightYellow3', 'LightYellow4', 'yellow2', 'yellow3', 'yellow4',
    'gold2', 'gold3', 'gold4', 'goldenrod1', 'goldenrod2', 'goldenrod3', 'goldenrod4',
    'DarkGoldenrod1', 'DarkGoldenrod2', 'DarkGoldenrod3', 'DarkGoldenrod4',
    'RosyBrown1', 'RosyBrown2', 'RosyBrown3', 'RosyBrown4', 'IndianRed1', 'IndianRed2',
    'IndianRed3', 'IndianRed4', 'sienna1', 'sienna2', 'sienna3', 'sienna4', 'burlywood1',
    'burlywood2', 'burlywood3', 'burlywood4', 'wheat1', 'wheat2', 'wheat3', 'wheat4', 'tan1',
    'tan2', 'tan4', 'chocolate1', 'chocolate2', 'chocolate3', 'firebrick1', 'firebrick2',
    'firebrick3', 'firebrick4', 'brown1', 'brown2', 'brown3', 'brown4', 'salmon1', 'salmon2',
    'salmon3', 'salmon4', 'LightSalmon2', 'LightSalmon3', 'LightSalmon4', 'orange2',
    'orange3', 'orange4', 'DarkOrange1', 'DarkOrange2', 'DarkOrange3', 'DarkOrange4',
    'coral1', 'coral2', 'coral3', 'coral4', 'tomato2', 'tomato3', 'tomato4', 'OrangeRed2',
    'OrangeRed3', 'OrangeRed4', 'red2', 'red3', 'red4', 'DeepPink2', 'DeepPink3', 'DeepPink4',
    'HotPink1', 'HotPink2', 'HotPink3', 'HotPink4', 'pink1', 'pink2', 'pink3', 'pink4',
    'LightPink1', 'LightPink2', 'LightPink3', 'LightPink4', 'PaleVioletRed1',
    'PaleVioletRed2', 'PaleVioletRed3', 'PaleVioletRed4', 'maroon1', 'maroon2',
    'maroon3', 'maroon4', 'VioletRed1', 'VioletRed2', 'VioletRed3', 'VioletRed4',
    'magenta2', 'magenta3', 'magenta4', 'orchid1', 'orchid2', 'orchid3', 'orchid4', 'plum1',
    'plum2', 'plum3', 'plum4', 'MediumOrchid1', 'MediumOrchid2', 'MediumOrchid3',
    'MediumOrchid4', 'DarkOrchid1', 'DarkOrchid2', 'DarkOrchid3', 'DarkOrchid4',
    'purple1', 'purple2', 'purple3', 'purple4', 'MediumPurple1', 'MediumPurple2',
    'MediumPurple3', 'MediumPurple4', 'thistle1', 'thistle2', 'thistle3', 'thistle4',
    'gray1', 'gray2', 'gray3', 'gray4', 'gray5', 'gray6', 'gray7', 'gray8', 'gray9', 'gray10',
    'gray11', 'gray12', 'gray13', 'gray14', 'gray15', 'gray16', 'gray17', 'gray18', 'gray19',
    'gray20', 'gray21', 'gray22', 'gray23', 'gray24', 'gray25', 'gray26', 'gray27', 'gray28',
    'gray29', 'gray30', 'gray31', 'gray32', 'gray33', 'gray34', 'gray35', 'gray36', 'gray37',
    'gray38', 'gray39', 'gray40', 'gray42', 'gray43', 'gray44', 'gray45', 'gray46', 'gray47',
    'gray48', 'gray49', 'gray50', 'gray51', 'gray52', 'gray53', 'gray54', 'gray55', 'gray56',
    'gray57', 'gray58', 'gray59', 'gray60', 'gray61', 'gray62', 'gray63', 'gray64', 'gray65',
    'gray66', 'gray67', 'gray68', 'gray69', 'gray70', 'gray71', 'gray72', 'gray73', 'gray74',
    'gray75', 'gray76', 'gray77', 'gray78', 'gray79', 'gray80', 'gray81', 'gray82', 'gray83',
    'gray84', 'gray85', 'gray86', 'gray87', 'gray88', 'gray89', 'gray90', 'gray91', 'gray92',
    'gray93', 'gray94', 'gray95', 'gray97', 'gray98', 'gray99']



class Application(tk.Tk):
    """This is the main application class holding the chat client.

    All other classes are instantiated within this one."""
    def __init__(self, address, port):
        tk.Tk.__init__(self)
        self.protocol('WM_DELETE_WINDOW', Networking.stopReactor)
        self.wm_title("ishyChat")
        
        #Set up application
        self.frame = Frame(self)
        self.frame.pack(fill = tk.BOTH, expand = 1)
        tksupport.install(self)
        
        #Set up factory
        self.factory = Networking.Factory()
        
        #Link the two together
        self.frame.factory = self.factory
        self.factory.app = self.frame
        
        Networking.runReactor(address, port, self.factory)


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
            Networking.stopReactor()
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
