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

import base64

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
        plaintext = text[:]
        plaintext = self._padMessage(plaintext)
        return base64.b64encode(iv), base64.b64encode(cipher.encrypt(plaintext))

    def encrypt_ECB(self, text):
        cipher = AES.new(self.key, AES.MODE_ECB)
        plaintext = text[:]
        plaintext = self._padMessage(plaintext)
        return base64.b64encode(cipher.encrypt(plaintext))

    def decrypt(self, iv, text):
        #text_start = text.find(' ') + 1
        #name = text[:text_start]
        #iv = text[text_start: text_start + AES.block_size]
        #cipher = self._new(iv)
        #plaintext = cipher.decrypt(text[text_start + AES.block_size:])
        #while plaintext[-1] == '#':
            #plaintext = plaintext[:-1]
        #return name + plaintext

        #name_start = text.find('<') + 1
        #name_end = text.find('> ', name_start)
        #name = self._decrypt_ECB(text[name_start: name_end])
        #msg_start = name_end + 2  # msgs look like '<name> msg here'
        #msg = self._decrypt(text[msg_start:])
        # We get rid of NULL characters as they mess things up when
        # strings are added in tkinter where the NULL character
        # is seen as a terminator.
        return self._new(base64.b64decode(iv)).decrypt(base64.b64decode(text)).replace('\0', '')

    #def _decrypt(self, text):
        #iv = text[:AES.block_size]
        #cipher = self._new(iv)
        #plaintext = cipher.decrypt(text[AES.block_size:])
        #while plaintext[-1] == '#':
            #plaintext = plaintext[:-1]
        #return plaintext

    def decrypt_ECB(self, text):
        cipher = AES.new(self.key, AES.MODE_ECB)
        plaintext = cipher.decrypt(base64.b64decode(text))
        #while plaintext[-1] == '#':
            #plaintext = plaintext[:-1]
        return plaintext.replace('\0', '')

    def _padMessage(self, text):
        text_copy = text[:]
        #while len(text_copy) % AES.block_size or len(text_copy) < AES.block_size:
            #text_copy += '#'
        text_len = len(text_copy)
        if text_len % AES.block_size:
            text_copy = text_copy.ljust(AES.block_size * ((text_len / AES.block_size) + 1), '\0')
        return text_copy

    def _new(self, iv):
        return AES.new(self.key, AES.MODE_CBC, iv)
