#!/usr/bin/env python
# -*- coding: utf-8 -*-

import ishyChat.Utils.Packer as Packer
"""This file contains various messages that are displayed by the client
(and some other stuff). I thought it would be good to put them together
in one place rather than scattered throughout the code."""

def dictPreprocessor(string = '', metadata = None):
    """Takes a string and produces a json string
    
    which contains a dict with the string in, along with some other
    stuff."""
    return Packer.makeDictAndPack(msg = string, name = 'client', metadata = metadata)

def tuplePreprocessor(string, name = ''): return (string, name)

start_message = dictPreprocessor("""Hi. Type '/help' for help.""")

warning_message = dictPreprocessor("""Warning: This connection hopefully will be running over HTTPS. However, the server that everyone connects to can (and may) read all the messages. Therefore, make sure you know and trust the person who is running the server.

""")

gui_help_message = tuplePreprocessor("""Help
ishyChat is a very simple minimalistic chat client. You make sure that one person has fired up the server, and then everyone else starts their clients (this thing) and gives it the address and port.
Commands
--------
Commands are prefixed with a '/'.
/q\t\tQuit the program.
/quit\t\tSame as /q
/h\t\tThis prints out this help message
/help\t\tSame as /h
/list\t\tPrints a list of all the people currently in the chatroom.
/listusers\t\tSame as /list
/warning\t\tPrints the warning message.
/ping\t\tPrints the roundtime between you and the server.
/[number]\t\t[number] must be >=1. Hard to explain what this does-just try it out.
Also, try pressing the up and down keys whilst the cursor is in the entrybox (where you type messages).
""")

ping_message = dictPreprocessor(metadata = {'ping': None})
getusers_message = dictPreprocessor(metadata = {'getusers': None})

starting_conn = tuplePreprocessor("Started to connect.")
conn_lost = tuplePreprocessor("Connection lost. Attempting to re-establish connection.")
conn_failed = tuplePreprocessor("Connection failed. Attempting to re-establish connection.")
