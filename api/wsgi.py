#!/usr/bin/env python3

import uuid
import pathlib
import eventlet
import subprocess

from urllib.parse import urlparse
from eventlet.green.subprocess import Popen
from flask import Flask, send_from_directory, jsonify, request
from flask_socketio import SocketIO, emit
from flask_cors import CORS

requests = eventlet.import_patched('requests.__init__')

app = Flask(__name__)
app.config.from_json('config.json')
socketio = SocketIO(app, cors_allowed_origins='*',
                    manage_session=True, engineio_logger=True)
cors = CORS(app, resources={r'/retrieve/*': {'origins': '*'}})


def parse_git_url(url):
    parse = urlparse(url)

    if parse.netloc != 'github.com':
        return url

    p = parse.path.split('/')
    c = len(p)
    j = c - 5

    user = p[1]
    repo = p[2]
    path = '/'.join(p[c - j - c:])
    base = 'https://api.github.com/repos/'

    api_url = '{}{}/{}/contents/{}'.format(base, user, repo, path)

    session = requests.Session()
    session.auth = (app.config['GITHUB_USER'],
                    app.config['GITHUB_PASSWORD'])
    res = session.get(api_url)

    if res.status_code == requests.codes.ok:
        response = res.json()
        return response['download_url']

    return url


@app.route('/')
def index():
    return jsonify({'message': 'Thanks for visiting api.reedo.me'}), 404


@app.route('/retrieve', methods=['POST'])
def retrieve_file():
    cwd = pathlib.Path.cwd()
    req = request.get_json()

    return send_from_directory(directory=cwd, filename=req['file'])


def convert_and_stream(type, url):
    cwd = pathlib.Path.cwd()
    target = '/home/latex/data/output'
    container = 'opendatacoder/markdown:latest'
    executable = '/usr/bin/docker'
    output = str(uuid.uuid4()).split('-')[-1]

    command = ['{}'.format(executable), 'run', '--rm', '-v',
               '{}:{}'.format(cwd, target), '{}'.format(container),
               '--format', '{}'.format(type), '--output', '{}'.format(output),
               '--input', '{}'.format(url)]

    instance = Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

    lines_std_out = iter(instance.stdout.readline, b'')

    for line in lines_std_out:
        socketio.sleep(0)
        data = line.decode('utf8').rstrip('\n')
        socketio.emit('my_response', {'data': str(data)})

    socketio.emit('done', {'file': '{}.pdf'.format(output)})


@socketio.on('instance')
def tasks_threaded(format, url):
    url = parse_git_url(url)

    socketio.start_background_task(convert_and_stream, format, url)

    emit('my_response', {'data': 'initiating process'})
    emit('my_response', {'data': 'parsing {}'.format(url)})


@socketio.on('loaded')
def test_message():
    emit('my_response', {'data': 'connected to terminal'})


if __name__ == '__main__':
    socketio.run(app, debug=True)
