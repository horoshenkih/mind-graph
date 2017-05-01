# -*- coding: utf-8 -*-

from flask import Flask, render_template, request, jsonify

from organon.parser import Parser

app = Flask(__name__)
ps = Parser()


@app.route('/')
def index(name=None):
    return render_template('index.html')


@app.route('/get_graph')
def get_graph(methods=["GET"]):
    text = request.args.get('input_text', "", type=str)
    app.logger.info("GOT: " + text)
    repr = ps.parse_to_list(text)

    return jsonify(repr=repr)


# run locally
if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080, debug=True)
