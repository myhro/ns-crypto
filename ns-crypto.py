#!/usr/bin/env python
# -*- coding: utf-8 -*-

import base64
import hashlib
import itertools
import json
import random
import string
import zlib


class Key():
    def __init__(self, key_file=None):
        self.key = None
        self.b64key = None
        if key_file:
            self.key_file = key_file
        else:
            self.key_file = 'key-' + ''.join(random.choice(string.letters + string.digits) for i in xrange(5))
            self.new()

    def get_key(self):
        return self.key

    def new(self):
        self.key = [random.randint(1, 94) for i in xrange(64)]
        self.b64key = base64.b64encode(zlib.compress(json.dumps(self.key)))

    def load(self):
        filebuffer = open(self.key_file)
        self.b64key = filebuffer.readline()
        self.key = json.loads(zlib.decompress(base64.b64decode(self.b64key)))
        filebuffer.close()

    def save(self):
        filebuffer = open(self.key_file, 'w')
        filebuffer.write(self.b64key + '\n')
        filebuffer.close()


class Message():
    def __init__(self, text):
        self.alphabet = string.printable[:-5]
        self.len_alphabet = len(self.alphabet)
        self.message = text

    def decrypt(self, key):
        steps = itertools.cycle(key.get_key())
        plain_chars = []
        for c in self.message:
            crypt_position = self.alphabet.index(c)
            plain_position = (crypt_position - steps.next()) % self.len_alphabet
            plain_chars.append(self.alphabet[plain_position])
        checksum = ''.join(plain_chars[-32:])
        text = ''.join(plain_chars[:-32])
        if hashlib.md5(text).hexdigest() == checksum:
            self.message = text
        return self.message

    def encrypt(self, key):
        checksum = hashlib.md5(self.message).hexdigest()
        plain_text = self.message + checksum
        steps = itertools.cycle(key.get_key())
        encrypted_chars = []
        for c in plain_text:
            plain_position = self.alphabet.index(c)
            crypt_position = (plain_position + steps.next()) % self.len_alphabet
            encrypted_chars.append(self.alphabet[crypt_position])
        self.message = ''.join(encrypted_chars)
        return self.message

    def text(self):
        return self.message


def main():
    enc_key = Key(key_file='crypto.key')
    enc_key.load()
    msg = Message('The book is on the table.')

    print msg.text()
    print msg.encrypt(key=enc_key)
    print msg.decrypt(key=enc_key)

    print '-'

    print msg.text()
    print msg.encrypt(key=enc_key)
    tmp_key = Key()
    print msg.decrypt(key=tmp_key)

if __name__ == '__main__':
    main()
