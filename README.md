# Contacts REST API
 
A RESTful API for managing personal contacts, built with FastAPI, PostgreSQL, Redis, and Docker.
 
## Features
 
- User registration and authentication via JWT tokens
- Email verification on signup
- Password reset via email
- Role-based access control (`user` / `admin`)
- Redis caching for authenticated user sessions
- Contact management: create, read, update, delete, search
- Upcoming birthday lookup (next 7 days)
- Avatar upload via Cloudinary (admin only)
- Rate limiting with SlowAPI
- Auto-generated HTML documentation with Sphinx
- Test coverage 89% (pytest + pytest-cov)
---
 
## Tech Stack
 
- **Python 3.13**
- **FastAPI** — web framework
- **PostgreSQL 15** — primary database
- **SQLAlchemy + Alembic** — ORM and migrations
- **Redis 7** — caching layer
- **Docker + Docker Compose** — containerization
- **Cloudinary** — avatar image storage
- **fastapi-mail** — transactional email (Gmail SMTP)
- **Sphinx** — API documentation
- **pytest** — testing
---
 
## Project Structure
 
```
├── src/
│   ├── api/             # Route handlers (auth, contacts, users, utils)
│   ├── conf/            # App configuration (settings from .env)
│   ├── core/            # Rate limiter
│   ├── database/        # SQLAlchemy models and DB session
│   ├── repository/      # Database access layer
│   ├── schemas.py       # Pydantic schemas
│   └── services/        # Business logic (auth, email, redis, cloudinary)
├── tests/               # Unit and integration tests
├── docs/                # Sphinx documentation
├── migrations/          # Alembic migration files
├── main.py              # Application entry point
├── Dockerfile
├── docker-compose.yml
└── requirements.txt
```
 
---
 
## Getting Started
 
### Prerequisites
 
- Docker and Docker Compose installed
- A Gmail account with an [App Password](https://myaccount.google.com/apppasswords)
- A [Cloudinary](https://cloudinary.com) account (for avatar uploads)
### 1. Clone the repository
 
```bash
git clone https://github.com/your-username/goit-pythonweb-hw-012.git
cd goit-pythonweb-hw-012
```
 
### 2. Create `.env` file
 
Copy the example below and fill in your values:
 
```dotenv
# Database
DB_URL=postgresql+asyncpg://postgres:your_password@db:5432/contacts_db_hw12
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your_password
POSTGRES_DB=contacts_db_hw12
 
# Auth
SECRET_KEY=your_secret_key
ALGORITHM=HS256
 
# Redis
REDIS_URL=redis://redis:6379
 
# Email (Gmail + App Password)
MAIL_USERNAME=your_email@gmail.com
MAIL_PASSWORD=your_16char_app_password
MAIL_FROM=your_email@gmail.com
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=465
MAIL_FROM_NAME=Contacts App
 
# Cloudinary
CLOUDINARY_NAME=your_cloud_name
CLOUDINARY_API_KEY=your_api_key
CLOUDINARY_API_SECRET=your_api_secret
```
 
> **Note:** Never commit your real `.env` file to version control.
 
### 3. Run with Docker Compose
 
```bash
docker compose up -d --build
```
 
This will start three containers:
- `contacts_db_hw12` — PostgreSQL database
- `redis_cache` — Redis
- `fastapi_app` — FastAPI application (runs migrations automatically on startup)
The API will be available at **http://localhost:8000**
 
### 4. Interactive API docs
 
Open **http://localhost:8000/docs** in your browser (Swagger UI).
 
---
 
## Running Locally (without Docker)
 
### 1. Install dependencies
 
```bash
pip install -r requirements.txt
```
 
### 2. Set up `.env`
 
Use `localhost` instead of service names:
 
```dotenv
DB_URL=postgresql+asyncpg://postgres:your_password@localhost:5432/contacts_db_hw12
REDIS_URL=redis://localhost:6379
```
 
### 3. Run migrations
 
```bash
alembic upgrade head
```
 
### 4. Start the server
 
```bash
uvicorn main:app --reload
```
 
---
 
## API Endpoints
 
### Auth
 
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/auth/signup` | Register a new user |
| POST | `/api/auth/login` | Login and get JWT token |
| GET | `/api/auth/verify/{token}` | Verify email address |
| POST | `/api/auth/forgot-password` | Request password reset email |
| GET | `/api/auth/reset-password-confirm/{token}` | Validate reset token |
| POST | `/api/auth/reset-password` | Set new password |
 
### Contacts
 
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/contacts/` | List all contacts |
| POST | `/api/contacts/` | Create a contact |
| GET | `/api/contacts/{id}` | Get a contact by ID |
| PUT | `/api/contacts/{id}` | Update a contact |
| DELETE | `/api/contacts/{id}` | Delete a contact |
| GET | `/api/contacts/search?query=` | Search contacts |
| GET | `/api/contacts/birthdays` | Upcoming birthdays |
 
### Users
 
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/users/me` | Get current user profile |
| PATCH | `/api/users/avatar` | Update avatar (admin only) |
| GET | `/api/users/admin/all-users` | List all users (admin only) |
 
---
 
## Running Tests
 
```bash
pytest --cov=src --cov-report=term-missing
```
 
Current coverage: **89%**
 
---
 
## Building Documentation
 
```bash
sphinx-apidoc -o docs/source src --implicit-namespaces
sphinx-build -b html docs/source docs/build/html
```
 
Open `docs/build/html/index.html` in your browser.
 
---
 
## Environment Variables Reference
 
| Variable | Description |
|----------|-------------|
| `DB_URL` | Async PostgreSQL connection string |
| `SECRET_KEY` | JWT signing secret |
| `ALGORITHM` | JWT algorithm (default: HS256) |
| `REDIS_URL` | Redis connection URL |
| `MAIL_USERNAME` | Gmail address for sending emails |
| `MAIL_PASSWORD` | Gmail App Password (16 characters) |
| `MAIL_FROM` | Sender email address |
| `MAIL_SERVER` | SMTP server (default: smtp.gmail.com) |
| `MAIL_PORT` | SMTP port (default: 465) |
| `CLOUDINARY_NAME` | Cloudinary cloud name |
| `CLOUDINARY_API_KEY` | Cloudinary API key |
| `CLOUDINARY_API_SECRET` | Cloudinary API secret |
 
---
 
## Author
 
Project Author: GoIT Neoversity 
Student: Olha Fursova
