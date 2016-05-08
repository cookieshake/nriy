#!/usr/bin/python3
# -*- coding: utf-8 -*-

from threading import Thread
import time

from weather import IyWeather

class Cuckoo:
    def __init__(self, directData, kakao):
        self.directData=directData
        self.kakao=kakao
        Thread( target=self.checker, args=() ).start()
        
    def checker(self):
        while True:
            try:
                now="%02i%02i" % (time.localtime()[3], time.localtime()[4])
                for direct in self.directData:
                    if "weatheralarm" in self.directData[direct]:
                        if self.directData[direct]["weatheralarm"]==now:
                            iy=IyWeather()
                            toWrite=""
                            
                            if "weatherlocation" in self.directData[direct]:
                                toWrite+=iy.getWeather(self.directData[direct]["weatherlocation"][0])

                            else:
                                toWrite+=iy.getWeather()

                            
                            toWrite+="\n\n행복한 하루 되세요(행복)"
                            self.kakao.write(direct, toWrite)
                            
                time.sleep(60)
            except:
                break