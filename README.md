# ChatSpace — Real-Time Messaging App

ChatSpace is a real-time messaging application built with **Python, Flask, and Socket.IO**, backed by **PostgreSQL** and scaled with a **Redis** message queue. It is fully containerized with Docker and deploys to Kubernetes.

## Features

- Real-time messaging with Socket.IO (Redis-backed message queue for multi-replica scaling)
- User registration and login (hashed passwords)
- Public room messages, direct messages, and @mentions with notifications
- Message reactions (toggleable emoji), edit, and delete
- Typing indicators and user online status
- User profiles with avatar upload (png/jpg/jpeg/pdf/txt, 5MB limit)
- File sharing in chat (base64 upload, stored server-side)
- Production-ready Gunicorn + Eventlet configuration
- Docker Compose support for local development
- Kubernetes manifests for cluster deployment (app, PostgreSQL, Redis)

## Architecture

| Component  | Technology                     | Purpose                                      |
|------------|--------------------------------|----------------------------------------------|
| Web app    | Flask 3 + Flask-SocketIO       | HTTP routes + WebSocket events (eventlet)    |
| Database   | PostgreSQL 16 (SQLAlchemy)     | Users, messages, reactions                   |
| Queue      | Redis 7                        | Socket.IO message queue (multi-replica safe) |
| Server     | Gunicorn (eventlet worker)     | WSGI/ASGI production serving                 |

## Requirements

**Local development:**
- Python 3.11+, pip, virtualenv

**Containerized:**
- Docker, Docker Compose

**Kubernetes:**
- A running cluster (tested with kind)
- kubectl configured against the cluster

## Quick Start with Docker Compose

1. **Create a `.env` file** in the project root:

   SECRET_KEY=your-secret-key
   POSTGRES_USER=chatuser
   POSTGRES_PASSWORD=your-password
   POSTGRES_DB=chatapp
text
 
  
 
 

2. **Build and start:**

 
 

   docker compose up --build
text
 
  
 
 

This starts three containers: `chat-app`, `chat-db` (PostgreSQL), and `chat-redis` (Redis queue).

3. **Open** http://localhost:5000

To stop:

 
 

docker compose down
text
 
  
 
 

## Local Development Without Docker

 
 

python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
python app.py
text
 
  
 
 

Create the same `.env` file as above. Requires a local PostgreSQL (and Redis for the SocketIO queue) or running them via `docker compose up db redis`.

The app listens on http://localhost:5000.

## Kubernetes Deployment

Manifests live in `k8k/`:

| File                    | Resource                                  |
|-------------------------|-------------------------------------------|
| `postgres.yml`          | PostgreSQL StatefulSet                    |
| `postgres-service.yml`  | PostgreSQL headless Service               |
| `redis.yml`             | Redis Deployment + Service (message queue)|
| `deployment.yml`        | Chat app Deployment (init containers wait for Postgres and Redis) |
| `service.yml`           | NodePort Service (80 -> 30080)            |
| `secret.yml`            | App secrets (placeholders only!)          |

### 1. Configure secrets (recommended)

 
 

kubectl create secret generic chat-secrets --from-literal=SECRET_KEY=your-secret-key
  --from-literal=POSTGRES_USER=chatuser --from-literal=POSTGRES_PASSWORD=your-password
  --from-literal=POSTGRES_DB=chatapp
text
 
  
 
 

If you use `k8k/secret.yml`, it must contain placeholders only — never real credentials.

### 2. Deploy the stack

 
 

kubectl apply -f k8k/postgres.yml
kubectl apply -f k8k/postgres-service.yml
kubectl apply -f k8k/redis.yml
kubectl apply -f k8k/deployment.yml
kubectl apply -f k8k/service.yml
text
 
  
 
 

### 3. Load the app image into a kind cluster

The deployment uses `imagePullPolicy: IfNotPresent` with a locally built image, so the image must exist inside the cluster node.

With the kind CLI:

 
 

kind load docker-image chatspacereal-timemessagingapp-app:latest --name <cluster-name>
text
 
  
 
 

Without the kind CLI (manual, node name `desktop-control-plane`):

 
 

docker save -o chat-app.tar chatspacereal-timemessagingapp-app:latest
docker cp chat-app.tar desktop-control-plane:/chat-app.tar
docker exec desktop-control-plane ctr --namespace=k8s.io images import /chat-app.tar
text
 
  
 
 

### 4. Verify

 
 

kubectl get pods
kubectl get svc
kubectl rollout status deployment/chat
text
 
  
 
 

All three pods (`chat`, `postgres-0`, `redis`) should reach `Running` and `1/1 Ready`.

### 5. Access the app

kind does not expose NodePorts to the host by default. Use port-forwarding:

 
 

kubectl port-forward svc/chat-app 5000:80
text
 
  
 
 

Then open http://localhost:5000 (keep the terminal open while testing).

## Configuration

All configuration is via environment variables:

| Variable           | Description                                  | Default                |
|--------------------|----------------------------------------------|------------------------|
| `SECRET_KEY`       | Flask secret key                             | `dev_secret_key`       |
| `POSTGRES_USER`    | PostgreSQL username                          | `postgres`             |
| `POSTGRES_PASSWORD`| PostgreSQL password                          | `postgres`             |
| `POSTGRES_HOST`    | PostgreSQL host                              | `localhost`            |
| `POSTGRES_PORT`    | PostgreSQL port                              | `5432`                 |
| `POSTGRES_DB`      | PostgreSQL database name                     | `chatapp`              |
| `REDIS_URL`        | Redis URL for the SocketIO message queue     | `redis://localhost:6379/0` |

Keep `.env` files and production credentials out of source control.

## Production Checklist

- Run behind HTTPS with an ingress controller or reverse proxy for TLS termination.
- Use Kubernetes Secrets (or a dedicated secret manager) for credentials.
- Use persistent volumes for PostgreSQL data.
- Mount a persistent volume for `uploads/` if uploaded files must survive pod recreation.
- Scale the app with `replicas > 1` — the Redis message queue keeps Socket.IO events consistent across pods.
- Sticky sessions at the ingress/proxy layer are recommended for Socket.IO with multiple replicas.

## Security Notes

- Never commit `.env` files or real database credentials.
- `k8k/secret.yml` must contain placeholders only.
- User uploads are stored outside Git (`uploads/` is ignored).
- Uploads are restricted by extension and 5MB size limit.

## License

Private project. Add an appropriate license before distributing or open-sourcing.
