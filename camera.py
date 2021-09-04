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
pilotMode = 0
ledRed = 0
ledGreen = 0
ledBlue = 0

#initialize Arduino sensors variables
calib = -1
distance = -1
ldr = -1
mr = 0
ml = 0
rgbLeds = -1


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
    'autolight' : 0,
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
                commands = str(dataSend['sliderr']) + ';' + str(dataSend['sliderg']) + ';' + str(dataSend['sliderb']) + '\n'
                ser.write(bytes(commands))
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
    'sliderr'   : ledRed,
    'sliderg'   : ledGreen,
    'sliderb'   : ledBlue,
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
    global pilotMode
    if mode == 'auto':
        pilotMode = 1
    elif mode == 'manual':
        pilotMode = 0
    else: # Stop
        pilotMode = 2
    app.logger.info("Pilot Mode: " + mode)
    return 'OK'

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
    return 'OK'

app.run(host='0.0.0.0', port='5000', debug=False)