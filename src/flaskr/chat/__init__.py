from flask import Flask, render_template

def init_app(app: Flask):
    app.add_url_rule('/', 'index', index)
    
def index():
    return render_template('index.html')