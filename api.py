import json
from flask import Flask, jsonify, request

from app import make_visualization

app = Flask(__name__)


@app.route('/', methods=['POST'])
def update_record():
    print(request.form)
    arguments = dict(request.form)
    figures = make_visualization(arguments)

    return jsonify(figures)

app.run()