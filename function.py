import hashlib
import time
from game import *
from weather import IyWeather
from lang import YoYak
import copy

class RoomFunction:
    def __init__(self, kakao, listener):
        self.kakao=kakao
        self.listener=listener
        
    def findReaders(self, chatId, author, curLog):
        r = self.kakao.read(chatId, 1)
        members=r["chatRoom"]["members"]
        waterList=r["chatRoom"]["watermarks"]

        memList=[]
        for member in members:
            memList.append(member["nickName"])
            if member["userId"]==author: authorName=member["nickName"]
            if member["userId"]==int(self.kakao.userId): myName=member["nickName"]

        authorLogs=[]
        for log in r["chatLogs"]:
            if log["authorId"]==author: authorLogs.append(log["logId"])
        
        lastLog=authorLogs[authorLogs.index(curLog)-1]


        readers=[]
        for n in range(len(waterList)):
            if waterList[n]>=lastLog :readers.append(memList[n])

        toWrite="읽은 사람들:"
        
        for reader in readers:
            if reader==authorName or reader==myName: continue
            toWrite+="\n"+reader
      
        self.kakao.write(chatId, toWrite)  
        
    def select(self, chatId, argument, author):
        if argument=="":
            self.kakao.write(chatId, "선택할걸 달라고")
            return None
            
        selections=argument.split("\n")
        hashList=[]
        
        timeNow=time.localtime()
        for selection in selections:
            selectPlus=selection+str(timeNow[0])+str(timeNow[1])+str(timeNow[2])+str(timeNow[3])+str(author)
            hashed=hashlib.sha1(selectPlus.encode(encoding="utf-8")).hexdigest()
            hashed=hashlib.sha1(hashed.encode(encoding="utf-8")).hexdigest()
            hashed=hashlib.sha1(hashed.encode(encoding="utf-8")).hexdigest()
            hashList.append(int(hashed, 16))
        
        selected=selections[hashList.index(sorted(hashList)[0])]    
            
        self.kakao.write(chatId, selected + " --> 이게 좋을듯 ㅇㅇ")
    
    def spec(self, chatId):
        msg=(
            "나란잉여 "+self.listener.version+"\n\n"
            "1. --읽은사람:\n"
            "너가 쓴 마지막 글을 읽은 사람들을 알려줌. 이게 잘 안 맞을 때에는..포기하면 편함\n\n"
            "2. --선택:\n"
            "--선택하고 엔터한 다음에 한 줄에 선택지 하나씩 입력해주면 선택장애들을 위해 내가 대신 선택해줌\n\n"
            "3. --훈민정음:\n"
            "자음 맞추기 퀴즈\n\n"
            "4. --끝말잇기:\n"
            "끝말잇기\n\n"
            "5. --오늘내일:\n"
            "'시간:날씨/기온/강수확률'형식으로 오늘 내일 날씨를 알려줌.\n\n"
            "6. --날씨:\n"
            "5번이랑 비슷하게 5일치 날씨를 알려줌. 기본 지역은 서울. 한 줄 띄고 지역명을 입력하면 그 지역 날씨를 알려줄게.\n\n"
            "7. --나가:\n"
            "말 그대로 나감"
            )
        self.kakao.write(chatId, msg)
        
    def out(self, chatId):
        self.kakao.write(chatId,"나가야지")
        self.kakao.leave(chatId)
        self.listener.roomDic.pop(chatId)
        self.listener.saveIny(1)
        
    def jaum(self, chatId):
        if "lastGame" in self.listener.roomDic[chatId] and time.time()-self.listener.roomDic[chatId]["lastGame"]<60:
            self.kakao.write(chatId, "지나친 게임이용은 일상생활에 지장을 줄 수 있습니다.")
        else:  
            game=JaumGame(self.kakao, self.listener)
            game.jaumStart(chatId)
    
    def pp(self, chatId):
        if "lastGame" in self.listener.roomDic[chatId] and time.time()-self.listener.roomDic[chatId]["lastGame"]<60:
            self.kakao.write(chatId, "지나친 게임이용은 일상생활에 지장을 줄 수 있습니다.")
        else:
            game=PostpreGame(self. kakao, self.listener)
            game.ppStart(chatId)
    
    def version(self, chatId):
        self.kakao.write(chatId, self.listener.version)
    
    def weather(self, chatId, argument):
        if argument=="": argument="서울"
        if "\n" in argument:
            self.kakao.write(chatId, "지역입력은 한줄로")
        else:
            weat=IyWeather()
            self.kakao.write(chatId, weat.getFive(argument))
    
    def todayTomo(self, chatId):
        weat=IyWeather()
        self.kakao.write(chatId, weat.getWeather())
        
    def danaga(self):
        roomList=[key for key in self.listener.roomDic]
        for room in roomList:
            self.out(room)
            
    def notice(self, msg):
        roomList=[key for key in self.listener.roomDic]
        for room in roomList:
            self.kakao.write(room, msg)
    
    def yoyak(self, chatId):
        r=self.kakao.read(chatId, 1)
        msgList=[]
        for log in r["chatLogs"][-200:]:
            if not log["authorId"]==int(self.kakao.userId): msgList.append(log["message"])
        
        y=YoYak(msgList)
        self.kakao.write(chatId, "요약하면:\n"+y.getYoYak())
        