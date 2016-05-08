from katokwrap import KakaotalkWrapper
from auth import RoomAuth
from service import RoomService
import os
import pickle
import time
import datetime
import logging

class NriyListener:
    def __init__(self, uuid, skey, userid, version):
        self.uuid=uuid
        self.skey=skey
        self.userid=userid
        self.kakao=KakaotalkWrapper(self.uuid, self.skey, self.userid)
   
        self.roomDic={}
        self.tierDic={0:[121550205], 1:[], 2:[], 3:[]}
        self.lastTime=time.time()
        self.version=version
    
        if os.path.isfile("./roomfile.iny"): self.roomDic = pickle.load(open("./roomfile.iny", "rb"))
        if os.path.isfile("./tier.iny"): self.tierDic = pickle.load(open("./tier.iny", "rb"))
        
        for room in self.roomDic:
            self.roomDic[room]={"status":"normal"}  
        

    def saveIny(self, ctr):
        if ctr==0 or ctr==1:pickle.dump(self.roomDic, open("./roomfile.iny", "wb"))
        if ctr==0 or ctr==2:pickle.dump(self.tierDic, open("./tier.iny", "wb"))
    
    def hello(self, chatId):
        self.kakao.write(chatId, "잉여해.. 왠지 오류가 많음. 그러려니.. 기능을 보려면 --기능")

    def busy(self, chatId):
        self.kakao.write(chatId, "나란잉여를 이용하실 수 없습니다.")
        self.kakao.leave(chatId)
   
    def start(self):
        while True:
            try:
                while True:
                    nowTime=time.time()
                    if nowTime-self.lastTime>500:
                        self.kakao.s=self.kakao.start()
                        self.lastTime=nowTime
                    
                    nchat=self.kakao.nchatlist()
                    newRoomList=nchat["chatInfos"]
                    toServe=[]

                    if len(newRoomList) > 0:
                        for newRoom in newRoomList:
                            chatId=newRoom["chatId"]
                            
                            if newRoom["type"]=="PlusChat":continue  
                            
                            authorizer=RoomAuth()
                            if authorizer.auth(newRoom, self.tierDic, self.roomDic):
                                if not chatId in self.roomDic:
                                    self.hello(chatId)
                                    self.roomDic[chatId]={"status":"normal"}     
                                if self.roomDic[chatId]["status"]=="normal": toServe.append(chatId)
                            else:
                                self.busy(chatId)
                    
                    if len(toServe)>0:
                        server=RoomService(self.kakao, self)
                        server.roll(toServe)
                        
                    time.sleep(5.9)
                    
            except Exception:
                logging.basicConfig(filename="except.iny",level=logging.DEBUG,)
                logging.exception(str(datetime.datetime.now()))
                open("except.iny","a", encoding="utf-8").write("\n")
                while True:
                    try:
                        self.kakao.s=self.kakao.start()
                    except: continue
                time.sleep(1)
            except KeyboardInterrupt:
                self.saveIny(0)
                break