from flask import Flask, render_template, redirect, url_for, request, session, flash
from flask_socketio import SocketIO, emit
import os
from werkzeug.utils import secure_filename

# Initialize Flask app and SocketIO
app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(24)
socketio = SocketIO(app)

# In-memory database and active user management
users_db = {'test_user': 'password123'}  # Pre-existing user for login
active_users = {}
uploads_dir = "uploads"  # Directory for uploaded files

# Ensure the upload directory exists
if not os.path.exists(uploads_dir):
    os.makedirs(uploads_dir)

@app.route('/')
def home():
    if 'username' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        if users_db.get(username) == password:
            session['username'] = username
            flash("Login successful!", 'success')
            return redirect(url_for('dashboard'))
        else:
            flash("Invalid credentials, please try again.", 'danger')
            return redirect(url_for('login'))
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        # Check if the username already exists
        if username in users_db:
            flash("Username already exists. Please choose another.", 'danger')
            return redirect(url_for('register'))
        
        # Add the new user to the "database"
        users_db[username] = password
        flash("Registration successful! Please log in.", 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    if 'username' not in session:
        return redirect(url_for('login'))

    username = session['username']
    users_online = list(active_users.keys())

    return render_template('dashboard.html', username=username, users_online=users_online)

@app.route('/logout')
def logout():
    username = session.get('username')
    if username:
        session.pop('username', None)
        emit('user_disconnected', {'username': username}, broadcast=True)
    flash("You have been logged out.", 'info')
    return redirect(url_for('login'))

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        flash("No file part", 'danger')
        return redirect(request.url)
    file = request.files['file']
    
    if file.filename == '':
        flash("No selected file", 'danger')
        return redirect(request.url)
    
    # Secure the filename and save it
    filename = secure_filename(file.filename)
    file.save(os.path.join(uploads_dir, filename))
    
    # Send file path or filename to the chat
    return redirect(url_for('dashboard'))

# WebSocket events for real-time communication
@socketio.on('connect')
def handle_connect():
    username = session.get('username')
    if username:
        active_users[username] = request.sid
        emit('user_connected', {'username': username}, broadcast=True)

@socketio.on('disconnect')
def handle_disconnect():
    username = session.get('username')
    if username:
        active_users.pop(username, None)
        emit('user_disconnected', {'username': username}, broadcast=True)

@socketio.on('message')
def handle_message(msg):
    username = session.get('username')
    if username:
        emit('message', {'username': username, 'msg': msg}, broadcast=True)

@socketio.on('file_message')
def handle_file_message(file_data):
    username = session.get('username')
    if username:
        emit('file_message', {'username': username, 'file_data': file_data}, broadcast=True)

if __name__ == '__main__':
    socketio.run(app, debug=True)
