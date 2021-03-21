#!/usr/bin/env python3

import logging
import os
from bluetooth import *
from wifi import Cell, Scheme
import subprocess
import time
import urllib
import dbus
import dbus.exceptions
import dbus.mainloop.glib
import dbus.service

from ble import (
    Advertisement,
    Characteristic,
    Service,
    Application,
    find_adapter,
    Descriptor,
    Agent,
)

import struct
import requests
import array
from enum import Enum

import sys

import RPi.GPIO as GPIO
import time
import datetime
import firebase_admin
from firebase_admin import firestore
from firebase_admin import credentials, initialize_app, storage
from picamera import PiCamera
from time import sleep
from random import randint
#from datetime import datetime
from picamera import PiCamera
from picamera.array import PiRGBArray
from threading import Thread
import numpy as np
from fractions import Fraction

# Display Log Info
verbose = True     # Display showMessage if True




MainLoop = None
try:
    from gi.repository import GLib

    MainLoop = GLib.MainLoop
except ImportError:
    import gobject as GObject

    MainLoop = GObject.MainLoop

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
logHandler = logging.StreamHandler()
filelogHandler = logging.FileHandler("logs.log")
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logHandler.setFormatter(formatter)
filelogHandler.setFormatter(formatter)
logger.addHandler(filelogHandler)
logger.addHandler(logHandler)

mainloop = None
global_ssid = None
global_psk = None

wpa_supplicant_conf = "/etc/wpa_supplicant/wpa_supplicant.conf"
sudo_mode = "sudo "


BLUEZ_SERVICE_NAME = "org.bluez"
GATT_MANAGER_IFACE = "org.bluez.GattManager1"
LE_ADVERTISEMENT_IFACE = "org.bluez.LEAdvertisement1"
LE_ADVERTISING_MANAGER_IFACE = "org.bluez.LEAdvertisingManager1"




# Motion Settings
threshold = 25     # How Much a pixel has to change
sensitivity = 6000  # How Many pixels need to change for motion detection

# Camera Settings
CAMERA_WIDTH = 128
CAMERA_HEIGHT = 80     
CAMERA_HFLIP = True
CAMERA_VFLIP = True
CAMERA_ROTATION= 0
CAMERA_FRAMERATE = 35
#--------------------------------------------------------------------------------------------

# Init firebase with your credentials
cred = credentials.Certificate("/home/pi/Desktop/smarthealth-61305-firebase-adminsdk-q56q7-0613d4d2e1.json")
initialize_app(cred, {'storageBucket': 'smarthealth-61305.appspot.com'})
#firebase_admin.initialize_app(cred)
db = firestore.client()
today = datetime.datetime.now()
#camera = PiCamera()

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BOARD)
GPIO.setup(37, GPIO.IN)
GPIO.setup(36, GPIO.OUT)



#-------------------------------------------------------------------------------------------  





class InvalidArgsException(dbus.exceptions.DBusException):
    _dbus_error_name = "org.freedesktop.DBus.Error.InvalidArgs"


class NotSupportedException(dbus.exceptions.DBusException):
    _dbus_error_name = "org.bluez.Error.NotSupported"


class NotPermittedException(dbus.exceptions.DBusException):
    _dbus_error_name = "org.bluez.Error.NotPermitted"


class InvalidValueLengthException(dbus.exceptions.DBusException):
    _dbus_error_name = "org.bluez.Error.InvalidValueLength"


class FailedException(dbus.exceptions.DBusException):
    _dbus_error_name = "org.bluez.Error.Failed"


def register_app_cb():
    logger.info("GATT application registered")


def register_app_error_cb(error):
    logger.critical("Failed to register application: " + str(error))
    mainloop.quit()



