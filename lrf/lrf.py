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
    Config.set('api', 'port', '3006')
    Config.add_section('lrf')
    Config.set('lrf', 'sr_port', '/dev/ttyUSB0')
    Config.set('lrf', 'baudrate', '115200')
    Config.set('lrf', 'timeout', '1')
    Config.add_section('data')
    Config.set('data', 'stop', '55 00 02 00 00 57') # stop
    Config.set('data', 'fro', '55 01 02 00 00 56') # find range once
    Config.set('data', 'frc', '55 02 02 03 E8 BE') # find range continuous
    Config.set('data', 'selfcheck', '55 03 02 00 00 54') #self check
    Config.set('data', 'blz', '55 04 02 00 64 37') #100 meter blind zone
    Config.set('data', 'count', '55 06 02 00 00 51') # count number of times lrf laser emitted
    Config.write(cfgfile)
    cfgfile.close()
configReader = ConfigParser()
configReader.read('config.ini')
sr_port = configReader['lrf']['sr_port']
baudrate = configReader['lrf'].getint('baudrate')
sr_timeout = configReader['lrf']['timeout']
api_port = configReader['api'].getint('port')
print(sr_port,baudrate)

def lrf(data):
    # os.system('python -m serial.tools.list_ports -v')
    # obj = list(ls.comports())
    # port_desc=obj[0].description
    # ports = serial.tools.list_ports.comports(include_links=False)
    # print(ports)
    # actualport=''
    # length=len(ports)
    # print(length)
    # print()
    # for port in ports :
    #     print('Find port '+ port.device)
    # try:
    #     ser = serial.Serial(ports[0].device)
    #     if ser.isOpen():
    #         ser.close()
    #     print("by port",ports[0].device)
    #     ser = serial.Serial(port.device, baudrate, timeout=1,stopbits=1,bytesize=8)
    #     ser.flushInput()
    #     ser.flushOutput()
    #     print('Connect ' + ser.name)
    #     actualport=ports[0].device
    #     ser.close()
    # except:
    #     if length > 1:
    #         ser=serial.Serial(ports[1].device)
    #         if ser.isOpen():
    #             ser.close()
    #         print("by port",ports[1].device)
    #         ser = serial.Serial(port.device, baudrate, timeout=1,stopbits=1,bytesize=8)
    #         ser.flushInput()
    #         ser.flushOutput()
    #         print('Connect ' + ser.name)
    #         actualport=ports[1].device
    #         ser.close() 
    #     else:
    #         return "no open port found"
    # sr=serial.Serial()
    # # sr.port=port
    # sr.port=sr_port
    # sr.baudrate=baudrate
    # sr.timeout=1
    # sr.stopbits=1
    # sr.bytesize=8
    # sr.open()
    # if sr.is_open:
    #     print("port is open")
    #     data=sr.write(data)
    #     response = sr.read()
    #     print(response)
    #     return response
    # else:
    #     print("port is not open")
    #     return 0

    os.system('python -m serial.tools.list_ports -v')
    sr=serial.Serial()
    sr.port=str(sr_port)
    sr.baudrate=baudrate
    sr.timeout=1
    sr.stopbits=1
    sr.bytesize=8
    sr.open()
    if sr.is_open:
        print("port is open")
        data=sr.write(data)
        response = sr.readline()
        print(response)
        sr.close()
        return response
    else:
        print("port is not open")
        return 0
class LRF(tornado.web.RequestHandler):
    def get(self):
        self.render('index.html')
class LRFOnce(tornado.web.RequestHandler):
    def get(self):
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
class LRFContinuous(tornado.web.RequestHandler):
    def get(self):
        data = configReader['data']['frc']
        #data = bytes.fromhex(data)
        # os.system('python -m serial.tools.list_ports -v')
        # sr=serial.Serial()
        # sr.port=str(sr_port)
        # sr.baudrate=baudrate
        # sr.timeout=1
        # sr.stopbits=1
        # sr.bytesize=8
        # sr.open()
        # if sr.is_open:
        #     print("port is open")
        #     data=sr.write(data)
        #     resp = sr.readline()
        global i

        os.system('python -m serial.tools.list_ports -v')
        sr=serial.Serial()
        sr.port=str(sr_port)
        sr.baudrate=baudrate
        sr.timeout=1
        sr.stopbits=1
        sr.bytesize=8
        sr.open()
        if sr.is_open:
            print("port is open")
            data=sr.write(data)
            while i!=15:
                i+=1
                response = sr.readline().strip().decode('UTF-8')
                resp=bytes.fromhex(response)
                print(resp)
                resp = resp.hex()
                resp = encrypt(resp,2)
                res1 = resp[4]
                res2 = resp[5]
                res3 = resp[6]
                dist = res1+res2+res3
                dist = int(dist,16) / 10
                print("resp ",str(dist)+" meter")
            sr.close()
            data = configReader['data']['stop']
            resp = lrf(bytes.fromhex(data))    # self.write({'Distance': str(dist)+" meter"})
        else:
            print("port is not open")
            
        # resp = lrf(bytes.fromhex(data))
        # # resp = b'\x55\x02\x04\xfc\x00\x38\xe9\x7e'
        # resp = resp.hex()
        # resp = encrypt(resp,2)
        # # print(resp)
        # # resp = bytes.fromhex(resp)
        # # resp = resp.split()[4:7]
        # res1 = resp[4]
        # res2 = resp[5]
        # res3 = resp[6]
        # dist = res1+res2+res3
        # dist = int(dist,16) / 10
        # resp = resp.hex()
        # resp = ''.join(map(str, resp))
        # print("resp ",str(dist)+" meter")
        # self.write({'Distance': str(dist)+" meter"})
class LRFSelfCheck(tornado.web.RequestHandler):
    def get(self):
        data = configReader['data']['selfcheck']
        resp = lrf(bytes.fromhex(data))
        #resp = b'\x55\x03\x06\x00\x00\x00\x28\x28\x25\x75'
        resp = resp.hex()
        resp = encrypt(resp,2)
        temp=resp[8]
        high_voltage=resp[7]
        temp=int(temp,16)
        high_voltage=int(high_voltage,16)
        print("temp ",temp,"°C" )
        print("high_voltage",high_voltage,"V")

        # self.write({'tempreture': str(temp)+" °C"})
        # self.write({'hv': str(high_voltage)+" V"})
class LRFBlindZone(tornado.web.RequestHandler):
    def get(self):
        data = configReader['data']['blz']
        resp = lrf(bytes.fromhex(data))
        print("resp ",resp)
class LRFCount(tornado.web.RequestHandler):
    def get(self):
        data = configReader['data']['count']
        resp = lrf(bytes.fromhex(data))
        resp = resp.hex()
        resp = encrypt(resp,2)
        print("resp ",resp)
class LRFStop(tornado.web.RequestHandler):
    def get(self):
        data = configReader['data']['stop']
        resp = lrf(bytes.fromhex(data))
        print("resp ",resp)
        # self.write({'items': resp})
def make_app():
    return tornado.web.Application([("/", LRF),("/lro", LRFOnce),("/lrc", LRFContinuous),("/lrsc", LRFSelfCheck),("/lrbz", LRFBlindZone),("/count", LRFCount),("/stop", LRFStop)],template_path=os.path.join(os.path.dirname(__file__), "templates"))

if __name__ == '__main__':
    app = make_app()
    app.listen(api_port)
    print("Lrf is listening for commands on port: "+str(api_port))
    IOLoop.instance().start()
