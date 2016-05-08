#!/usr/bin/python3
# -*- coding: utf-8 -*-

from things import Room

class Listener:
    def __init__(self, kakao):
        self.kakao=kakao
    
    def listen(self):
        rooms=[]
    
        nchats=self.kakao.nchatlist()["chatInfos"]
        
        for nchat in nchats:
            r=Room(self.kakao)
            
            r.type=nchat["type"]
            r.members=[ member["userId"] for member in nchat["displayMembers"] ]
            r.chatId=nchat["chatId"]
            r.lastMessage=nchat["lastMessage"]
            
            if not r.type=="PlusChat":rooms.append(r)

        return rooms