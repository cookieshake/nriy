# -*- coding: utf-8 -*-
import string

class YoYak:
    def __init__(self, msgList):
        self.msgList=[]
        for msg in msgList:
            msg=msg.replace(" ","")
            for punct in string.punctuation: msg=msg.replace(punct, "")
            self.msgList.append(msg)
            
        self.allText="\n".join(self.msgList)        
        self.scale=10
        self.nDic={}
        
        for n in range(2, self.scale+1):
            self.nDic[n]={}
        
    def makeNgram(self, list, N):
        Dic={}
        for text in list:
            i=0
            while len(text[i:i+N])==N: #N단위로 끊음
                pointer=text[i:i+N]
                if pointer in Dic: Dic[pointer]+=1
                else: Dic[pointer]=1
                i+=1

        return Dic

    def removeDup(self, N):
        for gram in self.nDic[N]:
            if self.nDic[N][gram]>1:
                for n in range(N-1, 1, -1):
                    i=0
                    while len(gram[i:i+n])==n:
                        pointer=gram[i:i+n]
                        self.nDic[n][pointer]-=(self.nDic[N][gram])
                        i+=1
                        
    def countSet(self, N):
        if N==2: return 5
        elif N==3 or N==4: return 4
        elif N>4: return 3
        
    def getYoYak(self):
        outputList=[]

        for n in range(2, self.scale+1):
            self.nDic[n]=self.makeNgram(self.msgList, n)

        for n in range(self.scale, 1, -1):
            self.removeDup(n)

        for n in self.nDic:
            print(self.nDic[n])
            
        for n in range(2, self.scale):
            for item, count in sorted(self.nDic[n].items(), key=lambda x:x[1], reverse=True):
                if count>=self.countSet(n): outputList.append(item)
        
        outputList.sort(key=lambda x:self.allText.find(x))
        
        return ", ".join(outputList)


    


