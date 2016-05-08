#!/usr/bin/python3
# -*- coding: utf-8 -*-

import time
import pickle
import copy
import os

from config import duuid, sKey, version
from katokwrap import KakaotalkWrapper
from listener import Listener
from things import Room
from auth import Authenticator
from server import Server
from cuckoo import Cuckoo

class Iyroid:
    def __init__(self):
        self.version=version
    
        self.kakao=KakaotalkWrapper(duuid, sKey)
        
        self.directData={}
        if os.path.isfile("./sav/directData"):
            self.directData = pickle.load(open("./sav/directData", "rb"))
            for direct in self.directData:
                if "status" in self.directData[direct]: self.directData[direct].pop("status")
                
        self.multiData={}
        if os.path.isfile("./sav/multiData"):
            self.multiData = pickle.load(open("./sav/multiData", "rb"))
            for direct in self.multiData:
                if "status" in self.multiData[direct]: self.multiData[direct].pop("status")
                
        self.mirrordirectData=copy.deepcopy(self.directData)
        self.mirrormultiData=copy.deepcopy(self.multiData)
        
        self.authenticator=Authenticator(self.kakao.userId, self.directData, self.multiData)
        
        self.cuckoo=Cuckoo(self.directData, self.kakao)
        self.server=Server(self.authenticator.superUsers, self.cuckoo, self.directData)

        self.listener=Listener(self.kakao)
        
    def run(self):
        while True:
            try:
                rooms=self.listener.listen()
                
                yesRooms=self.authenticator.authenticate(rooms)
                            
                if len(yesRooms)>0:
                    self.server.putServer(yesRooms)
                    
                self.authenticator.refresh()
                
                if not self.directData==self.mirrordirectData:
                    pickle.dump(self.directData, open("./sav/directData", "wb"))
                    self.mirrordirectData=copy.deepcopy(self.directData)
                
                if not self.multiData==self.mirrormultiData:
                    pickle.dump(self.multiData, open("./sav/multiData", "wb"))
                    self.mirrordirectData=copy.deepcopy(self.multiData)                
                    
                time.sleep(5)
            except KeyboardInterrupt: break
            except: continue
            
nriy=Iyroid()

nriy.run() 
