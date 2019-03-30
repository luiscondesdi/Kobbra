# -*- coding: utf-8 -*-
"""
Utility module forspecifies the classes for habbo encoding
"""
from math import floor
import datetime

class MessageCrypto(object):
    """
    Object for handling message crypto
    """

    def __init__(self):
        self.B64 = Base64Encoding()
        self.VL64 = VL64Encoding()

    def writeheader(self, number):
        """
        Method to encode a header message
        """
        return self.B64.encode(int(number), 2)

    def readheader(self, header):
        return self.B64.decode(header)
    
    def getint(self, number):
        """
        Method to encode a signed int
        """
        return self.VL64.encode(number)
    
    def getshortdate(self):
        return bytearray(datetime.datetime.now().strftime("%d.%m.%Y"), 'utf-8')
    
    def writestring(self, string):
        """
        Method to get a string parameter
        """
        #The very old fuse protocol requires a string terminator for parameters
        return bytearray(string, 'utf-8') + b"\x02"
    
    def readstring(self, command):
        stringlen = self.readheader(command[:2])
        name = "".join(command[2:2 + stringlen])
        return name, command[2 + stringlen:]

    def geteom(self):
        """
        Method to get the end of message byte
        """
        return b"\x01"

class Base64Encoding(object):
    """
    Class for FUSE B64 encoding
    """
    
    def encode(self, number, length):
        """
        Encode from int to fuse B64
        """
        res = bytearray(b'')
        for i in range(length):
            k = (length - (i + 1)) * 6
            res.append(0x40 + ((number >> k) & 0x3f))
        
        return res

    def decode(self, data):
        """
        Decode from bytearray fuse B64 to int
        """
        res = 0
        mag = 0
        for c in reversed(data): # Reversed takes care of the endianness :)
            x = ord(c) - 0x40
            if mag > 0:
                x *= int(floor(64**mag))
            res += x
            mag += 1
        return res

class VL64Encoding(object):
    """
    Object for fuse VL64 encoding
    """

    def __init__(self):
        self.max_int_bytes = 6

    def encode(self, number):
        """
        Encode from int to fuse VL64
        """
        res = bytearray(b'')

        i = abs(number)
        sign = 0 if number >= 0 else 4

        firstc = 64 + (i & 3)
        res.append(firstc)
        
        i = i >> 2
        while i != 0:
            res.append(64 + (i & 0x3f))
            i = i >> self.max_int_bytes

        signfc = firstc | len(res) << 3 | sign

        res[0] = signfc

        return res

    def decode(self, data):
        """
        Decode from fuse VL64 to int
        """
        datal = list(data)
        firstc = ord(datal[0])
        datal.pop(0)

        sign = (firstc & 4) == 4

        number = firstc & 3
        shiftam = 2
        shiftin = 1
        for c in datal:
            number = number | (ord(c) & 0x3f) << shiftam
            shiftam = 2 + 6 * shiftin
            shiftin += 1
        
        if sign:
            number *= -1

        return number
