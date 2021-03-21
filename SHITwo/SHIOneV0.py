import RPi.GPIO as GPIO
import time
import time
import firebase_admin
from firebase_admin import firestore
from firebase_admin import credentials, initialize_app, storage
from picamera import PiCamera
from time import sleep
from random import randint
from datetime import datetime


# Init firebase with your credentials
cred = credentials.Certificate("/home/pi/Desktop/smarthealth-61305.json")
initialize_app(cred, {'storageBucket': 'smarthealth-61305.appspot.com'})
#firebase_admin.initialize_app(cred)
db = firestore.client()
today = datetime.now()
camera = PiCamera()

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BOARD)
GPIO.setup(37, GPIO.IN)



def pictureFunc():
        
            #for _ in range(10000):
                value = randint(0, 10000)

                
                #camera.start_preview()
                
                camera.capture('/home/pi/Desktop/randomCaptures/picture%s.jpg' % value)
                


                #camera.stop_preview()



                # Put your local file path
                fileName = ('/home/pi/Desktop/randomCaptures/picture%s.jpg' % value)
                #fileName = "/home/pi/Desktop/randomCaptures/picture.jpg"
                bucket = storage.bucket()
                blob = bucket.blob(fileName)
                blob.upload_from_filename(fileName)

                # Put your local file path


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
                n=0
                i=0

        



n=0


while True:
    i=GPIO.input(37)
    
    
    if i==0:
        print("No motion detected"),i
        time.sleep(0.1)
        
    elif i==1:
        print("Motion is detected"),i
        n=(n+1)
        time.sleep(0.1)
        if n>15:
            pictureFunc()
            
        
    
    
    
    
    
