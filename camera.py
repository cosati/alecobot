from flask.helpers import make_response
import cv2
import numpy
import json
import RPi.GPIO as GPIO
from flask import Flask, render_template, Response, stream_with_context, request, jsonify
# from flask_socketio import SocketIO, emit

video = cv2.VideoCapture(0)
app = Flask('__name__')
# socketio = SocketIO(app)

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

#define sensor GPIOs
rearSensor = 16

#initialize GPIO status variables
irSts = 0

#define sensor pins as input
GPIO.setup(rearSensor, GPIO.IN)

data = {
    'sliderr'   : 0,
    'sliderg'   : 0,
    'sliderb'   : 0,
    'rear'      : 0
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
        
def rear_sensor():
    ir = GPIO.input(rearSensor)
    return ir

# def rear_sensor():
#     irSts = GPIO.input(rearSensor)
#     if irSts:
#         rs = "<td>-</td>"
#     elif not irSts:
#         rs = '<td class=\"alert\">Stop!</td>'
#     else:
#         rs = "<td class=\"nosignal\">No signal!</td>"
#     return rs

@app.route('/')
def index():    
    return render_template('index.html')

@app.route('/video_feed')
def video_feed():
    return Response(video_stream(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/data_feed', methods=["GET", "POST"])
def data_feed():
    data = {
    'sliderr'   : 500,
    'sliderg'   : 300,
    'sliderb'   : 100,
    'rear'      : rear_sensor()
    }
    response = make_response(jsonify(data))
    response.content_type = 'application/json'
    return response

# @socketio.on('connect')
# def test_connect():
#     emit('after connect',  {'data':'Connection success'})

app.run(host='0.0.0.0', port='5000', debug=False)
# if __name__ == '__main__':
#     socketio.run(app, host='0.0.0.0')