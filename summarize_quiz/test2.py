from flask import jsonify, Flask, request, session, url_for, redirect, render_template, g, flash, abort
import json

app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False

@app.route('/')
def index():
    print("main page")
    return "Hello World"

@app.route('/user')
def user():
    return "user"

if __name__ == "__main__":
    app.run(host='0.0.0.0')