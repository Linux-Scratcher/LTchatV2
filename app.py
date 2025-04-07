from flask import Flask, render_template, request, session, redirect, url_for
from flask_socketio import SocketIO, join_room, leave_room, emit
import secrets

app = Flask(__name__)
app.config['SECRET_KEY'] = secrets.token_hex(16)
socketio = SocketIO(app)

# Salon de chat principal
chat_room = "general"

@app.route('/')
def index():
    if 'username' in session:
        return redirect(url_for('chat'))
    return render_template('index.html')

@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    if not username:
        return redirect(url_for('index'))
    
    session['username'] = username
    return redirect(url_for('chat'))

@app.route('/chat')
def chat():
    if 'username' not in session:
        return redirect(url_for('index'))
    return render_template('chat.html', username=session['username'])

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('index'))

@socketio.on('join')
def on_join():
    username = session['username']
    join_room(chat_room)
    emit('message', {'msg': f'{username} a rejoint le chat'}, room=chat_room)

@socketio.on('leave')
def on_leave():
    username = session['username']
    leave_room(chat_room)
    emit('message', {'msg': f'{username} a quitté le chat'}, room=chat_room)
    session.pop('username', None)

@socketio.on('message')
def handle_message(data):
    username = session['username']
    emit('message', {'msg': f'{username}: {data["msg"]}'}, room=chat_room)

if __name__ == '__main__':
    socketio.run(app, debug=True, port=5006)  # Port personnalisé
