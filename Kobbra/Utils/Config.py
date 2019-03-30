# -*- coding: utf-8 -*-
"""
Configuration Utility module for Kobbra server
"""
from os import path

class IniConfiguration(object):
    """
    Kobbra ini configuration file manager object
    """
    def __init__(self, configPath):
        self.__path = configPath
        try:
            self.cfg = self.__load() # RAII!
        except IOError:
            self.store(self.__getconfigdefaults())

    def __load(self):
        """
        Loads a Kobbra configuration as dictionary
        """
        with open(self.__path, "r") as cfg:
            cfglines = cfg.readlines()

        cfgdict = dict()

        for line in cfglines:
            pair = line.split("=")
            cfgdict[pair[0].strip()] = pair[1].strip()

        return cfgdict

    def store(self, cfgdict):
        """
        Stores back a Kobbra configuration as dictionary
        """
        with open(self.__path, "w+") as cfg:
            for key, value in cfgdict.items():
                cfg.write(key + '=' + value + '\n')

    def __getconfigdefaults(self):
        """
        Default server configuration
        """
        defcfg = dict()
        
        #defcfg["version"] = "14"
        defcfg["bind"] = "127.0.0.1"
        defcfg["bind.remote"] = ""
        defcfg["loglevel"] = "5"
        defcfg["info.port"] = "12321"
        defcfg["mus.port"] = "12322"
        defcfg["db.file"] = "Kobbra.db"
        defcfg["db.script"] = "Kobbra.sql"
        return defcfg

