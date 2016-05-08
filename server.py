#!/usr/bin/python3
# -*- coding: utf-8 -*-

from threading import Thread
import time
import copy
import hashlib

from things import Room, Message
from config import version
from weather import IyWeather
from yoyak import YoYak

class Server:
    def __init__(self, superUsers, cuckoo, directData):
        self.directCommandDic={
            "기능": self.spec,
            "설정": self.setting,
            "선택": self.select,
            "날씨": self.weather
        }
        
        self.multiCommandDic={
            #"기능": self.multispec,
            "선택": self.select,
            "요약": self.yoyak
        }
                        
        self.superCommandDic={
            "키": self.printKeys,
            "슈퍼키": self.printSuperKeys
        }
        
        self.superUsers=superUsers
        self.directData=directData
        
    def putServer(self, rooms):
        for room in rooms:
            if room.type=="DirectChat":
                if "status" in self.directData[room.chatId] and self.directData[room.chatId]["status"]=="select":
                    self.directData[room.chatId]["selection"]=room.lastMessage
                else:
                    Thread( target=self.directServe, args=(room,) ).start()
            elif room.type=="MultiChat":
                Thread( target=self.multiServe, args=(room,) ).start()
    
    def directServe(self, room):
        msgs=room.read()
        
        for msg in msgs:
            if msg.authorId in self.superUsers:
                if msg.command in self.superCommandDic:
                    self.superCommandDic[msg.command](room, msg)   
            if msg.command in self.directCommandDic:
                self.directCommandDic[msg.command](room, msg)    

    def multiServe(self, room):
        msgs=room.read()
        
        for msg in msgs:
            if msg.command in self.multiCommandDic:
                self.multiCommandDic[msg.command](room, msg)
    
    def spec(self, room, msg):
        toWrite=(
            "나란잉여" + version + "\n\n"
            
            "입력방법:\n"
            "--<기능>\n"
            "<요소1>\n"
            "<요소2>\n"
            "...\n\n"
            
            "기능\n"
            "1. --설정: 각종 개인설정을 합니다\n"
            "2. --선택: 요소들을 입력해주면 그 중 하나를 선택해 드립니다\n"
            "3. --날씨: 날씨를 알려 드립니다. 요소에 지역명(시,군,구,동,읍,면)을 넣으면 그 지역의 날씨를 알려 드립니다"
        )
        

        
        room.write(toWrite)
    
    def printKeys(self, room, msg):
        keys=open("./sav/keys").read().split("\n")
        
        for key in keys[:5]:
            room.write(key)
            time.sleep(1)

    def printSuperKeys(self, room, msg):
        keys=open("./sav/superKeys").read().split("\n")
        
        for key in keys[:5]:
            room.write(key)
            time.sleep(1)
            
    def select(self, room, msg):
        if len(msg.argument)==0:
            self.kakao.write(chatId, "선택할 것을 주세요")
            return None
            
        selections=msg.argument
        hashList=[]
        
        timeNow=time.localtime()
        for selection in selections:
            selectPlus=selection+str(timeNow[0])+str(timeNow[1])+str(timeNow[2])+str(timeNow[3])+str(msg.authorId)
            hashed=hashlib.sha256(selectPlus.encode(encoding="utf-8")).hexdigest()
            hashed=hashlib.sha256(hashed.encode(encoding="utf-8")).hexdigest()
            hashed=hashlib.sha256(hashed.encode(encoding="utf-8")).hexdigest()
            hashed=hashlib.sha256(hashed.encode(encoding="utf-8")).hexdigest()
            hashed=hashlib.sha256(hashed.encode(encoding="utf-8")).hexdigest()
            hashed=hashlib.sha256(hashed.encode(encoding="utf-8")).hexdigest()
            hashed=hashlib.sha256(hashed.encode(encoding="utf-8")).hexdigest()
            hashed=hashlib.sha256(hashed.encode(encoding="utf-8")).hexdigest()
            hashList.append(int(hashed, 16))
        
        selected=selections[hashList.index(max(hashList))]    
            
        room.write(selected + " --> 이걸로 하죠")
        
    def setting(self, room, msg):
        self.directData[room.chatId]["status"]="select"
        
        #try:
        spec=(
            "무엇을 설정할까요?(숫자로 입력)\n"
            "1: 날씨 알림을 받고 싶은 시간\n"
            "2: 날씨 알림을 받고 싶은 지역"
        )
        room.write(spec)
            
        selections=["1","2"]
        for n in range(4):
            time.sleep(5)
            if "selection" in self.directData[room.chatId] and self.directData[room.chatId]["selection"] in selections:
                if self.directData[room.chatId]["selection"]=="1":
                    room.write("원하는 시간을 4자리의 숫자로 입력해 주세요. 예) 오후 1시 3분 --> 1303")
                    
                    for n in range(4):
                        time.sleep(5)
                        if "selection" in self.directData[room.chatId] and len(self.directData[room.chatId]["selection"])==4:
                            try:
                                int(self.directData[room.chatId]["selection"])
                            except:
                                room.write("올바른 숫자를 입력해 주세요")
                                continue
                            times=[ "%02i" % n for n in range(24) ]
                            mins=[ "%02i" % n for n in range(60) ]
                            if self.directData[room.chatId]["selection"][0:2] in times and self.directData[room.chatId]["selection"][2:4] in mins:
                                room.write("알람시간을 %s시 %s분으로 변경합니다" % (self.directData[room.chatId]["selection"][0:2],self.directData[room.chatId]["selection"][2:4]))
                                self.directData[room.chatId]["weatheralarm"] = self.directData[room.chatId]["selection"]
                                self.directData[room.chatId].pop("status")
                                self.directData[room.chatId].pop("selection")
                                return None
                    room.write("시간 초과로 종료합니다")
                    self.directData[room.chatId].pop("status")
                    self.directData[room.chatId].pop("selection")
                    return None
                        
                if self.directData[room.chatId]["selection"]=="2":
                    toWrite="원하는 지역(동, 읍, 면)을 입력해 주세요. 예) 신촌동"
                    room.write(toWrite)
                    donglist=[ line.split(",") for line in open("./donglist.txt").read().split("\n") ]
                    
                    for n in range(4):
                        time.sleep(5)
                        if "selection" in self.directData[room.chatId] and self.directData[room.chatId]["selection"]!=toWrite:
                            selectdong=[]
                            for dong in donglist:
                                if dong[3]==self.directData[room.chatId]["selection"]:
                                    selectdong.append(dong)
                            if len(selectdong)>0:
                                toWrite="숫자로 선택해주세요\n"
                                for index, dong in enumerate(selectdong):
                                    toWrite+="%s: %s %s %s\n" % (index+1, dong[1], dong[2], dong[3])
                                   
                                toWrite=toWrite[:-1]
                                
                                room.write(toWrite)
                                selections=[ str(i) for i in range(1, len(selectdong)+1) ]
                                for n in range(4):
                                    time.sleep(5)
                                    if "selection" in self.directData[room.chatId] and self.directData[room.chatId]["selection"] in selections:
                                        selected=selectdong[int(self.directData[room.chatId]["selection"])-1]
                                        room.write( "지역을 %s %s %s으로 변경합니다" % (selected[1], selected[2], selected[3]) )
                                        self.directData[room.chatId]["weatherlocation"] = selected
                                        self.directData[room.chatId].pop("status")
                                        self.directData[room.chatId].pop("selection")
                                        return None
                                room.write("시간 초과로 종료합니다")
                                self.directData[room.chatId].pop("status")
                                self.directData[room.chatId].pop("selection")
                                return None
                                    
                            else:
                                room.write("지역이 없습니다. 다시 입력해주세요")
                                
                    

        room.write("시간 초과로 종료합니다")
        self.directData[room.chatId].pop("status")
        self.directData[room.chatId].pop("selection")
        #except:
        #    room.write("오류 발생")
        #    self.directData[room.chatId].pop("status")
                        
        
    def weather(self, room, msg):
        iy=IyWeather()
        toWrite=""
        donglist=[ line.split(",") for line in open("./donglist.txt").read().split("\n") ]
        
        if msg.argument==[]:
            if "weatherlocation" in self.directData[room.chatId]:
                toWrite+=iy.getWeather(self.directData[room.chatId]["weatherlocation"][0])
                toWrite+="\n\n"
                toWrite+=iy.getFive(self.directData[room.chatId]["weatherlocation"][2])
            else:
                toWrite+=iy.getWeather()
                toWrite+="\n\n"
                toWrite+=iy.getFive()
            room.write(toWrite)  
        else:
            seldong=[]
            for dong in donglist:
                if msg.argument[0] in dong[2] or msg.argument[0] in dong[3]: seldong.append(dong)
                
            if len(seldong)>0:  
                toWrite="숫자로 선택해주세요\n"
                for index, dong in enumerate(seldong):
                    toWrite+="%s: %s %s %s\n" % (index+1, dong[1], dong[2], dong[3])
                    
                toWrite=toWrite[:-1]
                room.write(toWrite)
                selections=[ str(i) for i in range(1, len(seldong)+1) ]
                
                self.directData[room.chatId]["status"]="select"
                for n in range(4):
                    toWrite=""
                    time.sleep(5)
                    if "selection" in self.directData[room.chatId] and self.directData[room.chatId]["selection"] in selections:
                        selected=seldong[int(self.directData[room.chatId]["selection"])-1]
                        toWrite+=iy.getWeather(selected[0])
                        toWrite+="\n\n"
                        toWrite+=iy.getFive(selected[2])
                        
                        room.write(toWrite)
                        self.directData[room.chatId].pop("status")
                        self.directData[room.chatId].pop("selection")
                        return None
                        
                room.write("시간 초과로 종료합니다")
                self.directData[room.chatId].pop("status")
                self.directData[room.chatId].pop("selection")
                return None
            else:
                room.write("그런 지역이 없습니다")
            
    def yoyak(self, room, msg):
        r=room.read(1)
        
        msgList=[m.message for m in r ]
        
        y=YoYak(msgList)
        
        toWrite="요약하면:\n"
        toWrite+=y.getYoYak()
        
        room.write(toWrite)
            
        