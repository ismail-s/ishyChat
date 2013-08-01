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
#

#Encryption/decryption imports
from Crypto import Random
from Crypto.Cipher import AES

class Encryptor(object):
    def __init__(self, key):
        self.key = key
        while len(self.key) < 32:
            self.key = self.key + '#'
        self.key = self.key[:32]
        #print self.key, len(self.key)

    def encrypt(self, text):
        iv = Random.new().read(AES.block_size)
        cipher = self._new(iv)
        text_to_encrypt = text[:]
        while len(text_to_encrypt) % 16 or len(text_to_encrypt) < 16:
            text_to_encrypt += '#'
        return iv+cipher.encrypt(text_to_encrypt)

    def decrypt(self, text):
        #text_start = text.find(' ') + 1
        #name = text[:text_start]
        #iv = text[text_start: text_start + AES.block_size]
        #cipher = self._new(iv)
        #plaintext = cipher.decrypt(text[text_start + AES.block_size:])
        #while plaintext[-1] == '#':
            #plaintext = plaintext[:-1]
        #return name + plaintext
        
        name_start = text.find('<') + 1
        name_end = text.find('>')
        name = self._decrypt(text[name_start: name_end])
        msg_start = name_end + 2  #msgs look like '<name> msg here'
        msg = self._decrypt(text[msg_start:])
        return '<' + name + '> ' + msg
    
    def _decrypt(self, text):
        iv = text[:AES.block_size]
        cipher = self._new(iv)
        plaintext = cipher.decrypt(text[AES.block_size:])
        while plaintext[-1] == '#':
            plaintext = plaintext[:-1]
        return plaintext
    
    def _new(self, iv):
        return AES.new(self.key, AES.MODE_CBC, iv)


