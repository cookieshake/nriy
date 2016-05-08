from threading import Thread
import random
import time
import datetime
import logging

class JaumGame:
    def __init__(self, kakao, listener):
        self.kakao=kakao
        self.listener=listener
        
        wordFile=open("./res/twoword", encoding="utf-8")
        self.wordList=wordFile.read().split()
        wordFile.close()
        
        jaumqFile=open("./res/jaumq", encoding="utf-8")
        self.jaumqList=jaumqFile.read().split()
        jaumqFile.close()
    
    def jaumOk(self, jaum, word, wordList):
        srtList = ["ㄱ","ㄲ","ㄴ","ㄷ","ㄸ","ㄹ","ㅁ","ㅂ","ㅃ","ㅅ","ㅆ","ㅇ","ㅈ","ㅉ","ㅊ","ㅋ","ㅌ","ㅍ","ㅎ"]
        inputJaum = ""
    
        for letter in word:
            if ord(letter)>=44032 and ord(letter)<=55203:
                key = (ord(letter) - 44032)
                end = int(key % 28)
                mid = int((key - end) / 28 % 21)
                srt = int((key / 28 - mid) / 21)
                inputJaum+=srtList[srt]
            else: return False
            
        if jaum==inputJaum: pass
        else: return False
        
        if word in wordList: pass
        else: return False
        
        return True
    
    def jaumStart(self, chatId):
        self.listener.roomDic[chatId]["status"]="jaum"
        jaumqList=self.jaumqList
        self.listener.roomDic[chatId]["jaum"]=random.choice(jaumqList)
        self.listener.roomDic[chatId]["scoreBoard"]={}
        self.listener.roomDic[chatId]["imiList"]=[]
        self.listener.roomDic[chatId]["lastTime"]=int(time.time())
        
        
        jaum=self.listener.roomDic[chatId]["jaum"]
        
        r=self.kakao.read(chatId, 0)
        members=r["chatRoom"]["members"]
        
        self.listener.roomDic[chatId]["memDic"]={}
        memDic=self.listener.roomDic[chatId]["memDic"]
        
        for member in members:
            memDic[member["userId"]]=member["nickName"]
                      
        self.kakao.write(chatId, "답은 '--(정답)'처럼 해줘. 맞으면 +1점 틀리면 -0.3점. 그럼 자음퀴즈를 시작함. " + jaum + "!")
        
        Thread(target=self.jaumIng, args=(chatId,)).start()
            
    def jaumIng(self, chatId):  
        try:
            jaum=self.listener.roomDic[chatId]["jaum"]
            wordList=self.wordList
            imiList=self.listener.roomDic[chatId]["imiList"]
            scoreBoard=self.listener.roomDic[chatId]["scoreBoard"]
            lastTime=self.listener.roomDic[chatId]["lastTime"]
            while True:  
                r=self.kakao.read(chatId, 0)
                
                toWrite=""
                for chatLog in r["chatLogs"]:
                    author=chatLog["authorId"]
                    if chatLog["message"][0:2]=="--":
                        inputWord=chatLog["message"][2:]
                        if self.jaumOk(jaum, inputWord, wordList):
                            if inputWord in imiList:
                                toWrite+=inputWord + " --> 이미함\n"
                                if author in scoreBoard: scoreBoard[author]-=0.3
                                else: scoreBoard[author]=-0.3
                            else:
                                imiList.append(inputWord)
                                toWrite+=inputWord + " --> 인정ㅇㅇ\n"
                                if author in scoreBoard: scoreBoard[author]+=1
                                else: scoreBoard[author]=1
                                lastTime=int(time.time())
                        else:
                            toWrite+=inputWord + " --> 인정 못 함\n"
                            if author in scoreBoard: scoreBoard[author]-=0.3
                            else: scoreBoard[author]=-0.3
                if not toWrite=="": self.kakao.write(chatId, toWrite[:-1])     
                
                if len(imiList)>=2+len(scoreBoard)*4:
                    self.jaumEnd(chatId, "이 쯤 했으면 됐다고 생각해")
                    break
                if int(time.time())-lastTime>18:
                    self.jaumEnd(chatId, "자넨 시간을 소중히 생각하지 않았지. 게임은 끝났다(썩소)")
                    break
                   
                self.kakao.upseen(chatId, r["chatRoom"]["lastLogId"], 300, 300)
                time.sleep(2.1)
                
        except Exception:
            self.listener.roomDic[chatId]={"status":"normal"}
            self.kakao.write(chatId, "에러의 구렁텅이에 빠짐. 젠장.")
            logging.basicConfig(filename="except.iny",level=logging.DEBUG,)
            logging.exception(str(datetime.datetime.now()))
            open("except.iny","a", encoding="utf-8").write("\n")
            self.kakao.s=self.kakao.start()        
        
    def jaumEnd(self, chatId, endMsg):            
        scoreBoard=self.listener.roomDic[chatId]["scoreBoard"]
        memDic=self.listener.roomDic[chatId]["memDic"]
        toWrite=endMsg
        if not len(scoreBoard)==0:
            toWrite+="\n\n-결과-"
            for member, score in sorted(scoreBoard.items(), key=lambda x:x[1], reverse=True):
                toWrite+="\n%s : %0.1f점" % (memDic[member], score)
                
        self.kakao.write(chatId, toWrite)
        self.listener.roomDic[chatId]={"status":"normal", "lastGame":time.time()}

