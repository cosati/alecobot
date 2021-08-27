import cv2
import numpy
import RPi.GPIO as GPIO
from flask import Flask, render_template, Response, stream_with_context, request

video = cv2.VideoCapture(0)
app = Flask('__name__')

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

#define sensor GPIOs
rearSensor = 16

#initialize GPIO status variables
irSts = 0

#define sensor pins as input
GPIO.setup(rearSensor, GPIO.IN)

def video_stream():
    while True:
        ret, frame = video.read()
        if not ret:
            break;
        else:
            ret, buffer = cv2.imencode('.jpeg', frame)
            frame = buffer.tobytes()
            yield (b' --frame\r\n' b'Content-type: image/jpeg\r\n\r\n' + frame +b'\r\n')

def rear_sensor():
    while True:
        irSts = GPIO.input(rearSensor)
        if irSts:
            rs = "<td>-</td>"
        elif not irSts:
            rs = "<td>Stop!</td>"
        else:
            rs = "<td>No signal!</td>"
        yield(rs)

@app.route('/')
def index():
    # irSts = GPIO.input(rearSensor)
    # if irSts:
    #     rs = "-"
    # elif not irSts:
    #     rs = "Stop!"
    # else:
    #     rs = "No signal!"
    # templateData = {
    #     'sensor' : irSts
    # }
    return render_template('index.html')

@app.route('/video_feed')
def video_feed():
    return Response(video_stream(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/ir_feed')
def ir_feed():    
    return Response(rear_sensor(), mimetype="text/html")

app.run(host='0.0.0.0', port='5000', debug=False)