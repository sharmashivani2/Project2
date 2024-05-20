#!/usr/bin/python

#-*- encoding:utf-8 -*-
import tornado.web
import tornado.ioloop
from tornado.ioloop import IOLoop, PeriodicCallback
import tornado.process
import tornado.template
import tornado.httpserver
import json
import sys
import serial.tools.list_ports as ls
import os,time
import serial
import textwrap
import binascii
import math
import subprocess

i=0
def encrypt(string, length):
    a=textwrap.wrap(string,length)
    return a
from configparser import ConfigParser
os.chdir(os.path.dirname(os.path.realpath(__file__)))
configfile_name = "config.ini"
if not os.path.isfile(configfile_name):
    # Create the configuration file as it doesn't exist yet
    cfgfile = open(configfile_name, 'w')
    # Add content to the file
    Config = ConfigParser()
    Config.add_section('api')
    Config.set('api', 'port', '3017')
    Config.add_section('servo')
    Config.set('servo', 'sr_port', '/dev/ttyUSB0')
    Config.set('servo', 'baudrate', '9600')
    Config.set('servo', 'timeout', '1')
    Config.add_section('data')
    # Config.set('data', 'clockwise1', '40 31 39 39 3a 4d 6f 74 6f 72 3a 48 6f 6d 65 3a') # clk1
    Config.set('data', 'start','@199:Output:Y8 1\r\n') # start
    Config.set('data', 'clk','@199:Motor:Run:M1 1000\r\n') # clk1
    Config.set('data', 'anticlk','@199:Motor:Run:M1 -1000\r\n') # anticlk
    Config.set('data', 'stop','@199:Output:Y8 0\r\n') # stop
    Config.write(cfgfile)
    cfgfile.close()
configReader = ConfigParser()
configReader.read('config.ini')
baudrate = configReader['servo'].getint('baudrate')
baudrate_lrf = configReader['lrf'].getint('baudrate')
sr_timeout = configReader['servo']['timeout']
api_port = configReader['api'].getint('port')
desc = configReader['servo']['sr_desc']
proc = subprocess.Popen(['python -m serial.tools.list_ports '+desc], stdout=subprocess.PIPE, shell=True)
(port1, err) = proc.communicate()
port1 = port1.strip().decode('UTF-8')
sr=serial.Serial()
sr.port=str(port1)
sr.baudrate=baudrate
sr.timeout=1
sr.stopbits=1
sr.open()
l500 = {'500':0,'550':-12885,'600':-23599,'650':-32655,'700':-40426,'750':-47140,'800':-52997,'850':-58168,'900':-62740,'950':-66854,'1000':-70482}
l550 = {'500':12885,'550':0,'600':-3628,'650':-19770,'700':-27541,'750':-34255,'800':-40112,'850':-45283,'900':-49855,'950':-53969,'1000':-57597}
l600 = {'500':23599,'550':3628,'600':0,'650':-9056,'700':-16827,'750':-23541,'800':-29398,'850':-34569,'900':-39141,'950':-43255,'1000':-46883}
l650 = {'500':32655,'550':19770,'600':9056,'650':0,'700':-7771,'750':-14485,'800':-20342,'850':-25513,'900':-30085,'950':-34199,'1000':-37827}
l700 = {'500':40426,'550':27541,'600':16827,'650':7771,'700':0,'750':-6714,'800':-12571,'850':-17742,'900':-22314,'950':-26428,'1000':-30056}
l750 = {'500':47140,'550':34255,'600':23541,'650':14485,'700':6714,'750':0,'800':-5857,'850':-11028,'900':-15600,'950':-19714,'1000':-23342}
l800 = {'500':52997,'550':40112,'600':29398,'650':20342,'700':12571,'750':5857,'800':0,'850':-5171,'900':-9743,'950':-13857,'1000':-17485}
l850 = {'500':58168,'550':45283,'600':34569,'650':25513,'700':17742,'750':11028,'800':5171,'850':0,'900':-4572,'950':-8686,'1000':-12314}
l900 = {'500':62740,'550':49855,'600':39141,'650':30085,'700':22314,'750':15600,'800':9743,'850':4572,'900':0,'950':-4114,'1000':-7742}
l950 = {'500':66854,'550':53969,'600':43255,'650':34199,'700':26428,'750':19714,'800':13857,'850':8686,'900':4114,'950':0,'1000':-3628}
l1000 = {'500':70482,'550':57597,'600':46883,'650':37827,'700':30056,'750':23342,'800':17485,'850':12314,'900':7742,'950':3628,'1000':0}
serv_pos = l1000
def lrf(data):
    desc1 = configReader['lrf']['lrf_desc']
    print(desc1)
    proc = subprocess.Popen(['python -m serial.tools.list_ports '+desc1], stdout=subprocess.PIPE, shell=True)
    (port, err) = proc.communicate()
    port = port.strip().decode('UTF-8')
    sr2=serial.Serial()
    sr2.port=str(port)
    sr2.baudrate=baudrate_lrf
    sr2.timeout=1
    sr2.stopbits=1
    sr2.bytesize=8
    sr2.open()
    if sr2.is_open:
        print("port is open")
        data=sr2.write(data)
        response = sr2.readline()
        sr2.close()
        return response
    else:
        print("port is not open")
        return 0  
