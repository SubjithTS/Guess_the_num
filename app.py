from flask import Flask, render_template, session
from flask_socketio import SocketIO, emit, join_room, leave_room
import random
import math
import os
from datetime import datetime
from flask import Flask, render_template, request
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

MONGODB_URI = os.environ.get('MONGODB_URI', 'mongodb+srv://sreyas:LGAxY9cwZynotQuT@cluster0.mhetipw.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0')

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key_here'
socketio = SocketIO(app)

# Store game state
games = {}

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('connect')
def handle_connect():
    print(f'Client connected: {request.sid}')

@socketio.on('join_game')
def handle_join_game(data):
    username = data.get('username', 'Anonymous')
    
    # Create or get game room
    room = 'main_room'
    join_room(room)
    
    # Initialize game if not exists
    if room not in games:
        games[room] = {
            'target_number': random.randint(1, 100),
            'players': {},
            'game_active': True
        }
        print(f"New game started in room {room}. Target number: {games[room]['target_number']}")
    
    # Store player info
    games[room]['players'][request.sid] = username
    
    emit('game_update', {
        'type': 'player_joined',
        'message': f'{username} has joined the game!',
        'username': username
    }, room=room)
    
    emit('game_info', {
        'message': f'Welcome {username}! Guess a number between 1 and 100.',
        'target_number': games[room]['target_number']  # For debugging, remove in production
    })

@socketio.on('make_guess')
def handle_guess(data):
    room = 'main_room'
    
    if room not in games or not games[room]['game_active']:
        emit('guess_result', {
            'success': False,
            'message': 'Game is not active or has ended.'
        })
        return
    
    try:
        guess = int(data['guess'])
        username = games[room]['players'].get(request.sid, 'Anonymous')
        target = games[room]['target_number']
        
        if guess == target:
            # Correct guess!
            games[room]['game_active'] = False
            emit('game_winner', {
                'user': username,
                'guess': guess,
                'message': f'🎉 {username} guessed the number {target} correctly! Game over!'
            }, room=room, broadcast=True)
            
            emit('guess_result', {
                'success': True,
                'correct': True,
                'message': f'Congratulations! You guessed the number {target} correctly! 🎉',
                'guess': guess
            })
            
        else:
            # Calculate how close the guess is
            difference = abs(guess - target)
            
            if difference <= 5:
                feedback = "Very hot! 🔥"
            elif difference <= 10:
                feedback = "Hot! ♨️"
            elif difference <= 20:
                feedback = "Warm 🌡️"
            elif difference <= 30:
                feedback = "Cool ❄️"
            else:
                feedback = "Cold! 🧊"
            
            # Give hint about higher/lower
            direction = "higher" if guess < target else "lower"
            
            emit('guess_result', {
                'success': True,
                'correct': False,
                'message': f'Your guess is {guess}. Go {direction}. {feedback}',
                'guess': guess,
                'feedback': feedback
            })
            
            # Broadcast to other players (without revealing the exact feedback)
            emit('message', {
                'user': 'System',
                'text': f'{username} guessed {guess}.',
                'type': 'guess'
            }, room=room, broadcast=True, include_self=False)
            
    except ValueError:
        emit('guess_result', {
            'success': False,
            'message': 'Please enter a valid number!'
        })

@socketio.on('send_message')
def handle_message(data):
    room = 'main_room'
    username = games[room]['players'].get(request.sid, 'Anonymous') if room in games else 'Anonymous'
    
    emit('message', {
        'user': username,
        'text': data['text'],
        'type': 'chat'
    }, room=room, broadcast=True)

@socketio.on('disconnect')
def handle_disconnect():
    room = 'main_room'
    if room in games and request.sid in games[room]['players']:
        username = games[room]['players'][request.sid]
        del games[room]['players'][request.sid]
        
        emit('game_update', {
            'type': 'player_left',
            'message': f'{username} has left the game.'
        }, room=room, broadcast=True)

if __name__ == '__main__':
    socketio.run(app, debug=True)
