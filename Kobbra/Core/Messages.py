# -*- coding: utf-8 -*-
"""
This module implements the Kobbra network messages
"""
from hashlib import sha256

from Kobbra.Utils.Crypto import MessageCrypto, Base64Encoding
from Kobbra.Utils.Log import ConsoleLogger

class Response(object):
    """
    Response composition object
    """

    def __init__(self, managers):
        self.managers = managers
        self.c = MessageCrypto()

    def hello(self):
        """
        HELLO response
        """
        msg = self.c.writeheader(0)
        msg += self.c.geteom()
        ConsoleLogger.log("DBG","ResponseEvent: " + msg.decode('utf-8'))
        return msg

    def cryptoparams(self):
        """
        CRYPTO PARAMS (277) response 
        """
        msg = self.c.writeheader(277)
        msg += self.c.geteom()
        ConsoleLogger.log("DBG","ResponseEvent: " + msg.decode('utf-8'))
        return msg
    
    def secretkey(self):
        """
        SECRET KEY (1) response 
        """
        msg = self.c.writeheader(1)
        msg += self.c.geteom()
        ConsoleLogger.log("DBG","ResponseEvent: " + msg.decode('utf-8'))
        return msg

    def sessionparams(self):
        """
        SESSION PARAMS (257) response
        """
        # TODO: recover some of these params from DB
        params = {
            #0:0, #COPPA enabled if value 1, COPPA enforced if value > 1
            1:1, #Voucher enabled
            2:0, #Require parent email enabled
            3:0, #Send parent email
            4:0, #Allow direct mail enabled
            5:"", #Date format string
            6:0, #Partner integration enabled
            7:1, #Allow profile editing enabled
            8:"", #Tracking header
            9:0 #Tutorial enabled
        }

        #OK so this one was tricky to crack
        msg = self.c.writeheader(257)

        #First we add a VL64 params size
        msg += self.c.getint(len(params))

        #Then for each param we should first add the paramID in VL64
        #then the param value always respecting the param type (VL64 for int, string \x02 for string)
        for key, value in params.items():
            msg += self.c.getint(key)
            if type(value) == int:
                msg += self.c.getint(value)
            else:
                msg += self.c.writestring(value)

        msg += self.c.geteom()
        ConsoleLogger.log("DBG","ResponseEvent: " + msg.decode('utf-8'))
        return msg

    def availablesets(self):
        """
        AVAILABLE SETS (8) response
        """
        configman = self.managers.Config()
        msg = self.c.writeheader(8)
        msg += b"[" + bytearray(configman.GetDb("Figure.Data.Default"), 'utf-8') + b"]"
        msg += self.c.geteom()
        ConsoleLogger.log("DBG","ResponseEvent: " + msg.decode('utf-8'))
        return msg

    def localisederror(self, error):
        """
        LOCALISED ERROR (33) response
        """
        msg = self.c.writeheader(33)
        msg += bytearray(error, 'utf-8')
        msg += self.c.geteom()
        ConsoleLogger.log("DBG","ResponseEvent: " + msg.decode('utf-8'))
        return msg
    
    def login(self):
        msg = self.c.writeheader(3)
        msg += self.c.geteom()
        ConsoleLogger.log("DBG","ResponseEvent: " + msg.decode('utf-8'))
        return msg

    def userobject(self):
        player = self.managers.User().session.player
        msg = self.c.writeheader(5)
        msg += self.c.writestring(str(player.id)) #id
        msg += self.c.writestring(player.name) #name
        msg += self.c.writestring(player.figure) #figure
        msg += self.c.writestring(player.sex) #sex
        msg += self.c.writestring(player.motto) #motto
        msg += self.c.getint(player.tickets) #tickets
        msg += self.c.writestring(player.pfigure) #poolfigure
        msg += self.c.getint(player.films) #films
        msg += self.c.geteom()
        ConsoleLogger.log("DBG","ResponseEvent: " + msg.decode('utf-8'))
        return msg

    def creditbalance(self):
        player = self.managers.User().session.player
        msg = self.c.writeheader(6)
        msg += self.c.writestring(str(player.credits) + '.0')
        msg += self.c.geteom()
        ConsoleLogger.log("DBG","ResponseEvent: " + msg.decode('utf-8'))
        return msg

    def availbadges(self):
        # TODO: Fix badges!!!
        msg = self.c.writeheader(229)
        msg += self.c.getint(0) #numbadges
        msg += self.c.getint(0) #badgeslot?
        msg += self.c.getint(0) #showbadge 0/1
        msg += self.c.geteom()
        ConsoleLogger.log("DBG","ResponseEvent: " + msg.decode('utf-8'))
        return msg
    
    def date(self):
        msg = self.c.writeheader(163)
        msg += self.c.getshortdate()
        msg += self.c.geteom()
        ConsoleLogger.log("DBG","ResponseEvent: " + msg.decode('utf-8'))
        return msg

    def nameapproval(self, approval):
        msg = self.c.writeheader(36)
        msg += self.c.getint(approval)
        msg += self.c.geteom()
        ConsoleLogger.log("DBG","ResponseEvent: " + msg.decode('utf-8'))
        return msg

    def passapproval(self, approval):
        msg = self.c.writeheader(282)
        msg += self.c.getint(approval)
        msg += self.c.geteom()
        ConsoleLogger.log("DBG","ResponseEvent: " + msg.decode('utf-8'))
        return msg

    def mailapproval(self):
        msg = self.c.writeheader(271)
        msg += self.c.geteom()
        ConsoleLogger.log("DBG","ResponseEvent: " + msg.decode('utf-8'))
        return msg
    
    def nouserrooms(self, name):
        msg = self.c.writeheader(57)
        msg += self.c.writestring(name)
        msg += self.c.geteom()
        return msg
    
    def goroom(self, rid, rname):
        msg = self.c.writeheader(59)
        msg += bytearray(str(rid), 'utf-8')
        msg += b'\x13'
        msg += bytearray(rname, 'utf-8')
        msg += self.c.geteom()
        return msg
    
    def roomlist(self, rooms):
        msg = self.c.writeheader(16)
        for room in rooms:
            msg += bytearray(str(room[0]), 'utf-8')
            msg += b'\x09'
            msg += bytearray(room[3], 'utf-8')
            msg += b'\x09'
            msg += bytearray(room[1], 'utf-8')
            msg += b'\x09'
            msg += bytearray('0', 'utf-8')
            msg += b'\x09'
            msg += bytearray('x', 'utf-8')
            msg += b'\x09'
            msg += bytearray('0', 'utf-8')
            msg += b'\x09'
            msg += bytearray('20', 'utf-8')
            msg += b'\x09'
            msg += bytearray('null', 'utf-8')
            msg += b'\x09'
            msg += bytearray('kk', 'utf-8')
            msg += b'\x09'
            msg += b'\x13'
        msg += self.c.geteom()
        return msg