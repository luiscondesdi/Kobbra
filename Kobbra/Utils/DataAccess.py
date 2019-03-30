# -*- coding: utf-8 -*-
"""
This module implements the Kobbra sqlite database
"""
import sqlite3
from gevent.lock import Semaphore
from os.path import isfile
from os import stat

class Database(object):
    """
    Main object for Kobbra database
    """
    def __init__(self, path):
        self.lock = Semaphore()
        self.db = sqlite3.connect(path)
        self.emptydb = stat(path).st_size == 0

    def runscript(self, path):
        with open(path, "r") as f:
            self.db.executescript(f.read())
    
    def runsentence(self, sentence, values=None):
        with self.lock:
            c = self.db.cursor()
            if values != None:
                c.execute(sentence, values)
            else:
                c.execute(sentence)
            self.db.commit()
            return c.fetchall()
    
    def close(self):
        self.db.close()
