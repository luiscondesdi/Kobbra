# -*- coding: utf-8 -*-
"""
This module implements a port of the kepler netty server using the
sockets python module
"""
from gevent import server,signal as gsignal
import signal

from Kobbra.Core.Management import ManagerFactory
from Kobbra.Core.Events import EventDispatcher
from Kobbra.Utils.Crypto import Base64Encoding
from Kobbra.Utils.Log import ConsoleLogger

class InfoServer(object):
    """
    Main server object
    """
    def __init__(self, managers):
        self.managers = managers
        cfgman = self.managers.Config()
        self.localip = cfgman.GetIni("bind")
        self.remoteip = cfgman.GetIni("bind.remote")
        self.serverport = int(cfgman.GetIni("info.port"))

    def start(self):
        """
        Start info server method
        """
        localserver = server.StreamServer((self.localip, self.serverport), self.handle)
        gsignal(signal.SIGTERM, localserver.stop)
        gsignal(signal.SIGINT, localserver.stop)
        localserver.start()
        ConsoleLogger.log("INF", "Info server running on " + self.localip + ':' + str(self.serverport))

        if self.localip != '127.0.0.1':
            lbserver = server.StreamServer(('127.0.0.1', self.serverport), self.handle)
            gsignal(signal.SIGTERM, lbserver.stop)
            gsignal(signal.SIGINT, lbserver.stop)
            lbserver.start()
            ConsoleLogger.log("INF", "Info server running on 127.0.0.1:" + str(self.serverport))
        
        if len(self.remoteip) > 0:
            remoteserver = server.StreamServer(('127.0.0.1', self.serverport), self.handle)
            gsignal(signal.SIGTERM, remoteserver.stop)
            gsignal(signal.SIGINT, remoteserver.stop)
            remoteserver.start()
            ConsoleLogger.log("INF", "Info server running on " + self.remoteip + ':' + str(self.serverport))

    def handle(self, connection, address):
        """
        Method to handle info message events
        """
        ConsoleLogger.log("INF", "InfoServer: New connection at " + address[0])
        B64 = Base64Encoding()
        evt = EventDispatcher(self.managers, connection)

        # Say hi
        connection.sendall(evt.res.hello())
        # self.evt.res.secretkey()

        while True:
            # Mandatory UTF8 conversion
            pkt = list(connection.recv(2048).decode('utf8'))
            
            if len(pkt) == 0:
                break
            
            #if encrypted:
                #pkt = decrypted

            # Split messages following header directives
            pktl = 3 + B64.decode(pkt[:3])
            while pktl <= len(pkt):
                msg = pkt[3:pktl]
                commandid = B64.decode(msg[:2])
                
                ConsoleLogger.log("DBG", "InfoServer: Received command " + "".join(msg))
                evt.request(commandid, msg)

                # Check for more piggybacked commands
                pkt = pkt[pktl:]
                pktl = 3 + B64.decode(pkt[:3])

        ConsoleLogger.log("INF", "InfoServer: Closing connection at " + address[0])
        connection.close()
        
