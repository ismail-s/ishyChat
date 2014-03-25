#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""This module contains some functions that either make dicts and
turn them into strings, or take strings and turn them back into dicts."""
import json

def packUp(dict_to_pack):
    return json.dumps(dict_to_pack)

def packDown(string_to_unpack):
    return json.loads(string_to_unpack)

def makeDict(type = 'text', msg = '', metadata = None, name = None):
    if not metadata:
        metadata = {}
    return {'type': type,
            'message': msg,
            'metadata': metadata,
            'name': name}

def makeDictAndPack(type = 'text', msg = '', metadata = None, name = None):
    return packUp(makeDict(type, msg, metadata, name))

if __name__ == '__main__':
    test1 = makeDictAndPack(msg = 'test', metadata = {'test': None}, name = 'client')
    test1_corr_ans = {"message": "test", "metadata": {"test": null}, "name": "client"}
    print 'Test 1 out of 1:'
    print 'Output', test1
    print 'Test',
    print 'passed' if json.loads(test1) == test1_corr_ans else 'failed'
