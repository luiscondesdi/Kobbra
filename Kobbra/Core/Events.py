# -*- coding: utf-8 -*-
"""
This module implements server gevent handling objects
"""
from hashlib import sha256

from Kobbra.Utils.Log import ConsoleLogger
from Kobbra.Utils.Crypto import MessageCrypto, Base64Encoding
from Kobbra.Core.Messages import Response

class EventDispatcher(object):

    def __init__(self, managers, connection):
        self.managers = managers
        self.command = None
        self.connection = connection
        self.res = Response(managers)
        self.c = MessageCrypto()

        self.reqdict = {
            206:self.initcrypto,
            202:self.generatekey,
            4:self.trylogin,
            756:self.trylogin,         
            7:self.getinfo,
            8:self.getcredits,
            16:self.userrooms,
            157:self.getavailbadges,
            49:self.getdate,
            42:self.approvename,
            203:self.approvepassword,
            197:self.approvemail,
            43:self.register,
            29:self.createroom,
            2002:self.generatekey,
            204:"sso"

        }

        self.resdict = {
            0:self.res.hello,
            277:self.res.cryptoparams,
            1:self.res.secretkey,
            257:self.res.sessionparams,
            8:self.res.availablesets,
            33:self.res.localisederror,
            3:self.res.login,        
            5:self.res.userobject,
            6:self.res.creditbalance,
            229:self.res.availbadges,
            163:self.res.date,
            36:self.res.nameapproval,
            282:self.res.passapproval,
            271:self.res.mailapproval,
            57:self.res.nouserrooms,
            59:self.res.goroom
        }

    def request(self, commandid, msg):
        try:
            self.command = msg[2:]
            self.reqdict[commandid]()
        except KeyError:
            ConsoleLogger.log("EXC", "Session: KeyError raised. Unsupported command id " + str(commandid))

    def response(self, responseid):
        try:
            self.connection.sendall(self.resdict[responseid]())
        except KeyError:
            ConsoleLogger.log("EXC", "Session: KeyError raised. Unsupported response id " + str(responseid))

    def initcrypto(self):
        self.response(277)
    
    def generatekey(self):
        self.response(257)
        self.response(8)

    def trylogin(self):
        name, self.command = self.c.readstring(self.command)
        passwd = self.c.readstring(self.command)
        phash = sha256(passwd[0].encode('utf-8')).hexdigest()

        userman = self.managers.User()
        
        if userman.login(name, phash):    
            self.response(3) 
        else:
            self.res.localisederror("Login incorrect")
    
    def getinfo(self):
        self.response(5)

    def getcredits(self):
        self.response(6)

    def getavailbadges(self):
        self.response(229)
    
    def getdate(self):
        self.response(163)
    
    def approvename(self):
        name, self.command = self.c.readstring(self.command)
        
        userman = self.managers.User()
        approval = userman.checkname(name)

        self.connection.sendall(self.res.nameapproval(approval))
    
    def approvepassword(self):
        name, self.command = self.c.readstring(self.command)
        passwd, self.command = self.c.readstring(self.command)

        userman = self.managers.User()
        approval = userman.checkpass(name, passwd)

        self.connection.sendall(userman.passapproval(approval))

    def approvemail(self):
        # We could check the mail here, but whatever
        self.response(271)
    
    def register(self):
        self.command = self.command[2:] # Param @B
        name, self.command = self.c.readstring(self.command)
        self.command = self.command[2:] # Param @D
        figure, self.command = self.c.readstring(self.command)
        self.command = self.command[2:] # Param @E
        sex, self.command = self.c.readstring(self.command)
        self.command = self.command[4:] # Parameter @F (???)
        self.command = self.command[2:] # Param @G
        mail, self.command = self.c.readstring(self.command)
        self.command = self.command[2:] # Param @H
        birthday, self.command = self.c.readstring(self.command)
        self.command = self.command[9:] # Bool parameters @J (???), @A (Minor 11) and @I (Spam flag)
        self.command = self.command[2:] # Param @C
        passwd, self.command = self.c.readstring(self.command)
        phash = sha256((passwd.encode('utf-8'))).hexdigest()

        userman = self.managers.User()
        userman.register(name, phash, figure, sex, mail, birthday)

    def userrooms(self):
        dbman = self.managers.Database()
        name = self.managers.User().session.player.name
        rooms = dbman.PlayerRooms(name)
        if len(rooms) > 0:
            self.connection.sendall(self.res.roomlist(rooms))
        else:
            self.response(57)
    
    def createroom(self):
        roomstr = "".join(self.command)
        rsettings = roomstr.split('/')
        rsettings.pop(0)

        userman = self.managers.User()
        dbman = self.managers.Database()
        
        name = userman.session.player.name
        rid = dbman.CreateRoom(name, rsettings[0], rsettings[1], rsettings[2], rsettings[3], int(rsettings[4]))
        self.connection.sendall(self.res.goroom(rid, rsettings[1]))