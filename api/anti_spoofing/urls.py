from api.anti_spoofing.controllers import *
from api.anti_spoofing.config.settings import *
from flask import Flask, render_template
from flask import Response
import uuid
import cv2

app = Flask(__name__)
cap = cv2.VideoCapture(-1, cv2.CAP_ANY)


@app.route("/")
def run_anti_spoofing():
    return render_template('index.html', id=str(uuid.uuid4()), host=host_app, port=port_app)


@app.route("/verification_success")
def verification_success():
    return render_template('success.html')


@app.route("/verification_error")
def verification_error():
    return render_template('error.html')


@app.route("/video_feed/<string:id>")
def video_feed(id):
    return Response(detect_motion(cap, id),
                    mimetype="multipart/x-mixed-replace; boundary=frame")


@app.route("/video_feed")
def video_feed_2():
    id = str(uuid.uuid4())
    return Response(detect_motion(id),
                    mimetype="multipart/x-mixed-replace; boundary=frame")


@app.route("/observable/<string:id>")
def observable(id):
    return observe_transmission(id)
