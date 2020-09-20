import RPi.GPIO as GPIO
import time
from RPLCD import CharLCD
import P3picam
import picamera
from datetime import datetime
from threading import Lock
import queue
import threading
import bluetooth
import email4

displayLock = Lock()
recvQueue = queue.Queue()

MOTION_S = 23
BUZZER   = 24
doorSensorName = "ESP32test"

motionState = False
picPath= "/home/pi/Desktop/images/"
lcd= CharLCD(cols= 16, rows=2, pin_rs= 37, pin_e= 35, pins_data=[33, 31, 29,21], numbering_mode= GPIO.BOARD)
GPIO.setmode(GPIO.BOARD)
GPIO.setup(12, GPIO.IN, pull_up_down= GPIO.PUD_DOWN)
GPIO.setup(10, GPIO.IN, pull_up_down= GPIO.PUD_DOWN)
GPIO.setup(MOTION_S, GPIO.IN)
GPIO.setup(BUZZER, GPIO.OUT)
isAlarmed = False

# Bluetooth connection class
class Bluetooth:
    def __init__(self, name, port):
        self.deviceName = name
        self.address = ""
        self.port = port
        self.socket = None
        self.isDiscovered = False
        self.isConnected = False
        self.previousVal = ""

    def discover_device(self):
        devices = bluetooth.discover_devices(lookup_names=True)
        print("Found {} devices.".format(len(devices)))

        for addr, name in devices:
            if name == self.deviceName:
                print("Found {} - {}".format(addr, name))
                self.address = addr
                self.isDiscovered = True
                #create socket
                self.socket = bluetooth.BluetoothSocket( bluetooth.RFCOMM )
                return True
        return False
   
    def connect(self):
        if self.isDiscovered:
            self.socket.connect((self.address, self.port))
            self.isConnected = True
            return True
        else:
            return False

    def receive_message(self):
        if self.isConnected:
            data = self.socket.recv(100)
            val = data.decode('ascii')
            return val[-1]

    def __del__(self):
        print ("Closing connection ...")
        self.socket.close()
       
def recv_door_sensor_vals(sensorBT, dataQueue):
    global isAlarmed
    while(True):
        val = sensorBT.receive_message()
        for i in val:
            dataQueue.put(i)

def captureImage(currentTime, picPath):
    #Generate the picture's name
    picName = currentTime.strftime("%Y.%m.%d-%H%M%S") + '.jpg'    
    with picamera.PiCamera() as camera:
        camera.resolution= (1280, 720)
        camera.capture(picPath + picName)
    email4.pictureSave(picPath+ picName)
    print("We have taken a picture.")
                                   

def getTime():
    #fetch the current time
    currentTime = datetime.now()
    return currentTime
   
def button_callback_disabled(channel):
    global isAlarmed
    isAlarmed = False
    print("Stopped Alarm")
    displayLock.acquire()
    lcd.clear()
    lcd.write_string(u' Alarm Disabled ')
    displayLock.release()
    GPIO.output(24, False)
   
def button_callback_enabled(channel):
    global isAlarmed
    isAlarmed = True
    print("Start Alarm Mode")
    displayLock.acquire()
    lcd.clear()
    lcd.write_string(u' Alarm Enabled ')
    displayLock.release()

def check_motion_movement():
    global isAlarmed
    if GPIO.input(MOTION_S): #If there is a movement, PIR sensor gives input to GPIO23
        GPIO.output(BUZZER, True) #Output given to Buzzer through GPIO24
        displayLock.acquire()
        lcd.clear()
        if isAlarmed:
            lcd.write_string(u'BEEP .. BEEP ..')
        else:
            lcd.write_string(u'Alarm Disabled')
        time.sleep(1) #Buzzer turns on for 1 second
        GPIO.output(BUZZER, False)
        lcd.clear()
        displayLock.release()

def check_camera():
    global isAlarmed
    motionState = P3picam.motion()
    print (motionState)
    if motionState:        
        currentTime = getTime()
        captureImage(currentTime, picPath)
        alert_with_speaker(0.1, 3)
        displayLock.acquire()
        lcd.clear()
        if isAlarmed:
            lcd.write_string(u'PHOTO TAKEN')
        else:
            lcd.write_string(u'Alarm Disabled')
        displayLock.release()

def alert_with_speaker(delay, repeatFor):
    global isAlarmed
    if isAlarmed:
        print("Alarm enabled, no alerts with speaker")
    else:
        while(repeatFor != 0):
            GPIO.output(BUZZER, True)
            time.sleep(delay)
            GPIO.output(BUZZER, False)
            time.sleep(delay)
            repeatFor-=1

def check_door_sensor():
    global isAlarmed
    if not recvQueue.empty():
        val = recvQueue.get()
        displayLock.acquire()
        if val == "c":
            lcd.clear()
            alert_with_speaker(0.1, 1)
            print("Door closed")
            lcd.write_string(u'Door closed')
        elif val == "o":
            lcd.clear()
            alert_with_speaker(0.1, 2)
            print("Door opened")
            lcd.write_string(u'Door opened')
        displayLock.release()
   
GPIO.add_event_detect(10,GPIO.RISING,callback=button_callback_disabled)
GPIO.add_event_detect(12,GPIO.RISING,callback=button_callback_enabled)

##doorSensor = Bluetooth(doorSensorName, 1)
##if not doorSensor.discover_device():
##    print("Failed to find device")
##    exit()
##    
##if not doorSensor.connect():
##    print("Failed to connect")
##    exit()

##recvThread = threading.Thread( target=recv_door_sensor_vals, args=(doorSensor, recvQueue) )
##recvThread.start()

while True:
    if isAlarmed:
        check_motion_movement()
    check_camera()
##    check_door_sensor()
##
##recvThread.join()


##while True:
##  if GPIO.input(23): #If there is a movement, PIR sensor gives input to GPIO23
##     GPIO.output(24, True) #Output given to Buzzer through GPIO24
##     time.sleep(1) #Buzzer turns on for 1 second
##     GPIO.output(24, False)
####while True:
##   if(GPIO.input(12)==GPIO.HIGH):
##       lcd.write_string(u' Alarm Enabled ')

##if (GPIO.input(10)==GPIO.HIGH):
##    GPIO.output(24, False)
##    isAlarmed = False
