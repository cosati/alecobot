from flask.helpers import make_response
from werkzeug.datastructures import Authorization
import cv2
import numpy
import json
import logging
import sys
import time
import threading
import serial
import RPi.GPIO as GPIO
from flask import Flask, render_template, Response, stream_with_context, request, jsonify

video = cv2.VideoCapture(0)
app = Flask('__name__')

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

#define sensor GPIOs
rearSensor = 16

#initialize GPIO status variables
irSts = 0

#initialize other variables
#pilotMode = 0
ledRed = 0
ledGreen = 0
ledBlue = 0
lightAuto = False

#initialize Arduino sensors variables
calib = -1
distance = -1
ldr = -1
mr = 0
ml = 0
rgbLeds = -1
uno_commands = {
    'pilotMode': 0,
    'ArrowUp'   : False,
    'ArrowDown' : False,
    'ArrowLeft' : False,
    'ArrowRight': False,
}

#define sensor pins as input
GPIO.setup(rearSensor, GPIO.IN)

dataSend = {
    'sliderr'   : ledRed,
    'sliderg'   : ledGreen,
    'sliderb'   : ledBlue,
    'rear'      : 0,
    'front'     : 1,
    'distance'  : distance,
    'light'     : ldr,
    'lm'        : ml,
    'rm'        : mr,
    'init'      : calib,
}

@app.before_first_request
def arduino_job():
    def run_job():
        ser = serial.Serial('/dev/ttyACM0', 9600, timeout=1)
        ser.flush()
        global dataSend
        global calib
        global distance
        global ldr
        global mr
        global ml
        global rgbLeds
        global ledRed
        global ledGreen
        global ledBlue
        global uno_commands
        while True:
            if ser.in_waiting > 0:
                line = ser.readline().decode('utf-8').rstrip()
                # time.sleep(0.1)
                try :
                    arr = line.split(';')
                    calib = arr[0]
                    distance = arr[1]
                    ldr = arr[2]
                    mr = arr[3]
                    ml = arr[4]
                    rgbLeds = arr[5]
                except IndexError:
                    pass
                dataSerial = str(1 if lightAuto else 0) + ';' 
                dataSerial += str(ledRed) + ';' + str(ledGreen) + ';' + str(ledBlue) + ';' 
                dataSerial += str(uno_commands['pilotMode']) + ';' 
                dataSerial += str(1 if uno_commands['ArrowUp'] else 0) + ';' 
                dataSerial += str(1 if uno_commands['ArrowDown'] else 0) + ';' 
                dataSerial += str(1 if uno_commands['ArrowLeft'] else 0) + ';' 
                dataSerial += str(1 if uno_commands['ArrowRight'] else 0) 
                dataSerial += '\n'
                print(dataSerial, file=sys.stdout)
                serialWrite = bytes(dataSerial, encoding='utf-8')
                ser.write(serialWrite)
                # print(line, file=sys.stdout)                
                # time.sleep(0.5)

    thread = threading.Thread(target=run_job)
    thread.start()

def video_stream():
    while True:
        ret, frame = video.read()
        if not ret:
            break;
        else:
            ret, buffer = cv2.imencode('.jpeg', frame)
            frame = buffer.tobytes()
            yield (b' --frame\r\n' b'Content-type: image/jpeg\r\n\r\n' + frame +b'\r\n')

# Rear IR sensor      
def rear_sensor():
    ir = GPIO.input(rearSensor)
    return ir

@app.route('/')
def index():    
    return render_template('index.html')

@app.route('/video_feed')
def video_feed():
    return Response(video_stream(), mimetype='multipart/x-mixed-replace; boundary=frame')

# Send data to client
@app.route('/data_feed', methods=["GET", "POST"])
def data_feed():
    global calib
    global distance
    global ldr
    global mr
    global ml
    global rgbLeds
    global ledRed
    global ledGreen
    global ledBlue
    dataSend = {
    'sliderr'   : rgbLeds if lightAuto else ledRed,
    'sliderg'   : rgbLeds if lightAuto else ledGreen,
    'sliderb'   : rgbLeds if lightAuto else ledBlue,
    'rear'      : rear_sensor(),
    'front'     : 1,
    'distance'  : distance,
    'light'     : ldr,
    'lm'        : ml,
    'rm'        : mr,
    'init'      : calib,
    'autolight' : rgbLeds,
    }
    response = make_response(jsonify(dataSend))
    response.content_type = 'application/json'
    return response

# Pilot Mode
@app.route('/pilot/<mode>')
def pilote_mode(mode):
    global uno_commands
    if mode == 'auto':
        uno_commands['pilotMode'] = 1
    elif mode == 'manual':
        uno_commands['pilotMode'] = 2
    else: # Stop
        uno_commands['pilotMode'] = 0
    app.logger.info("Pilot Mode: " + mode)
    return 'OK pilote mode'

# LEDs intensity
@app.route('/<slider>/<value>')
def rgb_value(slider, value):
    global ledBlue
    global ledGreen
    global ledRed
    if slider == 'redslider':
        ledRed = int(value)
    elif slider == 'greenslider':
        ledGreen = int(value)
    elif slider == 'blueslider':
        ledBlue = int(value)
    return 'slider'

# Leds control mode
@app.route('/ledsmode/<value>')
def led_mode(value):
    global lightAuto
    global rgbLeds
    global dataSend
    global ledRed
    global ledGreen
    global ledBlue
    if value == 'man':
        lightAuto = False
        ledRed = rgbLeds
        ledGreen = rgbLeds
        ledBlue = rgbLeds
    elif value == 'auto':
        lightAuto = True
    return 'ledmode'

@app.route('/keydown/<key>')
def key_down(key) :
    global uno_commands
    uno_commands[key] = True
    return 'keydown'

@app.route('/keyup/<key>')
def key_up(key) :
    global uno_commands
    uno_commands[key] = False
    return 'keyup'

app.run(host='0.0.0.0', port='5000', debug=True)