def wifi_connect(ssid, psk):
    # write wifi config to file
    f = open('wifi.conf', 'w')
    f.write('country=US\n')
    f.write('ctrl_interface=DIR=/var/run/wpa_supplicant GROUP=netdev\n')
    f.write('update_config=1\n')
    f.write('\n')
    f.write('network={\n')
    f.write('    ssid="' + ssid + '"\n')
    f.write('    psk="' + psk + '"\n')
    f.write('}\n')
    f.close()
    
    

    cmd = 'mv wifi.conf ' + wpa_supplicant_conf
    cmd_result = ""
    cmd_result = os.system(cmd)
    print (cmd + " - " + str(cmd_result))


    # restart wifi adapter
    cmd = sudo_mode + 'ifdown wlan0'
    cmd_result = os.system(cmd)
    print(cmd + " - " + str(cmd_result))

    time.sleep(2)

    cmd = sudo_mode + 'ifup wlan0'
    cmd_result = os.system(cmd)
    print(cmd + " - " + str(cmd_result))

    time.sleep(10)

    cmd = 'iwconfig wlan0'
    cmd_result = os.system(cmd)
    print(cmd + " - " + str(cmd_result))

    cmd = 'ifconfig wlan0'
    cmd_result = os.system(cmd)
    print(cmd + " - " + str(cmd_result))

    p = subprocess.Popen(['ifconfig', 'wlan0'], stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE)

    out, err = p.communicate()

    ip_address = "<Not Set>"

    for l in out.split('\n'):
        if l.strip().startswith("inet addr:"):
            ip_address = l.strip().split(' ')[1].split(':')[1]

    return ip_address



class BluetoothService(Service):

    RASBERRY_SVC_UUID = "12634d89-d598-4874-8e86-7d042ee07ba7"

    def __init__(self, bus, index):
        Service.__init__(self, bus, index, self.RASBERRY_SVC_UUID, True)
        self.add_characteristic(SSIDControlCharacteristic(bus, 0, self))
        self.add_characteristic(PskControlCharacteristic(bus, 1, self))
        


class PskControlCharacteristic(Characteristic):
    uuid = "4116f8d2-9f66-4f58-a53d-fc7440e7c14e"
    description = b"Get psk"
    alls = []
    
    class State(Enum):
        on = "ON"
        off = "OFF"
        unknown = "UNKNOWN"

        @classmethod
        def has_value(cls, value):
            return value in cls._value2member_map_

    power_options = {"ON", "OFF", "UNKNOWN"}

    def __init__(self, bus, index, service):
        Characteristic.__init__(
            self, bus, index, self.uuid, ["encrypt-read", "encrypt-write"], service,
        )

        self.value = [0xFF]
        self.add_descriptor(CharacteristicUserDescriptionDescriptor(bus, 1, self))

    def ReadValue(self, options):
        logger.debug(" Read: " + rep7D042EE07BA7r(self.value))
        return self.value

    def WriteValue(self, value, options):
        print("psk received")
       
        if value == '':
            print("EMPTY psk received")
        else:
            temp = ''.join([chr(b) for b in value])
            print(temp)
            self.alls.append(temp)
            print(len(self.alls))
            if len(self.alls) == 2:
                print((self.alls))
                ip_address = wifi_connect(str(self.alls[0]), str(self.alls[1]))
                print(type(temp))
                print("wpa_supplicant wriitten")
                mainloop.quit()
                #ip_address = wifi_connect('fsdf', '1232324324')
                
                      
                
                
           
           
            
        
        
        self.value = value


class SSIDControlCharacteristic(Characteristic):
    uuid = "322e774f-c909-49c4-bd7b-48a4003a967f"
    description = b"Get ssid "

    def __init__(self, bus, index, service):
        Characteristic.__init__(
            self, bus, index, self.uuid, ["encrypt-read", "encrypt-write"], service,
        )

        self.value = []
        self.add_descriptor(CharacteristicUserDescriptionDescriptor(bus, 1, self))

    def ReadValue(self, options):
        logger.info(" read: " + repr(self.value))
        return self.value

    def WriteValue(self, value, options):
        print("ssid received")
        if value == '':
            print("EMPTY ssid received")
        else:
            temp = ''.join([chr(b) for b in value])
            print(temp)
            
            
            



class CharacteristicUserDescriptionDescriptor(Descriptor):

    CUD_UUID = "2901"

    def __init__(
        self, bus, index, characteristic,
    ):

        self.value = array.array("B", characteristic.description)
        self.value = self.value.tolist()
        Descriptor.__init__(self, bus, index, self.CUD_UUID, ["read"], characteristic)

    def ReadValue(self, options):
        return self.value

    def WriteValue(self, value, options):
        if not self.writable:
            raise NotPermittedException()
        self.value = value


