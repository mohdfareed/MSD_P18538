#!/usr/bin/env python3

from api import control_api as control
from api import transcription_api as transcription
from flask import Flask
from flask_executor import Executor

app = Flask(__name__)
executor = Executor(app)
transcription.executor = executor

app.register_blueprint(control.api, url_prefix="/control")
app.register_blueprint(transcription.api, url_prefix="/transcription")

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=9600)
