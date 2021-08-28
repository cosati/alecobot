from flask.helpers import make_response
from werkzeug.datastructures import Authorization
import cv2
import numpy
import json
import logging
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

#define sensor pins as input
GPIO.setup(rearSensor, GPIO.IN)

dataSend = {
    'sliderr'   : 0,
    'sliderg'   : 0,
    'sliderb'   : 0,
    'rear'      : 0,
    'front'     : 1,
    'distance'  : 10,
    'light'     : 70,
    'lm'        : 3,
    'rm'        : 4,
    'init'      : 1,
}

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
    dataSend = {
    'sliderr'   : 500,
    'sliderg'   : 300,
    'sliderb'   : 100,
    'rear'      : rear_sensor(),
    'front'     : 1,
    'distance'  : 10,
    'light'     : 70,
    'lm'        : 3,
    'rm'        : 4,
    'init'      : 1,
    }
    response = make_response(jsonify(dataSend))
    response.content_type = 'application/json'
    return response

@app.route('/pilot/<mode>')
def add_message(mode):
    if mode == 'auto':
        pilotMode = 1
    elif mode == 'manual':
        pilotMode = 0
    else: # Stop
        pilotMode = 2
    app.logger.info("Pilot Mode: " + mode)


app.run(host='0.0.0.0', port='5000', debug=False)