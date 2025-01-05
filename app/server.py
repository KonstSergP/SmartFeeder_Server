from flask import Flask
from app.config import *

class Server:
    def __init__(self):
       self.app = Flask(__name__)
    
    def run(self):
        self.app.run(host="0.0.0.0")
