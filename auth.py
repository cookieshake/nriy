import random

class RoomAuth:
    def auth(self, newRoom, tierDic, roomDic):

        chatId=newRoom["chatId"]
        members=newRoom["displayMembers"]
        
        t0=0
        t1=0
        t2=0
        t3=0
        
        
        for member in members:
            if member["userId"] in tierDic[0]: t0+=1
            if member["userId"] in tierDic[1]: t1+=1
            if member["userId"] in tierDic[2]: t2+=1
            if member["userId"] in tierDic[3]: t3+=1
        

        if t0>=1 and t1+t2+t3==0:
            for member in members:
                if member["userId"] in tierDic[0]: continue
                else: tierDic[1].append(member["userId"])
            return True

        elif t0+t1>=2:
            for member in members:
                if member["userId"] in tierDic[0]: continue
                elif member["userId"] in tierDic[1]: continue
                elif member["userId"] in tierDic[2]: continue
                elif member["userId"] in tierDic[3]:
                    tierDic[3].remove(member["userId"])
                    tierDic[2].append(member["userId"])
                else:
                    tierDic[2].append(member["userId"])

            return True
            
        elif t0+t1+t2>=3:
            for member in members:
                if member["userId"] in tierDic[0]: continue
                elif member["userId"] in tierDic[1]: continue
                elif member["userId"] in tierDic[2]: continue
                elif member["userId"] in tierDic[3]: continue
                else:
                    tierDic[3].append(member["userId"])
            return True
            
        elif t0+t1+t2+t3>=4:
            return True
            
        elif t0+t1+t2+t3>0:
            return True
            
        else:
            return False
        