class VivaldiAdvertisement(Advertisement):
    def __init__(self, bus, index):
        Advertisement.__init__(self, bus, index, "peripheral")
        self.add_manufacturer_data(
            0xFFFF, [0x70, 0x74],
        )
        self.add_service_uuid(BluetoothService.RASBERRY_SVC_UUID)

        self.add_local_name("Vivaldi")
        self.include_tx_power = True


def register_ad_cb():
    logger.info("Advertisement registered")


def register_ad_error_cb(error):
    logger.critical("Failed to register advertisement: " + str(error))
    mainloop.quit()


AGENT_PATH = "/com/punchthrough/agent"


def main():
    global mainloop

    dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)

    # get the system bus
    bus = dbus.SystemBus()
    # get the ble controller
    adapter = find_adapter(bus)

    if not adapter:
        logger.critical("GattManager1 interface not found")
        return

    adapter_obj = bus.get_object(BLUEZ_SERVICE_NAME, adapter)

    adapter_props = dbus.Interface(adapter_obj, "org.freedesktop.DBus.Properties")

    # powered property on the controller to on
    adapter_props.Set("org.bluez.Adapter1", "Powered", dbus.Boolean(1))

    # Get manager objs
    service_manager = dbus.Interface(adapter_obj, GATT_MANAGER_IFACE)
    ad_manager = dbus.Interface(adapter_obj, LE_ADVERTISING_MANAGER_IFACE)

    advertisement = VivaldiAdvertisement(bus, 0)
    obj = bus.get_object(BLUEZ_SERVICE_NAME, "/org/bluez")

    agent = Agent(bus, AGENT_PATH)

    app = Application(bus)
    app.add_service(BluetoothService(bus, 2))

    mainloop = MainLoop()

    agent_manager = dbus.Interface(obj, "org.bluez.AgentManager1")
    agent_manager.RegisterAgent(AGENT_PATH, "NoInputNoOutput")

    ad_manager.RegisterAdvertisement(
        advertisement.get_path(),
        {},
        reply_handler=register_ad_cb,
        error_handler=register_ad_error_cb,
    )

    logger.info("Registering GATT application...")

    service_manager.RegisterApplication(
        app.get_path(),
        {},
        reply_handler=register_app_cb,
        error_handler=[register_app_error_cb],
    )

    agent_manager.RequestDefaultAgent(AGENT_PATH)
    
    mainloop.run()
    # ad_manager.UnregisterAdvertisement(advertisement)
    # dbus.service.Object.remove_from_connection(advertisement)


#if __name__ == "__main__":
  #  main()


#-------------------------------------------------------------------------------------------  
class PiVideoStream:
    def __init__(self, resolution=(CAMERA_WIDTH, CAMERA_HEIGHT), framerate=CAMERA_FRAMERATE, rotation=0, hflip=False, vflip=False):
        # initialize the camera and stream
        self.camera = PiCamera()
        self.camera.resolution = resolution
        self.camera.rotation = rotation
        self.camera.framerate = framerate
        self.camera.hflip = hflip
        self.camera.vflip = vflip
        self.rawCapture = PiRGBArray(self.camera, size=resolution)
        self.stream = self.camera.capture_continuous(self.rawCapture,
            format="rgb", use_video_port=True)

        # initialize the frame and the variable used to indicate
        # if the thread should be stopped
        self.frame = None
        self.stopped = False
        camera = self.camera
        


    def start(self):
        # start the thread to read frames from the video stream
        t = Thread(target=self.update, args=())
        t.daemon = True
        t.start()
        return self

    def update(self):
        # keep looping infinitely until the thread is stopped
        for f in self.stream:
            # grab the frame from the stream and clear the stream in
            # preparation for the next frame
            self.frame = f.array
            self.rawCapture.truncate(0)

            # if the thread indicator variable is set, stop the thread
            # and resource camera resources
            if self.stopped:
                self.stream.close()
                self.rawCapture.close()
                self.camera.close()
                return

    def read(self):
        # return the frame most recently read
        return self.frame

    def stop(self):
        # indicate that the thread should be stopped
        self.stopped = True
            
