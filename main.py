# -*- coding: utf-8 -*-

from flask import Flask, render_template, request, jsonify

from mindgraph.parser import Parser

app = Flask(__name__)
ps = Parser()

@app.route('/')
def index(name=None):
    return render_template('index.html')

@app.route('/generate_dot')
def generate_dot(methods=["GET"]):
    text = request.args.get('input_text', "", type=str)
    app.logger.info("GOT: " + text)
    dot_repr = ps.parse_to_dot(text)

    return jsonify(dot_repr=dot_repr)

# run locally
if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080, debug=True)