class SERVO(tornado.web.RequestHandler):
    def get(self):
        self.render('index.html')
class SERVOStart(tornado.web.RequestHandler):
    def get(self):
        if sr.is_open:
            print("port is open")
            sr.write('@199:*IDN?\r\n'.encode('ascii'))  #@199:*IDN
            # time.sleep(1)
            resp = sr.readline().decode('utf-8')
            print(resp)
            sr.write('@199:Program:Int?\r\n'.encode('ascii')) #@199:Program:Int 
            # time.sleep(1)
            resp = sr.readline().decode('utf-8')
            print(resp)
            sr.write('@199:Program:MInt?\r\n'.encode('ascii')) #@199:Program:MInt
            # time.sleep(1)
            resp = sr.readline().decode('utf-8')
            print(resp)
            sr.write('@199:Motor:EStop?\r\n'.encode('ascii'))  #@199:Program:EStop
            # time.sleep(1)
            resp = sr.readline().decode('utf-8')
            print(resp) 
            sr.write('@199:Output:Y8 1\r\n'.encode('ascii'))
            resp = sr.readline().decode('utf-8')
            print(resp)
        else:
            print("check com port")
            # sr.read(resp)
class LRFOnce(tornado.web.RequestHandler):
    def get(self):
        global serv_pos
        data = configReader['data']['fro']
        resp = lrf(bytes.fromhex(data))
        resp1 = str(resp)
        if(len(resp1)>3):
            # resp = b'\x55\x02\x04\xfc\x00\x38\xe9\x7e'
            resp = resp.hex()
            resp = encrypt(resp,2)
            # print(resp)
            # resp = bytes.fromhex(resp)
            # resp = resp.split()[4:7]
            res1 = resp[4]
            res2 = resp[5]
            res3 = resp[6]
            dist = res1+res2+res3
            dist = int(dist,16) / 10
            # resp = resp.hex()
            # resp = ''.join(map(str, resp))
            print("resp ",str(dist)+" meter")
            self.write({'Distance': str(dist)+" meter"})
        else:
            self.write({'Distance': "Out of range"})
        # self.write({'Distance': str(dist)+" meter"})
        # dist = int(self.get_argument("stp"))
        dist2 = str(dist)[-2:]
        def round_up(n, decimals=0): 
            multiplier = 5 ** decimals 
            return math.ceil(n * multiplier) / multiplier
        def round_down(n, decimals=0):
            multiplier = 5 ** decimals
            return math.floor(n * multiplier) / multiplier
        if (float(dist2) >= 25):
            dist = int(round_up(dist, -2))
        else:
            dist = int(round_down(dist, -2))
        if sr.is_open:
            if str(dist) in serv_pos:
                pos = serv_pos.get(str(dist))
                print("position", pos)
                dt1 = '@199:Motor:Run:M1 '
                dt2 = str(pos)
                print(dt2)
                sr.write(dt1+dt2+'\r\n'.encode('ascii'))
                resp = sr.readline()#.decode('utf-8')
                print(resp)
                self.write({'AntiClk': 'anticlk'})
            if(dist == 500):
                serv_pos = l500
                name = 'l500'
            elif(dist == 550):
                serv_pos = l550
                name = 'l550'
            elif(dist == 600):
                serv_pos = l600
                name = 'l600'
            elif(dist == 650):
                serv_pos = l650
                name = 'l650'
            elif(dist == 700):
                serv_pos = l700
                name = 'l700'
            elif(dist == 750):
                serv_pos = l750
                name = 'l750'
            elif(dist == 800):
                serv_pos = l800
                name = 'l800'
            elif(dist == 850):
                serv_pos = l850
                name = 'l850'
            elif(dist == 900):
                serv_pos = l900
                name = 'l900'
            elif(dist == 950):
                serv_pos = l950
                name = 'l950'
            elif(dist == 1000):
                serv_pos = l1000
                name = 'l1000'
            else:
                pass
            print(name)
        else:
            print("check port")

class SERVOStop(tornado.web.RequestHandler):
    def get(self):
        if sr.is_open:
            sr.write('@199:Output:Y8 0\r\n'.encode('ascii'))
            resp = sr.readline().decode('utf-8')
            print(resp)
            sr.close()
            # resp = servo(data)
            self.write({'Stop': 'stop'})
        else:
            print("check com port")
       

def make_app():
    return tornado.web.Application([("/", SERVO),("/start", SERVOStart),("/stop", SERVOStop),("/lro", LRFOnce)],template_path=os.path.join(os.path.dirname(__file__), "templates"))

if __name__ == '__main__':
    app = make_app()
    app.listen(api_port)
    print("Lrf to Servo is listening for commands on port: "+str(api_port))
    IOLoop.instance().start()
