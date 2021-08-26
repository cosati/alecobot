import cv2
import numpy
import RPi.GPIO as GPIO
from flask import Flask, render_template, Response, stream_with_context, request

video = cv2.VideoCapture(0)
app = Flask('__name__')

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

#define reverse IR sensor
rearSensor = 7

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
                
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/video_feed')
def video_feed():
    return Response(video_stream(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route("/rear_sensor")
def rear_sensor():
    irSts = GPIO.input(rearSensor)
    print(irSts)
    if irSts:
        return "<td class=\"alert\">Stop!</td>"
    return "<td>Go!</td>"

app.run(host='0.0.0.0', port='5000', debug=False)