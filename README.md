ChatSpace - Real-Time Messaging App

ChatSpace is a lightweight real-time messaging application built with Python, Flask, and Socket.IO. The application is fully containerized with Docker and can be deployed to Kubernetes for production or cluster-based environments.

Features
Real-time messaging with Socket.IO
User registration and login
File upload support
PostgreSQL database backend
Production server using Gunicorn and Eventlet
Docker Compose support for local development
Kubernetes manifests for cluster deployment
Project Structure
.
├── app.py                         # Application entrypoint, routes, and Socket.IO events
├── templates/                     # HTML templates
│   ├── login.html
│   ├── register.html
│   └── dashboard.html
├── uploads/                       # User-uploaded files (ignored by Git)
├── instance/                      # Application instance data (ignored by Git)
├── k8k/                           # Kubernetes manifests
│   ├── deployment.yml
│   ├── service.yml
│   ├── postgres.yml
│   ├── postgres-service.yml
│   └── secret.yml
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── .env                           # Local environment variables (ignored by Git)
└── README.md

Requirements

For local development:

Python 3.11+
pip
A virtual environment

For containerized development:

Docker
Docker Compose

For Kubernetes deployment:

A Kubernetes cluster
kubectl configured for the target cluster
Quick Start with Docker Compose

Docker Compose is the recommended way to run ChatSpace locally.

1. Create the environment file

Create a .env file in the project root:

SECRET_KEY=your-secret-key
POSTGRES_USER=chatuser
POSTGRES_PASSWORD=your-password
POSTGRES_DB=chatapp


Use a strong, unique value for SECRET_KEY and a secure PostgreSQL password.

2. Build and start the application
docker compose up --build


Docker Compose will build the application image and start the required services.

3. Open the application

Once the containers are running, open:

http://localhost:5000


To stop the application:

docker compose down

Local Development Without Docker
1. Create a virtual environment

On Windows PowerShell:

python -m venv venv
.\venv\Scripts\Activate.ps1


On Linux/macOS:

python3 -m venv venv
source venv/bin/activate

2. Install dependencies
pip install -r requirements.txt

3. Configure environment variables

Create a .env file in the project root with the required application and PostgreSQL settings:

SECRET_KEY=your-secret-key
POSTGRES_USER=chatuser
POSTGRES_PASSWORD=your-password
POSTGRES_DB=chatapp

4. Start the application
python app.py


The application should then be available at:

http://localhost:5000

Kubernetes Deployment

The k8k/ directory contains the Kubernetes resources required to deploy ChatSpace and its PostgreSQL database.

1. Configure Secrets

Do not commit real credentials to Git.

The preferred approach is to create the Kubernetes Secret directly:

kubectl create secret generic chat-secrets \
  --from-literal=SECRET_KEY=your-secret-key \
  --from-literal=POSTGRES_USER=chatuser \
  --from-literal=POSTGRES_PASSWORD=your-password \
  --from-literal=POSTGRES_DB=chatapp


If k8k/secret.yml is included in the repository, keep it limited to placeholders or non-sensitive example values.

2. Deploy PostgreSQL
kubectl apply -f k8k/postgres.yml
kubectl apply -f k8k/postgres-service.yml

3. Deploy the application
kubectl apply -f k8k/deployment.yml
kubectl apply -f k8k/service.yml

4. Check the deployment

View the deployed resources:

kubectl get pods
kubectl get services
kubectl get deployments


To inspect application logs:

kubectl logs -l app=chatspace


The exact label selector may vary depending on the labels defined in k8k/deployment.yml.

Updating the Application

After making application changes, rebuild the Docker image and restart the Compose environment:

docker compose up --build


For Kubernetes, build and publish the updated image to the registry configured by the deployment manifest, then restart or update the deployment as required.

For example:

kubectl rollout restart deployment/chatspace


Check the rollout status with:

kubectl rollout status deployment/chatspace

Security Notes
Never commit .env files containing real credentials.
Never commit real database passwords or application secrets.
Keep uploads/ out of Git unless uploaded files are intentionally part of the project.
Keep instance/ out of Git when it contains local or runtime data.
Use Kubernetes Secrets for sensitive configuration.
Use strong, unique values for SECRET_KEY and database credentials.
For production deployments, place the application behind HTTPS using an ingress controller or reverse proxy with TLS.
Review file-upload handling carefully before exposing the application publicly.
Redis / Socket.IO Scaling

If the application uses Redis as a Socket.IO message queue, Redis should be documented and deployed as an additional service.

This is particularly important when running multiple ChatSpace application replicas: Socket.IO events need a shared message queue so that clients connected to different application instances can receive real-time events correctly.

If Redis is not present in the current Dockerfile, docker-compose.yml, or Kubernetes manifests, it should not be documented as a required component.

License

This project is intended for private use.

If you plan to distribute the application, add an appropriate open-source or proprietary license.

:::

One important correction: I would **not claim Redis is used** unless it actually appears in the application/configuration. The old “Redis-backed SocketIO queue” text sounds like leftover documentation, so the README above treats Redis as conditional rather than falsely documenting it as part of the current deployment.
