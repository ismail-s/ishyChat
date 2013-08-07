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
"""This module contains some functions that either make dicts and
turn them into strings, or take strings and turn them back into dicts."""
import json

def packUp(dict_to_pack):
    return json.dumps(dict_to_pack)

def packDown(string_to_unpack):
    return json.loads(string_to_unpack)

def makeDict(msg = '', iv = None, metadata = None, name = None):
    if not metadata:
        metadata = []
    return {'message': msg,
            'iv': iv,
            'metadata': metadata,
            'name': name}

def makeDictAndPack(msg = '', iv = None, metadata = None, name = None):
    return packUp(makeDict(msg, iv, metadata, name))

if __name__ == '__main__':
    test = makeDictAndPack(msg = 'test', metadata = ['test'], name = 'client')
    print test
