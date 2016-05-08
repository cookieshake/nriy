from xml.dom import minidom
import urllib.request
import urllib.parse
import time

class IyWeather:
    def getWeather(self):
        url="http://www.kma.go.kr/wid/queryDFSRSS.jsp"
        zoneCode="1141058500"
        params = urllib.parse.urlencode({"zone":zoneCode}).encode()

        read=urllib.request.urlopen(url, params).read()
        xmlraw = minidom.parseString(read)

        tm=xmlraw.getElementsByTagName("tm")[0].firstChild.data
        now=time.localtime()
        today=now[2]-int(tm[6:8])
        todayList=[]
        tomorrowList=[]
        toReturn=""

        dataList=xmlraw.getElementsByTagName("data")

        for data in dataList:
            hour=int(data.getElementsByTagName("hour")[0].firstChild.data)
            day=int(data.getElementsByTagName("day")[0].firstChild.data)
            temp=float(data.getElementsByTagName("temp")[0].firstChild.data)
            sky=int(data.getElementsByTagName("sky")[0].firstChild.data) #1:맑음,2:구름조금,3:구름많음,4:흐림
            pty=int(data.getElementsByTagName("pty")[0].firstChild.data) #0:없음, 1:비, 2:비/눈, 3:눈/비, 4:눈
            pop=int(data.getElementsByTagName("pop")[0].firstChild.data)
            
            if pty==0:
                if sky==1 or sky==2:
                    if hour>=8 and hour<=18: icon="(해)"
                    else: icon="(잘자)"
                if sky==3 or sky==4: icon="(구름)"

            if pty==1: icon="(비)"
            if pty==2: icon="(비)"
            if pty==3: icon="(눈)"
            if pty==4: icon="(눈)"

            line="%02d~%02d:%s/%4.1f℃/%2d%%" % (hour-3, hour, icon, temp, pop)
            if day==today: todayList.append(line)
            if day==today+1: tomorrowList.append(line)
        
        if len(todayList)>0:
            toReturn+="오늘\n"
            toReturn+="\n".join(todayList)
        toReturn+="\n내일\n"
        toReturn+="\n".join(tomorrowList)
        
        return toReturn

    def getFive(self, areaq):
        areaq=str(areaq.encode()).replace("\\x","%")[2:-1]
        url="http://weather.service.msn.com/data.aspx?weadegreetype=C&culture=ko-KR&weasearchstr="+areaq

        sun=["23","24","25","29","30","31","32","33","34","36"]
        rain=["0","1","2","3","4","5","6","7","9","10","11","12","17","18","35","37","38","39","40","45","47"]
        snow=["8","13","14","16","41","42","43","46"]
        cloud=["19","20","21","22","26","27","28"]

        read=urllib.request.urlopen(url).read()
        xmlraw = minidom.parseString(read)
        
        try:weather=xmlraw.getElementsByTagName("weather")[0]
        except IndexError: return "그런 곳이 있을까"
        
        location=weather.getAttribute("weatherlocationname")
        forecastList=weather.getElementsByTagName("forecast")

        lineList=[]
        lineList.append(location)

        current=weather.getElementsByTagName("current")[0]
        cur_skycode=current.getAttribute("skycode")
        cur_skytext=current.getAttribute("skytext")
        cur_temp=current.getAttribute("temperature")

        if cur_skycode in sun: icon="(해)"
        elif cur_skycode in rain: icon="(비)"
        elif cur_skycode in snow: icon="(눈)"
        elif cur_skycode in cloud: icon="(구름)"
        elif cur_skycode=="44": icon="(궁금)"

        line="현재:%s%s/%s℃\n" % (icon, cur_skytext, cur_temp)
        lineList.append(line)

        for forecast in forecastList:
            low=forecast.getAttribute("low")
            high=forecast.getAttribute("high")
            skycode=forecast.getAttribute("skycodeday")
            skytext=forecast.getAttribute("skytextday")
            date=forecast.getAttribute("date")
            day=forecast.getAttribute("shortday")
            precip=forecast.getAttribute("precip")

            if skycode in sun: icon="(해)"
            elif skycode in rain: icon="(비)"
            elif skycode in snow: icon="(눈)"
            elif skycode in cloud: icon="(구름)"
            else: icon="(궁금)"

            line="%s(%s):%s/▲%s℃▽%s℃/%s%%" % (date[5:], day, icon, high, low, precip)
            lineList.append(line)

        return "\n".join(lineList)

    
