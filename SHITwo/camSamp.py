import RPi.GPIO as GPIO
import time
import time
from picamera import PiCamera
from time import sleep
from random import randint
from datetime import datetime


today = datetime.now()
camera = PiCamera()

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BOARD)
GPIO.setup(37, GPIO.IN)
GPIO.setup(36, GPIO.OUT)


value = 1


def pictureFunc():
        
        
                GPIO.output(36, GPIO.HIGH)
            
                camera.capture('/home/pi/Desktop/blueeleven/picture%s.jpg' % value)
                
                GPIO.output(36, GPIO.HIGH)
                



while value < 1001:
   
        pictureFunc()
        print('picture taken number:%s' % value)
        value = value+1
            
        
    
    
    
    
    

