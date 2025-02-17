from flask import Flask, render_template
from flask_socketio import SocketIO, join_room, leave_room, emit
import webbrowser
from threading import Timer
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, cors_allowed_origins="*")

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('join')
def on_join(data):
    username = data['username']
    room = data['room']
    join_room(room)
    emit('message', {'msg': f"{username} đã tham gia vào phòng {room}."}, room=room)

@socketio.on('leave')
def on_leave(data):
    username = data['username']
    room = data['room']
    leave_room(room)
    emit('message', {'msg': f"{username} đã rời khỏi phòng {room}."}, room=room)

@socketio.on('offer-sending')
def handle_offer(data):
    room = data['room']
    emit('offer-sending', data['offer'], room=room, include_self=False)

@socketio.on('answer-receiving')
def handle_answer(data):
    room = data['room']
    emit('answer-sending', data['answer'], room=room)

@socketio.on('ice-candidate-sending')
def handle_ice_candidate(data):
    room = data['room']
    emit('ice-candidate-sending', data['candidate'], room=room)

def open_browser():
    webbrowser.open_new("http://127.0.0.1:5001/")

if __name__ == '__main__':
    if os.environ.get("WERKZEUG_RUN_MAIN") == "true":
        Timer(1, open_browser).start()
    socketio.run(app, host='0.0.0.0', port=5001, debug=True)
