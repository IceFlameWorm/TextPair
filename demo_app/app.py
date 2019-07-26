from flask import Flask
from .config import Config
from .logger import Logger

app = Flask(__name__)
app.config.from_object(Config)
logger = Logger(app)