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
#Base64 allows us to convert binary strings into an ASCII format, that
#doesn't cause any problems.
from base64 import b64encode, b64decode

class Encryptor(object):
    def __init__(self, key):
        self.key = key
        MAX_LEN_OF_KEY = 32
        #Pad the key with hashes so it is 32 bytes long.
        if len(self.key) < MAX_LEN_OF_KEY:
            self.key = self.key.ljust(MAX_LEN_OF_KEY, '#')
        self.key = self.key[:32]

    def encrypt(self, text):
        iv = Random.new().read(AES.block_size)
        cipher = self._new(iv)
        plaintext = self._padMessage(text)
        return b64encode(iv), b64encode(cipher.encrypt(plaintext))

    def encrypt_ECB(self, text):
        cipher = self._new_ECB()
        plaintext = self._padMessage(text)
        return b64encode(cipher.encrypt(plaintext))

    def decrypt(self, iv, text):
        # We get rid of NULL characters as they mess things up when
        # strings are added in tkinter where the NULL character
        # is seen as a terminator.
        plaintext = self._new(b64decode(iv)).decrypt(b64decode(text))
        return plaintext.replace('\0', '')

    def decrypt_ECB(self, text):
        cipher = self._new_ECB()
        plaintext = cipher.decrypt(b64decode(text))
        return plaintext.replace('\0', '')

    def _padMessage(self, text):
        text_copy = text[:]
        text_len = len(text_copy)
        if text_len % AES.block_size:
            text_copy = text_copy.ljust(\
            AES.block_size * ((text_len / AES.block_size) + 1),'\0')
        return text_copy

    def _new(self, iv):
        return AES.new(self.key, AES.MODE_CBC, iv)
        
    def _new_ECB(self):
        return AES.new(self.key, AES.MODE_ECB)
