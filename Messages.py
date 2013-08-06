#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  untitled.py
#  
#  Copyright 2013 ssuleman <ssuleman@ubuntu>
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
#  
import base64, json
"""This file contains various messages that are displayed by the client
(and some other stuff). I thought it would be good to put them together
in one place rather than scattered throughout the code."""

def preprocessor(string, metadata = None):
    """Takes a string and produces a base64 encoded json string
    
    which contains a dict with the string in, along with some other
    stuff."""
    std_dict = {'message': None, 'name': 'client', 'metadata': []}
    if metadata:
        std_dict['metadata'] = metadata
    std_dict['message'] = string
    return base64.b64encode(json.dumps(std_dict))


start_message = preprocessor("""Hi. Type '/help' for help. Type /warning for the important warning message.""")

warning_message = preprocessor("""Please note that I have no way of knowing if you typed the key correctly. If it was typed incorrectly, then you will quite soon see some mumbo-jumbo text on-screen instead of messages from other users.
All messages are encrypted using the key you entered at the beginning. This key should have been the same one everyone else is using, otherwise the chat won't work. The key should have been ideally 32 characters long to make it more secure.
Also note that the server only receives an encrypted version of the client's names.
The server will now speak to you, so please follow its instructions.

""")

help_message = preprocessor("""Help
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

ping_message = preprocessor("", ['ping'])

test_message = preprocessor('Testing...')

starting_conn = preprocessor("Started to connect.")
conn_lost = preprocessor("Connection lost. Attempting to re-establish connection.")
conn_failed = preprocessor("Connection failed. Attempting to re-establish connection.")
