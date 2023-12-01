from control import motor, servo
from flask import Blueprint, abort, jsonify, request

api = Blueprint("control_api", __name__)


@api.route("/move", methods=["POST"])
def move():
    data = request.json
    if not data:
        abort(400, "No data provided")
    angle = data.get("angle")
    speed = data.get("speed")

    if not angle:
        abort(400, "No angle provided")
    if not speed:
        abort(400, "No speed provided")

    motor.move(speed)
    servo.turn(angle)

    return jsonify({"message": "Car moving", "angle": angle, "speed": speed})


@api.route("/stop", methods=["POST"])
def stop():
    motor.move(0)
    servo.turn(0)

    return jsonify({"message": "Car stopped"})
