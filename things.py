#!/usr/bin/python3
# -*- coding: utf-8 -*-

class Room:
    def __init__(self, kakao):
        self.kakao=kakao
        
        self.type=""
        self.members=[]
        self.watermarks=[]
        self.chatId=0
        self.lastMessage=""
    
        self.status="normal"
        
    def write(self, msg):
        self.kakao.write(self.chatId, msg)
        
    def leave(self):
        self.kakao.leave(self.chatId)
        
    def read(self, since=0):
        msgs=[]
    
        r=self.kakao.read(self.chatId, since)
        self.kakao.upseen(self.chatId, r["chatRoom"]["lastLogId"], 300, 300)
        
        self.watermarks=r["chatRoom"]["watermarks"]
        
        for msg in r["chatLogs"]:
            m=Message(msg["authorId"], msg["msgId"], msg["chatId"], msg["logId"], msg["sendAt"], msg["message"])
            msgs.append(m)
        
        return msgs
        
class Message:
    def __init__(self, authorId, msgId, chatId, logId, sendAt, message):
        self.authorId=authorId
        self.msgId=msgId
        self.chatId=chatId
        self.logId=logId
        self.sendAt=sendAt
        self.message=message
        
        self.command=False
        self.argument=[]
        
        if self.message[0:2]=="--":
            if "\n" not in self.message:
                self.command=self.message[2:]
            else:
                self.command=self.message[2:self.message.find("\n")]
                self.argument=self.message.split("\n")[1:]