#------------------------------------------------------------------------------------------- 
def userMotionCode():
    # Users can put code here that needs to be run prior to taking motion capture images
    # Eg Notify or activate something.
    # User code goes here
    
    msgStr = "Motion Found So Do Something ..."
    showMessage("userMotionCode",msgStr)
    pictureFunc()
    return   





def pictureFunc():
    
                GPIO.output(36, GPIO.LOW)
                time.sleep(0.3)
                GPIO.output(36, GPIO.HIGH)
        
                value = randint(0, 10000)

                vs.camera.capture('/home/pi/Desktop/randomCaptures/picture%s.jpg' % value)
                
                #os.system("aplay /home/pi/Desktop/test.wav")

                # Put your local file path
                fileName = ('/home/pi/Desktop/randomCaptures/picture%s.jpg' % value)
                bucket = storage.bucket()
                blob = bucket.blob(fileName)
                blob.upload_from_filename(fileName)


                # Opt : if you want to make public access from the URL
                blob.make_public()


                #Adding data to firebase
                doc_ref = db.collection('testEntry').document('testDocument')

                doc_ref.set({

                    'Datetime':today,
                     'ImageUrl1':blob.public_url
                     

                })

                print("your file url", blob.public_url)
                print("Datetime: ", today)

#-------------------------------------------------------------------------------------------    
def showTime():
    rightNow = datetime.datetime.now()
    currentTime = "%04d%02d%02d-%02d:%02d:%02d" % (rightNow.year, rightNow.month, rightNow.day, rightNow.hour, rightNow.minute, rightNow.second)
    return currentTime    

#-------------------------------------------------------------------------------------------     
def showMessage(functionName, messageStr):
    if verbose:
        now = showTime()
        print ("%s %s - %s " % (now, functionName, messageStr))
    return

#----------------------------------------------------------------------------------------------- 
def checkForMotion(data1, data2):
    # Find motion between two data streams based on sensitivity and threshold
    motionDetected = False
    pixColor = 3 # red=0 green=1 blue=2 all=3  default=1
    if pixColor == 3:
        pixChanges = (np.absolute(data1-data2)>threshold).sum()/3
    else:
        pixChanges = (np.absolute(data1[...,pixColor]-data2[...,pixColor])>threshold).sum()
    if pixChanges > sensitivity:
        motionDetected = True
        msgStr = ("Found Motion threshold=%s  sensitivity=%s changes=%s" % ( threshold, sensitivity, pixChanges ))
        showMessage("checkForMotion", msgStr)         
    return motionDetected  

#-------------------------------------------------------------------------------------------    
def Main():
    msgStr = "Checking for Motion"
    showMessage("Main", msgStr)   
    frame_1 = vs.read()    
    while True:
        frame_2 = vs.read()  
        if checkForMotion(frame_1, frame_2):
            userMotionCode()
        frame_1 = frame_2   
    return

#-------------------------------------------------------------------------------------------     
if __name__ == '__main__':
    
    try:
        url = "https://www.google.com"
        urllib.urlopen(url)
        status = "Connected"
    except:
        status = "Not connected"
    print status
    if status == "Connected":
        try:
            msgStr = "Loading .... One Moment Please"
            showMessage("Init", msgStr)    
            vs = PiVideoStream().start()   # Initialize video stream
            vs.camera.hflip = CAMERA_HFLIP
            vs.camera.vflip = CAMERA_VFLIP
            vs.camera.rotation = CAMERA_ROTATION        
            time.sleep(2.0)    # Let camera warm up         
            Main()
        finally:
            print("")
            print("+++++++++++++++++++")
            print("  Exiting Program")
            print("+++++++++++++++++++")
            print("")
            
    else:
        main()
        try:
            msgStr = "Loading .... One Moment Please"
            showMessage("Init", msgStr)    
            vs = PiVideoStream().start()   # Initialize video stream
            vs.camera.hflip = CAMERA_HFLIP
            vs.camera.vflip = CAMERA_VFLIP
            vs.camera.rotation = CAMERA_ROTATION        
            time.sleep(2.0)    # Let camera warm up         
            Main()
        finally:
            print("")
            print("+++++++++++++++++++")
            print("  Exiting Program")
            print("+++++++++++++++++++")
            print("")
            
