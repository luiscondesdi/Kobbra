# -*- coding: utf-8 -*-
"""
 _____ _____ _____ _____ _____ _____
|  |  |     | __  | __  | __  |  _  |
|    -|  |  | __ -| __ -|    -|     |
|__|__|_____|_____|_____|__|__|__|__|

Kobbra - Python FUSE Server Emulation

"""
import gevent

from Kobbra.Utils.Log import ConsoleLogger
from Kobbra.Core.Mus import MusServer
from Kobbra.Core.Info import InfoServer
from Kobbra.Core.Management import ManagerFactory


class Kobbra(object):
    """
    Main Kobbra Server class
    """
    def __init__(self):
        # Load/Generate configuration 
        self.managers = ManagerFactory()
        cfgman = self.managers.Config()
        dbman = self.managers.Database()

        ConsoleLogger.currentlevel = int(cfgman.GetIni("loglevel"))        
        dbman.Connect(cfgman.GetIni("db.file"))

    def main(self):
        """
        Main Kobbra Server method
        """
        ConsoleLogger.banner()

        #mus = MusServer(self.managers)
        info = InfoServer(self.managers)
        
        #mus.start()
        info.start()

        gevent.wait()
        
        self.managers.Database().Close()
        ConsoleLogger.log("DBG", "Exiting!")
