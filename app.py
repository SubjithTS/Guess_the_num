from flask import Flask, render_template
from flask_socketio import SocketIO, emit
import random

app = Flask(__name__)
socketio = SocketIO(app)
secret_word = random.choice(["apple", "banana", "cherry"])

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('connect')
def handle_connect():
    emit('message', {'user': 'System', 'text': 'A new player has joined!'})

@socketio.on('send_message')
def handle_message(data):
    emit('message', data, broadcast=True)

@socketio.on('guess')
def handle_guess(data):
    guess = data['guess'].lower()
    if guess == secret_word:
        emit('correct_guess', {'user': data['user']}, broadcast=True)
    else:
        emit('wrong_guess', {'user': data['user'], 'guess': guess}, broadcast=True)

if __name__ == '__main__':
    socketio.run(app, debug=True)
