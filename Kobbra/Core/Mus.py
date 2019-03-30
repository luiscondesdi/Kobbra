# -*- coding: utf-8 -*-
"""
This module implements a port of the mus server in python
"""
from gevent import server

from Kobbra.Utils.Crypto import Base64Encoding
from Kobbra.Utils.Log import ConsoleLogger

class MusServer(object):
    """
    Main server object
    """
    def __init__(self, ip, port):
        self.serverip = ip
        self.serverport = port
        self.musserver = None

    def run(self):
        """
        Starting Server
        """
        self.musserver = server.StreamServer((self.serverip, self.serverport), self.handle)
        self.musserver.start()
        ConsoleLogger.log("INF", "Mus server running on " + self.serverip + ':' + str(self.serverport))

    def handle(self, connection, address):
        """
        Method to handle info message events
        """
        # Setup greenlet context
        ConsoleLogger.log("INF", "MusServer: New connection at " + address[0])

        connection.close()