class PostpreGame:
    def __init__(self, kakao, listener):
        self.kakao=kakao
        self.listener=listener
        
        wordFile=open("./res/nouns", encoding="utf-8")
        self.wordList=wordFile.read().split()
        wordFile.close()        
        
    def ppStart(self, chatId):
        self.listener.roomDic[chatId]["status"]="pp"
        self.listener.roomDic[chatId]["scoreBoard"]={}
        self.listener.roomDic[chatId]["imiList"]=[]
        self.listener.roomDic[chatId]["lastTime"]=int(time.time())
        self.listener.roomDic[chatId]["lastWord"]=random.choice(self.wordList)
        
        r=self.kakao.read(chatId, 0)
        members=r["chatRoom"]["members"]
        
        self.listener.roomDic[chatId]["memDic"]={}
        memDic=self.listener.roomDic[chatId]["memDic"]
        
        for member in members:
            memDic[member["userId"]]=member["nickName"]
                      
        self.kakao.write(chatId, "답은 '--(정답)'처럼 해줘. 맞으면 +1점 틀리면 -0.3점. 그럼 끝말잇기를 시작함. " + self.listener.roomDic[chatId]["lastWord"] + "!")
        
        Thread(target=self.ppIng, args=(chatId,)).start()
        
    def ppOk(self, word, lastWord):
        for letter in word:
            if ord(letter)>=44032 and ord(letter)<=55203:continue
            else: return False
            
        if word in self.wordList: pass
        else: return False
        
        if lastWord=="": return True
        
        if word[0]==lastWord[-1]: pass
        else:
            key = ord(word[0]) - 44032
            end = int(key % 28)
            mid = int((key - end) / 28 % 21)
            srt = int((key / 28 - mid) / 21)
            
            keyL = ord(lastWord[-1]) - 44032
            endL = int(keyL % 28)
            midL = int((keyL - endL) / 28 % 21)
            srtL = int((keyL / 28 - midL) / 21)            
            
            if srt==11 and mid==midL and end==endL: pass
            else: return False
        

        
        return True
        
        
    def ppIng(self, chatId):     
        try:
            wordList=self.wordList
            imiList=self.listener.roomDic[chatId]["imiList"]
            scoreBoard=self.listener.roomDic[chatId]["scoreBoard"]
            lastTime=self.listener.roomDic[chatId]["lastTime"]
            
            while True:  
                r=self.kakao.read(chatId, 0)
                lastWord=self.listener.roomDic[chatId]["lastWord"]
                toWrite=""
                for chatLog in r["chatLogs"]:
                    
                    author=chatLog["authorId"]
                    if chatLog["message"][0:2]=="--":
                        inputWord=chatLog["message"][2:]

                        if inputWord in imiList:
                            toWrite+=inputWord + " --> 이미함\n"
                            if author in scoreBoard: scoreBoard[author]-=0.3
                            else: scoreBoard[author]=-0.3
                            
                        else:
                            if self.ppOk(inputWord, lastWord):
                                imiList.append(inputWord)
                                toWrite+=inputWord + " --> 인정ㅇㅇ\n#지금단어는: "+inputWord+"\n"
                                self.listener.roomDic[chatId]["lastWord"]=inputWord
                                if author in scoreBoard: scoreBoard[author]+=1
                                else: scoreBoard[author]=1
                                lastTime=int(time.time())
                                break
                            else:
                                toWrite+=inputWord + " --> 인정 못 함\n"
                                if author in scoreBoard: scoreBoard[author]-=0.3
                                else: scoreBoard[author]=-0.3
                                
                if not toWrite=="": self.kakao.write(chatId, toWrite[:-1])     
                
                if len(imiList)>=3+len(scoreBoard)*4:
                    self.ppEnd(chatId, "이 쯤 했으면 됐다고 생각해")
                    break
                if int(time.time())-lastTime>18:
                    self.ppEnd(chatId, "자넨 시간을 소중히 생각하지 않았지. 게임은 끝났다(썩소)")
                    break
                   
                self.kakao.upseen(chatId, r["chatRoom"]["lastLogId"], 300, 300)
                time.sleep(2.1)
                
        except Exception:
            self.listener.roomDic[chatId]={"status":"normal"}
            self.kakao.write(chatId, "에러의 구렁텅이에 빠짐. 젠장.")
            logging.basicConfig(filename="except.iny",level=logging.DEBUG,)
            logging.exception(str(datetime.datetime.now()))
            open("except.iny","a", encoding="utf-8").write("\n")
            self.kakao.s=self.kakao.start()     
            
    def ppEnd(self, chatId, endMsg):            
        scoreBoard=self.listener.roomDic[chatId]["scoreBoard"]
        memDic=self.listener.roomDic[chatId]["memDic"]
        toWrite=endMsg
        if not len(scoreBoard)==0:
            toWrite+="\n\n-결과-"
            for member, score in sorted(scoreBoard.items(), key=lambda x:x[1], reverse=True):
                toWrite+="\n%s : %0.1f점" % (memDic[member], score)
                
        self.kakao.write(chatId, toWrite)
        self.listener.roomDic[chatId]={"status":"normal", "lastGame":time.time()}     