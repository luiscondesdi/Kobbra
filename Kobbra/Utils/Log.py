# -*- coding: utf-8 -*-
"""
Logging utility module for Kobbra Server
"""
import abc
import datetime

class ConsoleLogger():
    """
    Console logging class
    """
    loglevels = ["NONE", "ERR", "EXC", "WAR", "INF", "DBG"]
    currentlevel = 2 # Default error level at exception, overwritten from INI file

    @staticmethod
    def testlevel(level):
        """
        This method tests a log level versus current log level
        """
        try:
            newlevel = ConsoleLogger.loglevels.index(level)
            return newlevel <= ConsoleLogger.currentlevel and newlevel > 0
        except ValueError:
            return False

    @staticmethod
    def log(level, message):
        """
        This method writes a log to the console
        """
        if ConsoleLogger.testlevel(level):
            print("["+datetime.datetime.now().isoformat()+"]["+ level +"] "+ message)
    
    @staticmethod
    def banner():
        """
        This method prints a server banner to console
        """
        print(r" _____ _____ _____ _____ _____ _____")
        print(r"|  |  |     | __  | __  | __  |  _  |")
        print(r"|    -|  |  | __ -| __ -|    -|     |")
        print(r"|__|__|_____|_____|_____|__|__|__|__|")
        print("\nKobbra - Python FUSE Server Emulation\n")
