from function import RoomFunction
from threading import Thread
#import mysql.connector
import subprocess
import os
import logging
import datetime

class RoomService:
    def __init__(self, kakao, listener):
        self.kakao=kakao
        self.listener=listener
        
    def serve(self, chatId):
        try:
            r = self.kakao.read(chatId, 0)
            self.kakao.upseen(chatId, r["chatRoom"]["lastLogId"], 300, 300)

            for chatLog in r["chatLogs"]:
                
                author=chatLog["authorId"]

                if chatLog["message"][0:2]=="--":
                    if "\n" in chatLog["message"]:
                        command=chatLog["message"][2:chatLog["message"].find("\n")]
                        argument=chatLog["message"][chatLog["message"].find("\n")+1:]
                    else:
                        command=chatLog["message"][2:]
                        argument=""
                    
                    function=RoomFunction(self.kakao, self.listener)

                    if command=="기능": function.spec(chatId)
                    if command=="선택": function.select(chatId, argument, author)
                    if command=="읽은사람": function.findReaders(chatId, author, chatLog["logId"])
                    if command=="나가": function.out(chatId)
                    if command=="훈민정음":
                        function.jaum(chatId)
                        break
                    if command=="끝말잇기":
                        function.pp(chatId)
                        break
                    if command=="버전": function.version(chatId)
                    if command=="날씨": function.weather(chatId, argument)
                    if command=="오늘내일": function.todayTomo(chatId)
                    if command=="요약": function.yoyak(chatId)
                    if command=="whatthe공지": function.notice(argument)
                    if command=="whatthe다나가": function.danaga()

        except Exception:
            logging.basicConfig(filename="except.iny",level=logging.DEBUG,)
            logging.exception(str(datetime.datetime.now()))
            open("except.iny","a", encoding="utf-8").write("\n")
            self.kakao.s=self.kakao.start()
        
    def roll(self, roomList):
        for room in roomList:
            Thread(target=self.serve, args=(room,)).start()
