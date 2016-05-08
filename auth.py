#!/usr/bin/python3
# -*- coding: utf-8 -*-

import os
import random

from things import Room


class Authenticator:
    def __init__(self, myUserId, directData, multiData):
        self.myUserId=myUserId
        self.directData=directData
        self.multiData=multiData
    
        self.keys=[]
        if os.path.exists("./sav/keys"):
            self.keys=open("./sav/keys").read().split("\n")
            
        self.superKeys=[]
        if os.path.exists("./sav/superKeys"):
            self.superKeys=open("./sav/superKeys").read().split("\n")
  
        self.authedUsers=[]
        if os.path.exists("./sav/authedUsers"):
            if open("./sav/authedUsers").read()!="":
                self.authedUsers=open("./sav/authedUsers").read().split("\n")
                self.authedUsers=[ int(user) for user in self.authedUsers ]

        self.superUsers=[]
        if os.path.exists("./sav/superUsers"):
            if open("./sav/superUsers").read()!="":
                self.superUsers=open("./sav/superUsers").read().split("\n")
                self.superUsers=[ int(user) for user in self.superUsers ]                
                
        self.save()
        
    def authenticate(self, roomList):
    
        yes=[]
        
        for room in roomList:
            if self.howAuth(room):
                yes.append(room)
                
        return yes
    
    def howAuth(self, room):
        if room.type=="MultiChat":
            if room.chatId in self.multiData:
                return True
            else:
                for member in room.members:
                    if member in self.authedUsers:
                        for msg in room.read():
                            if msg.message=="--인증":
                                if msg.authorId in self.superUsers:
                                    for data in self.directData:
                                        if self.directData[data]["user"]==msg.authorId:
                                            if "multiauth" in self.directData[data]:
                                                self.directData[data]["multiauth"].append(room.chatId)
                                                self.multiData[room.chatId]={"user":msg.authorId}
                                                room.write("나란잉여 인증 완료. '--기능'을 통해 기능들을 보실 수 있습니다.")
                                                return True
                                            else:
                                                self.directData[data]["multiauth"]=[room.chatId]
                                                self.multiData[room.chatId]={"user":msg.authorId}
                                                room.write("나란잉여 인증 완료. '--기능'을 통해 기능들을 보실 수 있습니다.")
                                                return True
                                                
                                elif msg.authorId in self.authedUsers:
                                    for data in self.directData:
                                        if self.directData[data]["user"]==msg.authorId:
                                            if "multiauth" in self.directData[data]:
                                                if len(self.directData[data]["multiauth"])<1:
                                                    self.directData[data]["multiauth"].append(room.chatId)
                                                    self.multiData[room.chatId]={"user":msg.authorId}
                                                    room.write("나란잉여 인증 완료. '--기능'을 통해 기능들을 보실 수 있습니다.")
                                                    return True
                                                
                                                else:
                                                    #room.write("인증 가능 횟수를 초과하셨습니다.")
                                                    room.write("아직 단카방 인증을 사용하실 수 없습니다.")
                                                    room.leave()
                                                    return False
                                            else:
                                                #self.directData[data]["multiauth"]=[room.chatId]
                                                #self.multiData[room.chatId]={"user":msg.authorId}
                                                #room.write("나란잉여 인증 완료. '--기능'을 통해 기능들을 보실 수 있습니다.")
                                                #return True
                                                room.write("아직 단카방 인증을 사용하실 수 없습니다.")
                                                room.leave()
                                                return False
                                                
                #room.write("개인 인증된 분이 '--인증'을 입력함으로써 단카방을 인증하실 수 있습니다. 개인인증 되신 분이 없으시면 사용하실 수 없습니다.")   
                room.write("아직 단카방 인증을 사용하실 수 없습니다.")
                room.leave()
                return False
        
        elif room.type=="DirectChat":
            for member in room.members:
                if member in self.authedUsers:
                    if room.lastMessage in self.superKeys:
                        self.superKeys.remove(room.lastMessage)
                        for member in room.members:
                            if not member==self.myUserId: self.superUsers.append(member)
                        self.save()
                        
                        room.write("관리자 인증 완료.")
    
                    return True
                    
                else:
                    if room.lastMessage in self.keys:
                        self.keys.remove(room.lastMessage)
                        for member in room.members:
                            if not member==self.myUserId:
                                self.authedUsers.append(member)
                                self.directData[room.chatId]={"user":member}
                        self.save()
                        
                        room.write("나란잉여 인증 완료. '--기능'을 통해 기능들을 보실 수 있습니다.")
                        
                        return True
                        
                    elif room.lastMessage in self.superKeys:
                        self.superKeys.remove(room.lastMessage)
                        for member in room.members:
                            if not member==self.myUserId:
                                self.authedUsers.append(member)
                                self.superUsers.append(member)
                                self.directData[room.chatId]={"user":member}
                        self.save()
                        
                        room.write("관리자 인증 완료. '--기능'을 통해 기능들을 보실 수 있습니다.")

                        return True
                    else:
                        room.write("나란잉여를 이용하시려면 올바른 Key를 입력해 주시기 바랍니다")
                        return False
                    
        else:
            return False
        
    def makeKey(self):
        while True:
            key=""
            for n0 in range(2):
                for n1 in range(4):
                    key+=random.choice("1234567890abcdefghijklmnopqrstuvwxyz1234567890")
                key+="-"
            key=key[:-1]
            
            if key not in self.keys and key not in self.superKeys: break
                
        return key
    
    def refresh(self):
        while len(self.superKeys)<5:
            self.superKeys.append(self.makeKey())
 
        while len(self.keys)<50:
            self.keys.append(self.makeKey())
            
        self.save()
        
    def save(self):
        open("./sav/keys", "w").write("\n".join(self.keys))
        open("./sav/superKeys", "w").write("\n".join(self.superKeys))
        open("./sav/authedUsers", "w").write("\n".join( [str(thg) for thg in self.authedUsers] ))
        open("./sav/superUsers", "w").write("\n".join( [str(thg) for thg in self.superUsers] ))
        