import os
from flask import Flask
from src.flaskr import chat

def create_app(test_config=None):
    app = Flask(
        __name__, 
        instance_relative_config=True,
        template_folder='chat/templates',
        static_folder='static'
    )
 
    chat.init_app(app)

    return app