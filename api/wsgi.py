#!/usr/bin/env python3

import pathlib
import eventlet
import subprocess

from flask import Flask, send_from_directory, jsonify
from flask_socketio import SocketIO, emit
from eventlet.green.subprocess import Popen

eventlet.monkey_patch()

app = Flask(__name__)
app.config.from_json('config.json')
socketio = SocketIO(app, cors_allowed_origins="*")


@app.route('/')
def index():
    return jsonify({'message': 'Thanks for visiting the api.reedo.me'}), 404


@app.route('/retrieve', methods=['POST'])
def retrieve_file():
    cwd = pathlib.Path.cwd()

    return send_from_directory(directory=cwd, filename='out.pdf')


def convert_and_stream(type, url):
    cwd = pathlib.Path.cwd()
    target = '/home/latex/data/output'
    container = 'opendatacoder/markdown:latest'

    command = ['docker', 'run', '--rm', '-v', '{}:{}'.format(cwd, target),
               '{}'.format(container), '--format', ''.format(type),
               '--output', 'out', '--input', '{}'.format(url)]

    instance = Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

    lines_std_out = iter(instance.stdout.readline, b'')

    for line in lines_std_out:
        socketio.sleep(0)
        data = line.decode('utf8').rstrip('\n')
        socketio.emit('my_response', {'data': str(data)})

    socketio.emit('done')


@socketio.on('instance')
def tasks_threaded(format, url):
    socketio.start_background_task(convert_and_stream, format, url)

    emit('my_response', {'data': 'initiating process'})


@socketio.on('loaded')
def test_message():
    emit('my_response', {'data': 'connected to terminal'})


if __name__ == '__main__':
    socketio.run(app, debug=True)
