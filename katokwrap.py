#!/usr/bin/python
# -*- coding: utf-8 -*-
__author__ = 'carpedm20'


import sys
import struct
import base64
import rsa as RSA
import socket
import bson
import json
import urllib, urllib.request
import http.client
import time
import datetime
import logging
from threading import RLock
from bson.py3compat import b
from Crypto.Cipher import AES
from pkcs73 import PKCS7Encoder

class KakaotalkWrapper:
    def __init__(self, duuid, sKey, userId):
        self.duuid=duuid
        self.sKey=sKey
        self.userId=userId
        self.aes_key=b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
        self.lock=RLock()
        self.s=self.start()

        
        
        
    def start(self):
        self.lock.acquire()
        try:
            document = self.checkin()
           
            host = document['host']
            port = document['port']

            h = self.hand()

            l = self.login(self.sKey, self.duuid)
            enc_l = self.enc_aes(l)
            command = struct.pack('I',len(enc_l)) + enc_l

            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
            s.setsockopt(socket.SOL_TCP, socket.TCP_KEEPIDLE, 30)
            s.setsockopt(socket.SOL_TCP, socket.TCP_KEEPINTVL, 5)
            s.setsockopt(socket.SOL_TCP, socket.TCP_KEEPCNT, 3)
            s.connect((host,port))
            
            s.settimeout(1)

            s.send(h + command)
            reply = s.recv(4096)
        finally:
            self.lock.release()

        return s

    def hex_secure(self, data):
        dec_h=b''
        for n in range(int(len(data)/2052)+1):
            pac=self.dec_aes(data[n*2052+4:(n+1)*2052])
            encoder=PKCS7Encoder()
            pac=encoder.decode(pac)
            dec_h+=pac

        return self.hex_to_dic(dec_h[22:])


    def hex_string(self, data):
        data = data.split('}')[0].replace('\n','').replace(', 0x','\\x').strip().replace('0x','\\x').decode("string-escape")
        dec_h = dec_aes(data[4:])

    def checkin(self, ):
        new = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        new.connect(('110.76.141.20', 5228))

        data = b'\x12\x27\x00\x00'
        data += b'\x00\x00'
        data += b'CHECKIN\x00\x00\x00\x00'
        data += b'\x00'

        body = bson.BSON.encode({'useSub': True, 'ntype': 3, 'userId': self.userId, 'MCCMNC': None, 'appVer': '3.8.7', 'os': 'android'})

        data += body[:4] 
        data += body

        new.sendall(data)
        reply = new.recv(20480)
        
        bs = reply[22:]
        (document, _) = bson._bson_to_dict(bs,dict, True, bson.OLD_UUID_SUBTYPE)

        return document

    def rsa(self, secret):
        n = 0xaf0dddb4de63c066808f08b441349ac0d34c57c499b89b2640fd357e5f4783bfa7b808af199d48a37c67155d77f063ddc356ebf15157d97f5eb601edc5a104fffcc8895cf9e46a40304ae1c6e44d0bcc2359221d28f757f859feccf07c13377eec2bf6ac2cdd3d13078ab6da289a236342599f07ffc1d3ef377d3181ce24c719
        e = 3
        
        pub_key = RSA.PublicKey(n, e)
        enc_key = RSA.encrypt(secret, pub_key)

        return enc_key


    def hand(self, ):
        hand = b'\x80\x00\x00\x00'
        hand += b'\x01\x00\x00\x00' # RSA = 1, DH = 2
        hand += b'\x01\x00\x00\x00' # AES_CBC=1, AES_CFB128=2, AES_OFB128=3, RC4=4
        hand += self.rsa(self.aes_key)

        return hand
    
    def receive(self):
        try:
            reply = b''
            breaker=0
            while True:  
                new = self.s.recv(40960)
                reply += new
                expect=0
                if len(reply)==0:
                    breaker=1
                    break
                for n in range(int(len(reply)/2052)+1):
                    if reply[n*2052:n*2052+4]==b'':continue
                    expect+=4
                    expect+=struct.unpack('i',reply[n*2052:n*2052+4])[0]  
                if len(reply)==expect and expect!=2052:
                    break
            if breaker==1:
                log=open("except.iny", "a", encoding="utf-8")
                log.write(str(datetime.datetime.now())+":at kakao.receive:"+":No Answer"+"\n\n")
                log.close()
                return None
            
            hs=self.hex_secure(reply)
            
        except socket.timeout as e:
            logging.basicConfig(filename="except.iny",level=logging.DEBUG,)
            logging.exception(str(datetime.datetime.now()))
            open("except.iny","a", encoding="utf-8").write("\n")
            return None
                
        return hs
    
    def send(self, data, ignore=False):
        
        enc_data = self.enc_aes(data)
        command = struct.pack('I',len(enc_data)) + enc_data
        
        while True:
            try:
                self.s.send(command)
                reply = b''
                breaker=0
                           
                while True: 
                    new = self.s.recv(40960)
                    reply += new
                    expect=0
                    
                    for n in range(int(len(reply)/2052)+1):
                        if reply[n*2052:n*2052+4]==b'':continue
                        expect+=4
                        expect+=struct.unpack('i',reply[n*2052:n*2052+4])[0]  
                    if len(reply)==expect and expect!=2052:
                        break
                        
                if len(reply)==0:
                    log=open("except.iny", "a", encoding="utf-8")
                    log.write(str(datetime.datetime.now())+":at kakao.send:"+data[6:17].decode().strip()+":No answer"+"\n\n")
                    log.close()
                    self.s=self.start()
                    continue
                
                hs=self.hex_secure(reply)
                break
                
            except socket.timeout as e:
                logging.basicConfig(filename="except.iny",level=logging.DEBUG,)
                logging.exception(str(datetime.datetime.now())+":"+data[6:17].decode().strip())
                open("except.iny","a", encoding="utf-8").write("\n")
                
        return hs

    def login(self, sKey, duuid):
        data = b'\x14\x00\x00\x00'
        data += b'\x00\x00' 
        data += b'LOGIN\x00\x00\x00\x00\x00\x00'
        data += b'\x00' 

        body = bson.BSON.encode({'opt': '', 'prtVer': '1.0', 'appVer': '3.8.7', 'os': 'android', 'lang': 'en', 'sKey': sKey, 'duuid': duuid, 'ntype': 3, 'MCCMNC': None})

        data += body[:4]
        data += body

        return data
    def get_list(self):
        url = 'https://ch-talk.kakao.com/android/chats/list.json'

        headers = { 'GET' : '/android/chats/list.json',
            'HOST' : 'ch-talk.kakao.com',
            'Connection' : 'Close',
            'Accept-Language' : 'ko',
            'Content-Transfer-Encoding' : 'UTF-8',
            'User-Agent' : 'KakaoTalkAndroid/4.0.0 Android/4.1.2',
            'A' : 'android/4.0.3/ko',
            'S' : self.sKey + '-' + self.duuid, 
            'Cache-Control' : 'no-cache',
            'Content-Type' : 'application/x-www-form-urlencoded',
            'Content-Length' : '0' }

        request = urllib.request.Request(url, None, headers)
        response = urllib.request.urlopen(request)

        data = response.read()
        data = data.decode()
        data = json.loads(data ,encoding='utf-8')

        return data
        
    def nchatlist(self):
        self.lock.acquire()
        try:
            data = b'\x06\x00\x00\x00'
            data += b'\x00\x00'
            data += b'NCHATLIST\x00\x00'
            data += b'\x00'

            body = bson.BSON.encode({'maxIds': [], 'chatIds': []})

            data += body[:4]
            data += body
            
            succ = self.send(data)
            while True:
                if not 'chatInfos' in succ:
                    succ = self.receive()
                else: break

                if succ==None:
                    self.s=self.start()
                    succ = self.send(data)
        finally:
            self.lock.release()

        return succ

    def leave(self, chatId):
        self.lock.acquire()
        try:
            data = b'\x06\x00\x00\x00'
            data += b'\x00\x00'
            data += b'LEAVE\x00\x00\x00\x00\x00\x00'
            data += b'\x00'

            body = bson.BSON.encode({'chatId': chatId})

            data += body[:4]
            data += body

            succ = self.send(data)
            
        finally:
            self.lock.release()
            
        return succ

    def upseen(self, chatId, max, cnt, cur):
        self.lock.acquire()
        try:
            data = b'\x08\x00\x00\x00' 
            data += b'\x00\x00' 
            data += b'UPSEEN\x00\x00\x00\x00\x00'
            data += b'\x00'

            body = bson.BSON.encode({'max': max, 'cnt': cnt, 'cur': cur, 'chatId': chatId})
            
            data += body[:4]
            data += body

            succ = self.send(data)
        finally:
            self.lock.release()
            
        return succ

    def read(self, chatId, since):
        self.lock.acquire()
        try:
            data = b'\x06\x00\x00\x00'
            data += b'\x00\x00'
            data += b'READ\x00\x00\x00\x00\x00\x00\x00'
            data += b'\x00'

            body = bson.BSON.encode({'chatId': chatId, 'since': since})

            data += body[:4]
            data += body
            

            succ = self.send(data)
            while True:
                if not "chatRoom" in succ:
                    succ = self.receive()
                else: break 
                 
                if succ==None:
                    self.s=self.start()  
                    succ = self.send(data)
        finally:
            self.lock.release()
                               
        return succ


    def write(self, chatId, msg):
        self.lock.acquire()
        try:
            data = b'\x06\x00\x00\x00'
            data += b'\x00\x00' 
            data += b'WRITE\x00\x00\x00\x00\x00\x00' 
            data += b'\x00' 

            body = bson.BSON.encode({'chatId': chatId, 'msg': msg, 'extra': None, 'type': 1})


            data += body[:4]
            data += body


            succ = self.send(data, True)
        finally:
            self.lock.release()

        return succ

    def enc_aes(self, data):
        iv = b'locoforever\x00\x00\x00\x00\x00'
        aes = AES.new(key=self.aes_key, mode=AES.MODE_CBC, IV=iv)
        encoder=PKCS7Encoder()
        pad_text = encoder.encode(data)
        cipher = aes.encrypt(pad_text)
        return cipher

    def dec_aes(self, data):
        iv = b'\x6c\x6f\x63\x6f\x66\x6f\x72\x65\x76\x65\x72\x00\x00\x00\x00\x00'
        aes = AES.new(key=self.aes_key, mode=AES.MODE_CBC, IV=iv)
        pad_text = aes.decrypt(data)
        encoder=PKCS7Encoder()
        plain_data = encoder.decode(pad_text)
        return pad_text


    def dec_packet(self, data):
        dec_body=data
        packet = {}
        packet['num'] = self.hex_to_num(dec_body[:4])
        packet['status'] = dec_body[4:6]
        packet['command'] = dec_body[6:17].replace(b'\x00',b'')
        packet['body_type'] = dec_body[17:18]
        packet['body_len'] = self.hex_to_num(dec_body[18:22])
        packet['body'] = self.dec_bson(dec_body[22:packet['body_len']+22])
        return packet
     
    def hex_to_dic(self, data):
        
        return bson.BSON.decode(data)
        
    def dec_bson(self, data):
        (document, _) = bson._bson_to_dict(data, dict, True, bson.OLD_UUID_SUBTYPE)
        return document


    def response(self, data):
        text = self.dec_aes(data)
        text[22:]


    def hex_to_num(self, data):
        return struct.unpack('I',data)[0]

