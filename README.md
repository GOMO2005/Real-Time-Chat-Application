ChatSpace — Real-Time Messaging App

ChatSpace is a lightweight real-time messaging application built with Python, Flask, and Socket.IO. The application is fully containerized with Docker and can be deployed to Kubernetes.

Features
Real-time messaging with Socket.IO
User registration and login
File upload support
Database-backed application
Production-ready Gunicorn + Eventlet configuration
Docker Compose support for local development
Kubernetes manifests for cluster deployment
Requirements

For local development:

Python 3.11+
pip
A virtual environment

For containerized development:

Docker
Docker Compose

For Kubernetes deployment:

A running Kubernetes cluster
kubectl configured to access the cluster
Quick Start with Docker Compose

Docker Compose is the recommended way to run ChatSpace locally.

1. Create the environment file

Create a .env file in the project root:

SECRET_KEY=your-secret-key
POSTGRES_USER=chatuser
POSTGRES_PASSWORD=your-password
POSTGRES_DB=chatapp

2. Build and start the application
docker compose up --build

3. Open the application

Once the containers are running, open:

http://localhost:5000


To stop the application:

docker compose down

Local Development Without Docker
1. Create a virtual environment
python -m venv venv

2. Activate the virtual environment
.\venv\Scripts\Activate.ps1

3. Install dependencies
pip install -r requirements.txt

4. Configure environment variables

Create a .env file in the project root using the variables described in the Docker Compose section.

5. Start the application
python app.py


The application should then be available at:

http://localhost:5000

Kubernetes Deployment

The Kubernetes configuration can be deployed using the manifests in the k8k/ directory.

1. Configure secrets

Do not commit real credentials to Git.

The recommended approach is to create the Kubernetes secret directly:

kubectl create secret generic chat-secrets `
  --from-literal=SECRET_KEY=your-secret-key `
  --from-literal=POSTGRES_USER=chatuser `
  --from-literal=POSTGRES_PASSWORD=your-password `
  --from-literal=POSTGRES_DB=chatapp


If k8k/secret.yml is committed to the repository, make sure it contains placeholders only and never real production credentials.

2. Deploy PostgreSQL
kubectl apply -f k8k/postgres.yml
kubectl apply -f k8k/postgres-service.yml

3. Deploy the application
kubectl apply -f k8k/deployment.yml
kubectl apply -f k8k/service.yml

4. Check the deployment
kubectl get pods
kubectl get services
kubectl get deployments

Configuration

ChatSpace uses environment variables for application and database configuration.

Variable	Description
SECRET_KEY	Secret key used by the Flask application
POSTGRES_USER	PostgreSQL username
POSTGRES_PASSWORD	PostgreSQL password
POSTGRES_DB	PostgreSQL database name

Keep .env files and production credentials out of source control.

Production

The application is configured to support a production deployment using Gunicorn with Eventlet.

For production deployments, it is recommended to:

Run the application behind HTTPS.
Use an ingress controller or reverse proxy for TLS termination.
Store secrets using Kubernetes Secrets or another secure secret-management system.
Use persistent storage for PostgreSQL data.
Configure persistent storage for uploaded files if uploads need to survive pod recreation.
Avoid committing credentials or other sensitive configuration to Git.
Security Notes
Never commit .env files containing real credentials.
Never commit real database passwords or application secrets.
Keep user-uploaded content out of Git.
k8k/secret.yml should contain placeholders only if it is committed to the repository.
Use HTTPS in production.
Use persistent volumes for stateful data in Kubernetes.
License

This project is intended for private use.

If you plan to distribute or open-source the project, add an appropriate license before doing so.
