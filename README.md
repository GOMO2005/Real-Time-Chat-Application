# ChatSpace — Real-Time Messaging App

Lightweight real-time chat app built with Python. This folder contains the server entrypoint and simple template pages for auth and dashboard.

## Project structure

- `app.py` — application entrypoint (starts the web server, handles routes and real-time messaging).
- `Templates/` — HTML templates: `login.html`, `register.html`, `dashboard.html`.
- `uploads/` — directory for user-uploaded files (avatars, attachments).

## Requirements

- Python 3.8+
- Common dependencies: `Flask`, `Flask-SocketIO` (or similar). Add a `requirements.txt` if you plan to share or deploy.

## Setup

1. (Optional) Create and activate a virtual environment:

   python -m venv venv
   venv\Scripts\activate

2. Install dependencies (create `requirements.txt` if missing):

   pip install flask flask-socketio

## Configuration

- Check `app.py` for any configuration values (host, port, secret keys, upload folder). Set environment variables or edit a config section if present.
- Ensure `uploads/` exists and is writable by the app process.

## Running

Run the app from the project root:

```
python app.py
```

By default the server will bind to the host/port defined in `app.py`. If `Flask` is used with environment variables, you might run:

```
set FLASK_APP=app.py
set FLASK_ENV=development
flask run
```

## Notes

- If the app uses Socket.IO, confirm the client code in `dashboard.html` matches the server-side socket namespace and events.
- Review `Templates/` to update UI, or add static assets in a `static/` folder if needed.
- For production deployment, use a WSGI server (e.g., Gunicorn) and a proper Socket.IO worker configuration.

## Next steps

- Add `requirements.txt` and an `.env.example` file for configuration values.
- Add instructions for deploying with Docker or a process manager.

## License

Choose a license or keep for private use.
