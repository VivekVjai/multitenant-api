Multi-Tenant E-Commerce API (Django + PostgreSQL + Docker + Azure)

A production-ready multi-tenant e-commerce backend API built using Django + PostgreSQL, containerized with Docker, deployed to Azure App Service, and fully automated using CI/CD with GitHub Actions.

This project demonstrates real-world backend engineering practices including:

Multi-tenancy (tenant-aware models)

Containerized deployment

Cloud database + secure connection handling

CI/CD pipeline automation

Production environment configuration

Live Health Check (Azure)

✅ API Health Endpoint:

GET /health/


Expected response:

{
  "status": "ok",
  "db": "connected"
}

🧱 Tech Stack

Backend: Django (Python)

Database: PostgreSQL (Azure PostgreSQL)

Containerization: Docker + Docker Hub

Cloud Deployment: Azure App Service (Linux Docker Container)

CI/CD: GitHub Actions

Web Server: Gunicorn

📌 Features

✅ Multi-tenant architecture
✅ Tenant-aware indexing & constraints
✅ Health endpoint for production monitoring
✅ Dockerized Django production build
✅ Azure deployment-ready environment setup
✅ GitHub Actions pipeline:

runs tests

checks migrations

builds Docker image

pushes to Docker Hub

deploys to Azure automatically

⚙️ Environment Variables

The API uses environment variables for configuration.

Example .env:

DJANGO_ENV=dev
DJANGO_SECRET_KEY=your-secret-key
DJANGO_DEBUG=1
DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1

DB_NAME=postgres
DB_USER=postgres
DB_PASSWORD=postgres
DB_HOST=localhost
DB_PORT=5432

PAYMENT_WEBHOOK_SECRET=super-secret-key

🐳 Run Locally (Docker)
1️⃣ Clone Repo
git clone https://github.com/VivekVjai/multitenant-api.git
cd multitenant-api

2️⃣ Build and Run
docker compose up --build

3️⃣ Run Migrations
docker compose exec web python manage.py migrate

4️⃣ Test API
http://127.0.0.1:8000/health/

🧪 Run Tests (CI Style)
python manage.py test

🔄 CI/CD Pipeline (GitHub Actions)

This project includes a full CI/CD pipeline located at:

.github/workflows/ci-cd.yml


Pipeline steps:

✅ CI

Spin up PostgreSQL service

Install dependencies

Check migrations

Run migrations

Run tests

✅ CD

Build Docker image

Push to Docker Hub

Deploy container to Azure Web App

☁️ Deployment (Azure)

Deployed using:

Azure App Service

Docker Hub container

Environment variables configured inside Azure Portal

Important Azure env var:

WEBSITES_PORT=8000

🔐 Security Notes

This repository does NOT contain:

❌ .env
❌ passwords
❌ Azure publish profiles
❌ API secrets

All secrets are stored in:

GitHub Actions Secrets

Azure Web App Environment Variables

👨‍💻 Author

Vivek
🔗 GitHub: https://github.com/VivekVjai

📌 Project Repo: https://github.com/VivekVjai/multitenant-api
