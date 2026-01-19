import os
import uuid
import base64
from flask import Flask, render_template, redirect, url_for, request, session, flash, send_from_directory, jsonify
from flask_socketio import SocketIO, emit, disconnect
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash

# ------------------ CONFIG ------------------

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "pdf", "txt"}

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "dev_secret_key")
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///app.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["MAX_CONTENT_LENGTH"] = 5 * 1024 * 1024  # 5MB limit

socketio = SocketIO(app, manage_session=True)
db = SQLAlchemy(app)

# ------------------ DATABASE ------------------

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    avatar = db.Column(db.String(200), nullable=True)
    status = db.Column(db.String(20), default="Online")
    bio = db.Column(db.String(500), nullable=True)
    email = db.Column(db.String(120), unique=True, nullable=True)

class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    receiver_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)  # None = group
    content = db.Column(db.Text, nullable=True)
    timestamp = db.Column(db.DateTime, default=db.func.current_timestamp())
    is_file = db.Column(db.Boolean, default=False)
    reactions = db.Column(db.JSON, default={})

with app.app_context():
    db.create_all()

# ------------------ ACTIVE USERS ------------------

active_users = {}  # username -> set(socket_ids)

# ------------------ HELPERS ------------------

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

# ------------------ ROUTES ------------------

