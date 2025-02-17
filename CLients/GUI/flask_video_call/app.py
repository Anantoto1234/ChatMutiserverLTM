from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit, join_room, leave_room
import webbrowser
from threading import Timer

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
socketio = SocketIO(app, cors_allowed_origins="*")

users_in_room = {}

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('join')
def handle_join(data):
    room = data['room']
    username = data['username']
    join_room(room)
    users_in_room[request.sid] = username

    emit('user_joined', {'user_id': request.sid, 'username': username}, room=room)
    emit('notification', {'message': f"{username} đã tham gia phòng {room}."}, room=room)

@socketio.on('leave')
def handle_leave(data):
    room = data['room']
    username = users_in_room.pop(request.sid, None)
    leave_room(room)
    
    if username:
        emit('notification', {'message': f"{username} đã rời khỏi phòng {room}."}, room=room)

@socketio.on('offer')
def handle_offer(data):
    emit('offer', data, room=data['room'])

@socketio.on('answer')
def handle_answer(data):
    emit('answer', data, room=data['room'])

@socketio.on('ice-candidate')
def handle_ice_candidate(data):
    emit('ice-candidate', data, room=data['room'])

def open_browser():
    webbrowser.open_new('http://localhost:5002/')

if __name__ == '__main__':
    Timer(1, open_browser).start()
    socketio.run(app, host='0.0.0.0', port=5002)
