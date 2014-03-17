#!/usr/bin/env python
# -*- coding: utf-8 -*-

import ishyChat.Utils.Packer as Packer
"""This file contains various messages that are displayed by the client
(and some other stuff). I thought it would be good to put them together
in one place rather than scattered throughout the code."""

def dictPreprocessor(string, metadata = None):
    """Takes a string and produces a json string
    
    which contains a dict with the string in, along with some other
    stuff."""
    return Packer.makeDictAndPack(msg = string, name = 'client', metadata = metadata)

def tuplePreprocessor(string, name = ''): return (string, name)

start_message = dictPreprocessor("""Hi. Type '/help' for help. Type /warning for the important warning message.""")

warning_message = dictPreprocessor("""Please note that I have no way of knowing if you typed the key correctly. If it was typed incorrectly, then you will quite soon see some mumbo-jumbo text on-screen instead of messages from other users.
All messages are encrypted using the key you entered at the beginning. This key should have been the same one everyone else is using, otherwise the chat won't work. The key should have been ideally 32 characters long to make it more secure.
Also note that the server only receives an encrypted version of the client's names.
The server will now speak to you, so please follow its instructions.

""")

gui_help_message = tuplePreprocessor("""Help
ishyChat is a very simple minimalistic chat client. You make sure that one person has fired up the server, and then everyone else starts their clients (this thing) and gives it the address and pre-shared key (for encryption).
Commands
Commands are prefixed with a '/'.
/q        Quit the program.
/quit     Same as /q
/test     This prints out a test string
/h        This prints out this help message
/help     Same as /h
/warning  Prints the warning message.
/ping     Prints the roundtime between you and the server.
/[number] This one is a bit of a funny one. You give it a number, and it displays that message in the entrybox. For example, typing /1 would print the last received message in the entrybox. This facilitates resending a recently received message, or quoting what someone else said.
""")

ping_message = dictPreprocessor("", ['ping'])


starting_conn = tuplePreprocessor("Started to connect.")
conn_lost = tuplePreprocessor("Connection lost. Attempting to re-establish connection.")
conn_failed = tuplePreprocessor("Connection failed. Attempting to re-establish connection.")
