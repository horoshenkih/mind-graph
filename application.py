# -*- coding: utf-8 -*-

from flask import Flask, render_template, request, jsonify

from organon.parser import Parser

application = Flask(__name__)
ps = Parser()


@application.route('/')
@application.route('/index')
def index(name=None):
    return render_template('index.html')


@application.route('/get_graph')
def get_graph(methods=["GET"]):
    text = request.args.get('input_text', "", type=str)
    application.logger.info("GOT: " + text)
    repr = ps.parse_to_list(text)

    return jsonify(repr=repr)


# run locally
if __name__ == '__main__':
    application.run()
