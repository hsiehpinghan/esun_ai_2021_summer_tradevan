from flask import Flask
from absl import logging
from esun.interfaces.rest import (
    api
)

app = Flask(__name__)
app.register_blueprint(api.bp)
