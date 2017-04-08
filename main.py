# -*- coding: utf-8 -*-
import logging

from flask import Flask, render_template, request, jsonify, send_file, Response
import requests
from graphviz import Source
from PIL import Image
from io import BytesIO
from base64 import b64encode

from parser import parse_to_dot

app = Flask(__name__)

@app.route('/')
def index(name=None):
    return render_template('index.html')

@app.route('/generate_dot')
def generate_dot(methods=["GET"]):
    text = request.args.get('input_text', "", type=str)
    app.logger.info("GOT: " + text)
    dot_repr = parse_to_dot(text)

    f = _dot2pngfile(dot_repr)
    picture = "data:image/png;base64, " + b64encode(f.getvalue())

    return jsonify(dot_repr=dot_repr, picture=picture)

def _dot2pngfile(dot_repr):
    s = Source(dot_repr, format="png")
    f = BytesIO(s.pipe())
    return f

# run locally
if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080, debug=True)
