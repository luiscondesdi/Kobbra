# -*- coding: utf-8 -*-
"""
This module implements the Kobbra object model
"""

class Player(object):
    """
    Main player storage class
    """

    def __init__(self, playerdata):
        self.id = None
        self.name = playerdata[0]
        self.motto = playerdata[2]
        self.figure = playerdata[3]
        self.pfigure = playerdata[4]
        self.sex = playerdata[5]
        self.credits = 0
        self.tickets = 0
        self.films = 0

class Room(object):
    """
    Main room storage class
    """

    def __init__(self, roomdata):
        self.id = None
        self.users = 0
        self.maxusers = 30
    
    def Enter(self):
        if self.users < self.maxusers:
            self.users += 1