@app.route("/")
def home():
    return redirect(url_for("dashboard")) if "username" in session else redirect(url_for("login"))

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        user = User.query.filter_by(username=request.form["username"]).first()
        if user and check_password_hash(user.password_hash, request.form["password"]):
            session["username"] = user.username
            flash("Login successful!", "success")
            return redirect(url_for("dashboard"))
        flash("Invalid credentials", "danger")
    return render_template("login.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        if User.query.filter_by(username=request.form["username"]).first():
            flash("Username already exists", "danger")
            return redirect(url_for("register"))

        new_user = User(
            username=request.form["username"],
            password_hash=generate_password_hash(request.form["password"])
        )
        db.session.add(new_user)
        db.session.commit()
        flash("Registration successful!", "success")
        return redirect(url_for("login"))

    return render_template("register.html")

@app.route("/dashboard")
def dashboard():
    if "username" not in session:
        return redirect(url_for("login"))

    users_online = list(active_users.keys())
    if session["username"] not in users_online:
        users_online.append(session["username"])

    return render_template(
        "dashboard.html",
        username=session["username"],
        users_online=users_online
    )

@app.route("/logout")
def logout():
    session.pop("username", None)
    flash("Logged out successfully", "info")
    return redirect(url_for("login"))

@app.route("/profile", methods=["GET", "POST"])
def profile():
    if "username" not in session:
        return redirect(url_for("login"))

    user = User.query.filter_by(username=session["username"]).first()

    if request.method == "POST":
        user.bio = request.form.get("bio")
        user.email = request.form.get("email")
        file = request.files.get("avatar")
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
            file.save(filepath)
            user.avatar = filename
        db.session.commit()
        flash("Profile updated!", "success")
        return redirect(url_for("profile"))

    return render_template("profile.html", user=user)

@app.route("/uploads/<filename>")
def uploaded_file(filename):
    return send_from_directory(app.config["UPLOAD_FOLDER"], filename)

@app.route("/edit_message", methods=["POST"])
def edit_message():
    msg_id = request.form["msg_id"]
    content = request.form["content"]
    msg = Message.query.get(msg_id)
    if not msg or msg.sender.username != session["username"]:
        msg.content = content
        db.session.commit()
        return jsonify({"success": True})
    return jsonify({"success": False}), 403

@app.route("/delete_message", methods=["POST"])
def delete_message():
    msg_id = request.form["msg_id"]
    msg = Message.query.get(msg_id)
    if msg.sender.username == session["username"]:
        db.session.delete(msg)
        db.session.commit()
        return jsonify({"success": True})
    return jsonify({"success": False}), 403

# ------------------ SOCKET.IO ------------------

@socketio.on("connect", namespace="/chat")
def connect():
    if "username" not in session:
        disconnect()
        return

    username = session["username"]
    active_users.setdefault(username, set()).add(request.sid)
    emit("user_connected", {"username": username, "online_count": len(active_users)}, broadcast=True)

@socketio.on("disconnect", namespace="/chat")
def disconnect_user():
    username = session.get("username")
    if username and username in active_users:
        active_users[username].discard(request.sid)
        if not active_users[username]:
            active_users.pop(username)
            emit("user_disconnected", {"username": username, "online_count": len(active_users)}, broadcast=True)

@socketio.on("message", namespace="/chat")
def handle_message(msg):
    if "username" not in session:
        return

    username = session["username"]
    sender = User.query.filter_by(username=username).first()
    if not sender:
        print(f"Error: No user found for username {username}")
        return  # Stop processing if sender not found

    message = Message(sender_id=sender.id, content=msg)
    db.session.add(message)
    db.session.commit()

    mentions = [word[1:] for word in msg.split() if word.startswith("@")]
    emit("message", {
        "msg_id": message.id,
        "username": username,
        "msg": msg,
        "timestamp": message.timestamp.strftime("%H:%M"),
        "reactions": message.reactions
    }, broadcast=True)

    for mentioned_user in mentions:
      if mentioned_user in active_users:
        for sid in active_users[mentioned_user]:
            emit("mention", {"from": username, "msg": msg}, room=sid)

@socketio.on("direct_message", namespace="/chat")
def direct_message(data):
    if "username" not in session:
        return

    sender = User.query.filter_by(username=session["username"]).first()
    receiver = User.query.filter_by(username=data["to"]).first()
    if sender and receiver:
        msg = Message(sender_id=sender.id, receiver_id=receiver.id, content=data["msg"])
        db.session.add(msg)
        db.session.commit()
        # emit only to the receiver SID(s)
        for sid in active_users.get(receiver.username, []):
            emit("direct_message", {
                "from": sender.username,
                "to": receiver.username,
                "msg": data["msg"],
                "timestamp": msg.timestamp.strftime("%H:%M")
            }, room=sid)

@socketio.on("typing", namespace="/chat")
def typing(data):
    emit("typing", {"username": session["username"], "typing": data["typing"]}, broadcast=True)

@socketio.on("react_message", namespace="/chat")
def react_message(data):
    msg = Message.query.get(data["msg_id"])
    emoji = data["emoji"]
    user_id = User.query.filter_by(username=session["username"]).first().id
    reactions = msg.reactions or {}
    reactions.setdefault(emoji, [])
    if user_id not in reactions[emoji]:
        reactions[emoji].append(user_id)
    msg.reactions = reactions
    db.session.commit()
    emit("reaction_updated", {"msg_id": msg.id, "reactions": reactions}, broadcast=True)

@socketio.on("update_status", namespace="/chat")
def update_status(data):
    username = session.get("username")
    if username:
        user = User.query.filter_by(username=username).first()
        user.status = data["status"]
        db.session.commit()
        emit("status_updated", {"username": username, "status": data["status"]}, broadcast=True)

@socketio.on("file_message", namespace="/chat")
def handle_file_message(data):
    if "username" not in session:
        return

    filename = secure_filename(data['filename'])
    file_data = data['file_data']

    # Decode base64
    header, encoded = file_data.split(",", 1)
    decoded = base64.b64decode(encoded)

    filename = f"{uuid.uuid4().hex}_{secure_filename(data['filename'])}"
    with open(filename, 'wb') as f:
        f.write(decoded)

    username = session["username"]
    sender = User.query.filter_by(username=username).first()
    message = Message(sender_id=sender.id, content=filename, is_file=True)
    db.session.add(message)
    db.session.commit()

    emit("file_message", {
        "msg_id": message.id,
        "username": username,
        "filename": filename,
        "timestamp": message.timestamp.strftime("%H:%M")
    }, broadcast=True)

# ------------------ RUN ------------------

if __name__ == "__main__":
    socketio.run(app, debug=True, use_reloader=False)
