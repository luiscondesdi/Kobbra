# -*- coding: utf-8 -*-
"""
This module implements the Kobbra management engine
"""
from hashlib import sha256
from gevent.lock import Semaphore
from gevent.local import local

from Kobbra.Utils.Log import ConsoleLogger
from Kobbra.Utils.DataAccess import Database
from Kobbra.Utils.Config import IniConfiguration
from Kobbra.Utils.Crypto import MessageCrypto, Base64Encoding

from Kobbra.Core.Model import Player

class ManagerFactory(object):
    """
    Manager intercom system
    """

    def __init__(self):
        self.__user = None
        self.__db = None
        self.__cfg = None
    
    def User(self):
        if self.__user == None:
            self.__user = UserManager(self)
        return self.__user
    
    def Database(self):
        if self.__db == None:
            self.__db = DatabaseManager(self)
        return self.__db
    
    def Config(self):
        if self.__cfg == None:
            self.__cfg = ConfigManager(self)
        return self.__cfg

class ConfigManager(object):
    """
    Configuration management object
    """

    def __init__(self, managers):
        self.managers = managers
        self.__ini = IniConfiguration("Kobbra/Kobbra.ini")
        dbman = self.managers.Database()
        self.__db = dbman.Config()
    
    def TryReloadDb(self):
        if self.__db == None:
            dbman = self.managers.Database()
            self.__db = dbman.Config()

    def GetIni(self, key):
        return self.__ini.cfg[key]
    
    def GetDb(self, key):
        return self.__db[key]


class DatabaseManager(object):
    """
    Database management object
    """

    def __init__(self, managers):
        self.managers = managers
        self.__db = None
    
    def Connect(self, path):
        if self.__db == None:
            self.__db = Database(path)
            if self.__db.emptydb:
                cfgman = self.managers.Config()
                self.__db.runscript(cfgman.GetIni("db.script"))
            self.managers.Config().TryReloadDb()

    def Close(self):
        if self.__db != None:
            self.__db.close()
            self.__db = None

    def CheckLogin(self, name, passwd):
        if self.__db == None:
            return None

        result = self.__db.runsentence("SELECT * FROM 'Users' WHERE Name=? AND Pass=?;", [name, passwd])

        return result
    
    def FindUser(self, name):
        if self.__db == None:
            return None
        
        return len(self.__db.runsentence("SELECT * FROM 'Users' WHERE Name=?;", [name])) > 0

    def GetPurse(self, name):
        if self.__db == None:
            return None
        
        return self.__db.runsentence("SELECT * FROM 'Purse' WHERE User=?;", [name])
    
    def Register(self, name, passwd, figure, sex, mail, birthday):
        if self.__db == None:
            pass
        
        self.__db.runsentence("INSERT INTO Users (Name,Pass,Figure,Sex,Mail,Birthday) VALUES (?,?,?,?,?,?);", [name, passwd, figure, sex, mail, birthday])
        ConsoleLogger.log("INF","Session: Register " +name + " born " + birthday + " with mail " + mail)
    
    def Config(self):
        if self.__db == None:
            return None
        
        return dict(self.__db.runsentence("SELECT * FROM 'Settings';"))
    
    def CreateRoom(self, player, floor, name, model, door, sowner):
        if self.__db == None:
            return None
        
        self.__db.runsentence("INSERT INTO 'Room' (User,Floor,Name,Model,Door,ShowOwner) VALUES(?,?,?,?,?,?);", [player,floor,name,model,door,sowner])
        res = self.__db.runsentence("SELECT Id FROM Room WHERE User=? AND Name=?;", [player,name])
        return res[0][0] # Return room ID as it is very important for the client
    
    def PlayerRooms(self, name):
        if self.__db == None:
            return None
        
        return self.__db.runsentence("SELECT * FROM Room WHERE User=?;", [name])

class UserManager(object):
    """
    User/player management object
    """

    def __init__(self, managers):
        self.managers = managers
        
        self.c = MessageCrypto()
        self.lock = Semaphore()
        
        self.__players = []
        self.__cfg = self.managers.Database().Config()
        
        # Init greenlet local
        self.session = local()
        self.session.player = None
    
    def __AssignId(self, player):
        """
        This method creates a new id within the player registry
        """
        with self.lock:
            self.__players.append(player)
            return self.__players.index(player)
        return None
    
    def isconnected(self, name):
        for p in self.__players:
            if p.name == name:
                return True
        return False
            
    def login(self, name, passwd):
        dbman = self.managers.Database() 
        users = dbman.CheckLogin(name, passwd)

        if len(users) > 0:
            player = Player(users[0])
            player.id = self.__AssignId(player)

            purses = dbman.GetPurse(player.name)
            player.credits = purses[0][1]
            player.tickets = purses[0][2]
            player.films = purses[0][3]
            
            self.session.player = player
            ConsoleLogger.log("INF", "Player " + name + " logged in")
            return True

        return False

    def checkname(self, name):
        cfgman = self.managers.Config()

        dbman = self.managers.Database()
        exists = dbman.FindUser(name)

        maxl = int(cfgman.GetDb('User.Name.MaxLength'))
        minl = int(cfgman.GetDb('User.Name.MinLength'))
        
        approval = 0

        if exists:
            approval = 4 # Username already exists
        elif len(name) < minl:
            approval = 2 # Name is too short
        elif len(name) > maxl:
            approval = 1 # Name is too long
        #else:
        # TODO: test if name contains any unallowed chars, then set approval to 3
        return approval
    
    def checkpass(self, name, passwd):
        cfgman = self.managers.Config()

        maxpassl = int(cfgman.GetDb('User.Pass.MaxLength'))
        minpassl = int(cfgman.GetDb('User.Pass.MinLength'))

        approval = 0

        if name == passwd:
            approval = 5
        elif len(passwd) < minpassl:
            approval = 1
        elif len(passwd) > maxpassl:
            approval = 2
        #else:
        # TODO: test if name contains any unallowed chars, then set approval to 3
        return approval
