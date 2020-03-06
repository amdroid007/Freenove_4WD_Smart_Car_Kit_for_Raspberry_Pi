import io
import os
import socket
import struct
import time
import threading
import picamera
import sys,getopt
from threading import Thread
from Thread import *
from server import Server
from evdev import InputDevice, categorize, ecodes
from select import select
from Motor import *
from Buzzer import *
from Ultrasonic import *
from Adc import *
from servo import *
from gpiozero import LED
from TailLight import TailLight
from builtins import True

SPACE = 57
OK = 28
LEFT = 105
RIGHT = 106
UP = 103
DOWN = 108
VUP = 115
VDOWN = 114
PLAY = 164
PREV = 165
NEXT = 163
CONFIG = 171
ESCAPE = 111
STARTAUTO = 112
STARTLINE = 113
STARTLIGHT = 114


ARMSTART = 40 
ARMEND = 155
HANDSTART = 10
HANDEND = 90

HEADLIGHTPIN = 16
LEFTGREENPIN = 21
RIGHTGREENPIN = 21
LEFTREDPIN = 26
RIGHTREDPIN = 20

class myapp():
    
    def __init__(self, motor=None, headlight=None, taillight = None, buzzer = None):
        self.serverup=False
        self.automode=False
        self.taillight = taillight
        self.TCP_Server=Server(motor, headlight, taillight, buzzer)
        print "Initializing..."
        self.on_pushButton()
                        
    def close(self):
        print "Closing down..."
        try:
           stop_thread(self.SendVideo)
           stop_thread(self.ReadData)
           stop_thread(self.power)
        except:
            pass
        try:
            self.TCP_Server.server_socket.shutdown(2)
            self.TCP_Server.server_socket1.shutdown(2)
            self.TCP_Server.StopTcpServer()
        except:
            pass
        self.serverup = False
        print "Close TCP" 
        os._exit(0)
    
    def on_pushButton(self):
        if self.serverup==False:
            self.TCP_Server.tcp_Flag = True
            print "Open TCP"
            self.TCP_Server.StartTcpServer()
            self.SendVideo=Thread(target=self.TCP_Server.sendvideo)
            self.ReadData=Thread(target=self.TCP_Server.readdata)
            self.power=Thread(target=self.TCP_Server.Power)
            self.SendVideo.start()
            self.ReadData.start()
            self.power.start()
            self.serverup = True
            
        elif self.serverup==True:
            self.TCP_Server.tcp_Flag = False
            try:
                stop_thread(self.ReadData)
                stop_thread(self.power)
                stop_thread(self.SendVideo)
            except:
                pass
            
            self.TCP_Server.StopTcpServer()
            self.serverup=False
            print "Close TCP"
    
    def run_light(self):
        self.PWM.setMotorModel(0,0,0,0)
        while self.automode:
            L = self.adc.recvADC(0)
            R = self.adc.recvADC(1)
            if L < 2.99 and R < 2.99 :
                self.PWM.setMotorModel(600,600,600,600)
                
            elif abs(L-R)<0.15:
                self.PWM.setMotorModel(0,0,0,0)
                
            elif L > 3 or R > 3:
                if L > R :
                    self.PWM.setMotorModel(-1200,-1200,1400,1400)
                    
                elif R > L :
                    self.PWM.setMotorModel(1400,1400,-1200,-1200)
            
if __name__ == '__main__':
    devices = map(InputDevice, ('/dev/input/event0','/dev/input/event3'))
    devices = {dev.fd: dev for dev in devices}
    for dev in devices.values(): 
         print(dev)
    buzzer = Buzzer()
    myservo=Servo()
    curarmangle = ARMSTART
    curhandangle = (HANDSTART + HANDEND) / 2
    myservo.setServoPwm('3',curarmangle)
    myservo.setServoPwm('4',curhandangle)
    headlight=LED(HEADLIGHTPIN)
    taillight = TailLight(LEFTREDPIN, LEFTGREENPIN, RIGHTREDPIN, RIGHTGREENPIN)
    
    self.adc=Adc()
    self.PWM=Motor(taillight)
    myshow=myapp(self.PWM, headlight, taillight, buzzer)
    
    sdcount = 0
    try:
        while True:
           r, w, x = select(devices, [], [])
           for fd in r:
              for event in devices[fd].read():
                if event.type == ecodes.EV_KEY:
                    if event.value == 0: # release stop
                        if event.code != 57:
                            PWM.setMotorModel(0,0,0,0) # This will turn on the taillight
                            buzzer.run('0')
                            # tail.bothred() so this is no longer necessary
                            sdcount = 0
                    elif event.value == 1: # press - start
                        if event.code == UP:
                            PWM.setMotorModel(1000,1000,1000,1000)      
                        elif event.code == DOWN:
                            PWM.setMotorModel(-1000,-1000,-1000,-1000)
                        elif event.code == LEFT:
                            # tail.leftblink() Given the change in motor code, I don't think we need this now.
                            PWM.setMotorModel(-1500,-1500,2000,2000)
                        elif event.code == RIGHT:
                            # tail.rightblink() motor class is taking care of turning the blinkers on
                            PWM.setMotorModel(2000,2000,-1500,-1500)
                        elif event.code == SPACE:
                            myshow.on_pushButton()
                        elif event.code == OK:
                            buzzer.run('1') 
                        elif event.code == VUP:
                            if curarmangle >= ARMSTART + 5:
                                curarmangle = curarmangle - 5
                                myservo.setServoPwm('3', curarmangle)
                        elif event.code == VDOWN:
                            if curarmangle <= ARMEND - 5:
                                curarmangle = curarmangle + 5
                                myservo.setServoPwm('3', curarmangle)
                        elif event.code == PLAY:
                            curhandangle = HANDEND
                            myservo.setServoPwm('4',curhandangle)
                        elif event.code == PREV:
                            if curhandangle >= HANDSTART + 5:
                                curhandangle = curhandangle - 5
                                myservo.setServoPwm('4', curhandangle)
                        elif event.code == NEXT:
                            if curhandangle <= HANDEND - 5:
                                curhandangle = curhandangle + 5
                                myservo.setServoPwm('4', curhandangle)
                        elif event.code == CONFIG:
                            headlight.toggle()
                        elif event.code == ESCAPE:
                            self.automode = False
                        elif event.code == STARTAUTO:
                            pass
                        elif event.code == STARTLINE:
                            pass
                        elif event.code == STARTLIGHT:
                            self.automode = True
                            t = threading.Thread(target=self.run_light)
                            t.start()
                        else:
                            print(categorize(event))
                    elif event.value == 2: # Holding - long press processing
                        if event.code == 57: # long press play/pause button
                            sdcount = sdcount + 1
    			if sdcount > 30:
    			   os.system("sudo poweroff")
    except KeyboardInterrupt:
        myshow.close()
