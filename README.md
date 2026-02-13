# 🚀 Task Management API

<div align="center">

![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)
![Python](https://img.shields.io/badge/python-3.11-blue.svg?style=for-the-badge&logo=python&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-316192?style=for-the-badge&logo=postgresql&logoColor=white)
![Docker](https://img.shields.io/badge/docker-%230db7ed.svg?style=for-the-badge&logo=docker&logoColor=white)

**A production-ready REST API for task and project management built with FastAPI, PostgreSQL, and modern best practices.**

[Live API](https://task-management-api-a775.onrender.com/docs) • [Documentation](#-api-documentation) • [Features](#-features) • [Quick Start](#-getting-started)

</div>

---

## 📖 Table of Contents

- [Overview](#-overview)
- [Features](#-features)
- [Tech Stack](#tech-stack)
- [Live Demo](#-live-demo)
- [Project Structure](#-project-structure)
- [API Documentation](#-api-documentation)
- [Getting Started](#-getting-started)
  - [Prerequisites](#prerequisites)
  - [Local Setup](#local-setup)
  - [Docker Setup](#docker-setup)
- [Environment Variables](#-environment-variables)
- [Database Schema](#database-schema)
- [API Endpoints](#-api-endpoints)
- [Testing](#-testing)
- [Deployment](#-deployment)
- [Contributing](#-contributing)

---

## 🌟 Overview

**Task Management API** is a full-featured, production-ready REST API that provides comprehensive task and project management capabilities. Built with **FastAPI** and **PostgreSQL**, it implements modern authentication, advanced filtering, and follows industry best practices for scalability and security.

### Why This API?

- ✅ **Production-Ready**: Fully tested, documented, and deployed
- ✅ **Secure**: JWT authentication with refresh tokens, password hashing, email verification
- ✅ **Scalable**: Async database operations, connection pooling, rate limiting
- ✅ **Well-Documented**: Interactive Swagger UI, comprehensive code comments
- ✅ **Modern Stack**: FastAPI, SQLAlchemy 2.0, Pydantic v2, Docker
- ✅ **Best Practices**: Clean architecture, repository pattern, type hints

---

## ✨ Features

### 🔐 Authentication & Security
- **JWT-based authentication** with access and refresh tokens
- **Password hashing** using bcrypt
- **Email verification** system
- **Password reset** flow with time-limited tokens
- **Rate limiting** to prevent abuse and brute force attacks
- **CORS** configuration for frontend integration

### 📝 Task Management
- **Full CRUD operations** for tasks
- **Advanced filtering** by status, priority, category, and date range
- **Full-text search** in title and description
- **Pagination** with total count and page info
- **Task statistics** (total, by status, overdue count)
- **Due date tracking** with overdue detection
- **Priority levels**: LOW, MEDIUM, HIGH, URGENT
- **Status tracking**: TODO, IN_PROGRESS, COMPLETED, ARCHIVED

### 🏷️ Category Management
- **Custom categories** with color coding
- **Category-based filtering**
- **Task count per category**
- **Unique category names** per user

### 📊 Monitoring & Performance
- **Performance metrics** tracking
- **Request/response logging**
- **Processing time headers**
- **Health check endpoint** with database connectivity
- **Slow request detection**

### 👥 User Management
- **User registration** with validation
- **Profile management** (view, update, delete)
- **Password updates**
- **Account deletion**

---

## 🛠️ Tech Stack

### Backend Framework
- **[FastAPI](https://fastapi.tiangolo.com/)** - Modern, fast web framework for building APIs
- **[Uvicorn](https://www.uvicorn.org/)** - Lightning-fast ASGI server

### Database
- **[PostgreSQL](https://www.postgresql.org/)** - Powerful, open-source relational database
- **[SQLAlchemy 2.0](https://www.sqlalchemy.org/)** - ORM with async support
- **[Alembic](https://alembic.sqlalchemy.org/)** - Database migration tool
- **[asyncpg](https://github.com/MagicStack/asyncpg)** - Fast PostgreSQL driver for Python

### Authentication & Security
- **[python-jose](https://python-jose.readthedocs.io/)** - JWT token generation/validation
- **[passlib](https://passlib.readthedocs.io/)** - Password hashing with bcrypt
- **[SlowAPI](https://github.com/laurents/slowapi)** - Rate limiting

### Validation
- **[Pydantic v2](https://docs.pydantic.dev/)** - Data validation and settings management
- **[email-validator](https://github.com/JoshData/python-email-validator)** - Email validation

### Testing
- **[pytest](https://pytest.org/)** - Testing framework
- **[pytest-asyncio](https://pytest-asyncio.readthedocs.io/)** - Async test support
- **[httpx](https://www.python-httpx.org/)** - Async HTTP client for testing
- **[Faker](https://faker.readthedocs.io/)** - Fake data generation

### DevOps
- **[Docker](https://www.docker.com/)** - Containerization
- **[Render](https://render.com/)** - Cloud deployment platform
- **[Neon](https://neon.tech/)** - Serverless PostgreSQL

---

## 🌐 Live Demo

### API Base URL
```
https://task-management-api-a775.onrender.com
```

### Interactive Documentation
- **Swagger UI**: [https://task-management-api-a775.onrender.com/docs](https://task-management-api-a775.onrender.com/docs)
- **ReDoc**: [https://task-management-api-a775.onrender.com/redoc](https://task-management-api-a775.onrender.com/redoc)

### Health Check
```bash
curl https://task-management-api-a775.onrender.com/health
```

### Quick Test
```bash
# Register a user
curl -X POST "https://task-management-api-a775.onrender.com/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "username": "testuser",
    "password": "securepass123"
  }'

# Login
curl -X POST "https://task-management-api-a775.onrender.com/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "password": "securepass123"
  }'
```

---

## 📁 Project Structure
```
task_management_api/
├── app/
│   ├── __init__.py
│   ├── main.py                      # FastAPI application & middleware
│   ├── config.py                    # Settings & environment variables
│   ├── database.py                  # Database connection & session
│   │
│   ├── models/                      # SQLAlchemy ORM models
│   │   ├── __init__.py
│   │   ├── user.py                  # User model
│   │   ├── task.py                  # Task model with enums
│   │   └── category.py              # Category model
│   │
│   ├── schemas/                     # Pydantic request/response schemas
│   │   ├── __init__.py
│   │   ├── user.py                  # User schemas
│   │   ├── task.py                  # Task schemas
│   │   ├── category.py              # Category schemas
│   │   ├── token.py                 # Token schemas
│   │   └── common.py                # Common response schemas
│   │
│   ├── repositories/                # Data access layer
│   │   ├── __init__.py
│   │   ├── base.py                  # Base repository with CRUD
│   │   ├── user_repository.py       # User data operations
│   │   ├── task_repository.py       # Task data operations
│   │   └── category_repository.py   # Category data operations
│   │
│   ├── services/                    # Business logic layer
│   │   ├── __init__.py
│   │   ├── auth_service.py          # Authentication logic
│   │   ├── user_service.py          # User management logic
│   │   ├── task_service.py          # Task management logic
│   │   └── category_service.py      # Category management logic
│   │
│   ├── api/                         # API routes
│   │   ├── __init__.py
│   │   ├── deps.py                  # Dependency injection
│   │   └── v1/
│   │       ├── __init__.py
│   │       ├── router.py            # Main API router
│   │       ├── auth.py              # Authentication endpoints
│   │       ├── users.py             # User endpoints
│   │       ├── tasks.py             # Task endpoints
│   │       └── categories.py        # Category endpoints
│   │
│   ├── core/                        # Core utilities
│   │   ├── __init__.py
│   │   ├── security.py              # JWT & password hashing
│   │   ├── exceptions.py            # Custom exceptions
│   │   ├── rate_limiter.py          # Rate limiting config
│   │   ├── monitoring.py            # Performance monitoring
│   │   └── logging_config.py        # Logging configuration
│   │
│   └── utils/                       # Helper functions
│       ├── __init__.py
│       └── email.py                 # Email utilities
│
├── tests/                           # Test suite
│   ├── __init__.py
│   ├── conftest.py                  # Test fixtures
│   ├── test_auth.py                 # Authentication tests
│   ├── test_users.py                # User tests
│   ├── test_tasks.py                # Task tests
│   ├── test_categories.py           # Category tests
│   ├── test_rate_limiting.py        # Rate limit tests
│   ├── test_monitoring.py           # Monitoring tests
│   └── test_error_handling.py       # Error handling tests
│
├── alembic/                         # Database migrations
│   ├── versions/                    # Migration files
│   ├── env.py                       # Alembic environment
│   └── script.py.mako               # Migration template
│
├── logs/                            # Application logs (gitignored)
├── .env                             # Environment variables (gitignored)
├── .env.example                     # Environment template
├── .gitignore                       # Git ignore rules
├── alembic.ini                      # Alembic configuration
├── Dockerfile                       # Docker configuration
├── docker-compose.yml               # Docker Compose for local dev
├── render.yaml                      # Render deployment config
├── requirements.txt                 # Python dependencies
├── README.md                        # This file
└── DEPLOYMENT.md                    # Deployment guide
```

---

## 📚 API Documentation

### Base URL
```
https://task-management-api-a775.onrender.com/api/v1
```

### Authentication
All endpoints except authentication and public endpoints require a JWT token.

**Include in headers:**
```
Authorization: Bearer <your_access_token>
```

### Response Format

**Success Response:**
```json
{
  "message": "Operation successful",
  "data": { ... }
}
```

**Error Response:**
```json
{
  "detail": "Error description",
  "errors": {
    "field": "Specific error message"
  }
}
```

### Rate Limits

| Endpoint Type | Limit | Purpose |
|--------------|-------|---------|
| Authentication | 3-10/min | Prevent brute force |
| Standard | 30/min | Normal operations |
| Global | 100/min | Overall protection |

Rate limit info in headers:
- `X-RateLimit-Limit`: Maximum requests
- `X-RateLimit-Remaining`: Remaining requests
- `X-RateLimit-Reset`: Reset time

---

## 🔌 API Endpoints

### 🔐 Authentication (`/api/v1/auth`)

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/register` | Register new user | ❌ |
| POST | `/login` | Login user | ❌ |
| POST | `/refresh` | Refresh access token | ❌ |
| POST | `/password-reset/request` | Request password reset | ❌ |
| POST | `/password-reset/confirm` | Confirm password reset | ❌ |
| POST | `/verify-email` | Verify email address | ❌ |
| POST | `/resend-verification` | Resend verification email | ❌ |
| GET | `/me` | Get current user info | ✅ |
| POST | `/logout` | Logout user | ✅ |

<details>
<summary><b>📋 Authentication Examples</b></summary>

**Register User:**
```bash
curl -X POST "https://task-management-api-a775.onrender.com/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "username": "johndoe",
    "password": "securepass123",
    "full_name": "John Doe"
  }'
```

**Login:**
```bash
curl -X POST "https://task-management-api-a775.onrender.com/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "johndoe",
    "password": "securepass123"
  }'
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer"
}
```

</details>

---

### 👤 Users (`/api/v1/users`)

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/me` | Get own profile | ✅ |
| PUT | `/me` | Update own profile | ✅ |
| PUT | `/me/password` | Update password | ✅ |
| DELETE | `/me` | Delete account | ✅ |
| GET | `/{user_id}` | Get user by ID | ✅ |

<details>
<summary><b>📋 User Examples</b></summary>

**Get Profile:**
```bash
curl -X GET "https://task-management-api-a775.onrender.com/api/v1/users/me" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**Update Profile:**
```bash
curl -X PUT "https://task-management-api-a775.onrender.com/api/v1/users/me" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "full_name": "John Updated Doe",
    "email": "newemail@example.com"
  }'
```

</details>

---

### ✅ Tasks (`/api/v1/tasks`)

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/` | Create new task | ✅ |
| GET | `/` | Get tasks (with filters) | ✅ |
| GET | `/{task_id}` | Get task by ID | ✅ |
| PUT | `/{task_id}` | Update task | ✅ |
| DELETE | `/{task_id}` | Delete task | ✅ |
| PATCH | `/{task_id}/status` | Update task status | ✅ |
| PATCH | `/{task_id}/priority` | Update task priority | ✅ |
| GET | `/overdue` | Get overdue tasks | ✅ |
| GET | `/statistics` | Get task statistics | ✅ |

**Query Parameters for GET `/`:**
- `skip`: Number of records to skip (default: 0)
- `limit`: Max records to return (default: 10, max: 100)
- `status`: Filter by status (TODO, IN_PROGRESS, COMPLETED, ARCHIVED)
- `priority`: Filter by priority (LOW, MEDIUM, HIGH, URGENT)
- `category_id`: Filter by category UUID
- `search`: Search in title and description
- `due_date_from`: Filter by due date (from)
- `due_date_to`: Filter by due date (to)

<details>
<summary><b>📋 Task Examples</b></summary>

**Create Task:**
```bash
curl -X POST "https://task-management-api-a775.onrender.com/api/v1/tasks/" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Complete project documentation",
    "description": "Write comprehensive docs for the API",
    "status": "TODO",
    "priority": "HIGH",
    "due_date": "2024-12-31T23:59:59"
  }'
```

**Get Tasks with Filters:**
```bash
curl -X GET "https://task-management-api-a775.onrender.com/api/v1/tasks/?status=TODO&priority=HIGH&limit=10" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**Response:**
```json
{
  "items": [
    {
      "id": "123e4567-e89b-12d3-a456-426614174000",
      "title": "Complete project documentation",
      "description": "Write comprehensive docs for the API",
      "status": "TODO",
      "priority": "HIGH",
      "due_date": "2024-12-31T23:59:59",
      "category_id": null,
      "user_id": "456e7890-e89b-12d3-a456-426614174000",
      "is_overdue": false,
      "created_at": "2024-02-14T10:00:00",
      "updated_at": "2024-02-14T10:00:00"
    }
  ],
  "total": 15,
  "page": 1,
  "page_size": 10,
  "total_pages": 2
}
```

**Search Tasks:**
```bash
curl -X GET "https://task-management-api-a775.onrender.com/api/v1/tasks/?search=documentation" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**Get Statistics:**
```bash
curl -X GET "https://task-management-api-a775.onrender.com/api/v1/tasks/statistics" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**Response:**
```json
{
  "total": 45,
  "by_status": {
    "todo": 12,
    "in_progress": 8,
    "completed": 20,
    "archived": 5
  },
  "overdue": 3
}
```

</details>

---

### 🏷️ Categories (`/api/v1/categories`)

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/` | Create category | ✅ |
| GET | `/` | Get all categories | ✅ |
| GET | `/{category_id}` | Get category by ID | ✅ |
| PUT | `/{category_id}` | Update category | ✅ |
| DELETE | `/{category_id}` | Delete category | ✅ |
| GET | `/{category_id}/stats` | Get category stats | ✅ |

<details>
<summary><b>📋 Category Examples</b></summary>

**Create Category:**
```bash
curl -X POST "https://task-management-api-a775.onrender.com/api/v1/categories/" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Work",
    "color": "#FF5733"
  }'
```

**Get All Categories:**
```bash
curl -X GET "https://task-management-api-a775.onrender.com/api/v1/categories/" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**Get Category Stats:**
```bash
curl -X GET "https://task-management-api-a775.onrender.com/api/v1/categories/{category_id}/stats" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**Response:**
```json
{
  "category": {
    "id": "789e0123-e89b-12d3-a456-426614174000",
    "name": "Work",
    "color": "#FF5733",
    "user_id": "456e7890-e89b-12d3-a456-426614174000",
    "created_at": "2024-02-14T10:00:00",
    "updated_at": "2024-02-14T10:00:00"
  },
  "task_count": 12
}
```

</details>

---

### 📊 Monitoring

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/health` | Health check | ❌ |
| GET | `/metrics` | Performance metrics | ❌ |
| POST | `/metrics/reset` | Reset metrics | ❌ |

---

## 🚀 Getting Started

### Prerequisites

- **Python 3.11+**
- **PostgreSQL 14+** (or Neon account)
- **Git**
- **Docker** (optional, for containerized development)

### Local Setup

#### 1️⃣ Clone Repository
```bash
git clone https://github.com/YOUR_USERNAME/task-management-api.git
cd task-management-api
```

#### 2️⃣ Create Virtual Environment

**Windows (PowerShell):**
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

**macOS/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

#### 3️⃣ Install Dependencies
```bash
pip install -r requirements.txt
```

#### 4️⃣ Set Up Environment Variables
```bash
# Copy example environment file
cp .env.example .env

# Edit .env with your configuration
# Windows: notepad .env
# macOS/Linux: nano .env
```

**Generate SECRET_KEY:**
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

#### 5️⃣ Set Up Database

**Option A: Local PostgreSQL**
```bash
# Create database
psql -U postgres
CREATE DATABASE task_management_dev;
CREATE USER task_admin WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE task_management_dev TO task_admin;
\q
```

**Option B: Neon (Serverless PostgreSQL)**
1. Sign up at [neon.tech](https://neon.tech)
2. Create new project
3. Copy connection string to `.env`

#### 6️⃣ Run Database Migrations
```bash
alembic upgrade head
```

#### 7️⃣ Start Development Server
```bash
uvicorn app.main:app --reload
```

**API will be available at:**
- **API**: http://localhost:8000
- **Docs**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

---

### Docker Setup

#### 1️⃣ Using Docker Compose (Includes PostgreSQL)
```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

#### 2️⃣ Using Dockerfile Only
```bash
# Build image
docker build -t task-management-api .

# Run container
docker run -p 8000:8000 \
  -e DATABASE_URL="your_database_url" \
  -e SECRET_KEY="your_secret_key" \
  task-management-api
```

---

## 🔧 Environment Variables

Create a `.env` file in the project root:
```bash
# Database
DATABASE_URL=postgresql+asyncpg://user:password@host:5432/dbname?ssl=require
DATABASE_URL_SYNC=postgresql://user:password@host:5432/dbname?sslmode=require

# Security
SECRET_KEY=your-secret-key-min-32-characters
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=15
REFRESH_TOKEN_EXPIRE_DAYS=7

# Application
APP_NAME=Task Management API
APP_VERSION=1.0.0
DEBUG=False
ENVIRONMENT=production

# CORS
BACKEND_CORS_ORIGINS=["https://your-frontend.com"]

# Rate Limiting
RATE_LIMIT_PER_MINUTE=100
AUTH_RATE_LIMIT_PER_MINUTE=5

# Email (Optional)
SMTP_TLS=True
SMTP_PORT=587
SMTP_HOST=smtp.gmail.com
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
EMAILS_FROM_EMAIL=noreply@taskmanagement.com
EMAILS_FROM_NAME=Task Management API
```

See `.env.example` for complete list.

---

## 🗄️ Database Schema

### Entity Relationship Diagram
```
┌─────────────────────┐
│       USERS         │
├─────────────────────┤
│ id (UUID, PK)       │
│ email (unique)      │
│ username (unique)   │
│ hashed_password     │
│ is_active           │
│ is_verified         │
│ full_name           │
│ created_at          │
│ updated_at          │
└─────────────────────┘
         │ 1
         │
         │ N
┌────────┴────────────────────┐
│        │                    │
│ 1      │               1    │
│        │                    │
│ N      │                    │ N
┌────────▼────────┐  ┌────────▼────────┐
│   CATEGORIES    │  │      TASKS      │
├─────────────────┤  ├─────────────────┤
│ id (UUID, PK)   │  │ id (UUID, PK)   │
│ name            │  │ title           │
│ color           │  │ description     │
│ user_id (FK)    │  │ status (enum)   │
│ created_at      │  │ priority (enum) │
│ updated_at      │  │ due_date        │
└─────────────────┘  │ user_id (FK)    │
         │ 1         │ category_id(FK) │
         │           │ created_at      │
         │ N         │ updated_at      │
         └───────────┤ is_overdue      │
                     └─────────────────┘
```

### Models

**User Model:**
- UUID primary key
- Email and username (unique, indexed)
- Password (hashed with bcrypt)
- Active and verified status
- Timestamps

**Task Model:**
- UUID primary key
- Title and description
- Status: TODO, IN_PROGRESS, COMPLETED, ARCHIVED
- Priority: LOW, MEDIUM, HIGH, URGENT
- Optional due date
- Foreign keys: user_id, category_id
- Computed field: is_overdue

**Category Model:**
- UUID primary key
- Name (unique per user)
- Color (hex code)
- Foreign key: user_id

---

## 🧪 Testing

### Run Tests
```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run with coverage
pytest --cov=app tests/

# Run specific test file
pytest tests/test_auth.py -v

# Generate HTML coverage report
pytest --cov=app --cov-report=html tests/
```

### Test Coverage

Current coverage: **~87%**
```
tests/test_auth.py ............................   33%
tests/test_users.py .......                       47%
tests/test_tasks.py ........................      78%
tests/test_categories.py ............              90%
tests/test_rate_limiting.py ...                   93%
tests/test_monitoring.py .....                    98%
tests/test_error_handling.py ....                100%

======================== 85 passed in 18.45s ========================
```

---

## 🚢 Deployment

### Deploy to Render

1. **Push to GitHub:**
```bash
git push origin main
```

2. **Create Web Service on Render:**
   - Connect GitHub repository
   - Runtime: Docker
   - Region: Choose nearest
   - Plan: Free

3. **Set Environment Variables** in Render dashboard

4. **Deploy:**
   - Automatic deployment on git push
   - Manual deploy option available

### Deploy to Other Platforms

<details>
<summary><b>Heroku</b></summary>
  
```bash
# Install Heroku CLI
# Login
heroku login

# Create app
heroku create your-app-name

# Add PostgreSQL
heroku addons:create heroku-postgresql:mini

# Set environment variables
heroku config:set SECRET_KEY=your_secret_key

# Deploy
git push heroku main
```

</details>

<details>
<summary><b>AWS (EC2 + RDS)</b></summary>

1. Create RDS PostgreSQL instance
2. Launch EC2 instance
3. Install Docker
4. Pull and run container
5. Configure security groups
6. Set up domain and SSL

</details>

<details>
<summary><b>DigitalOcean</b></summary>

1. Create PostgreSQL database
2. Create App Platform app
3. Connect GitHub repository
4. Set environment variables
5. Deploy

</details>


---

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. **Fork the repository**
2. **Create a feature branch:**
```bash
   git checkout -b feature/amazing-feature
```
3. **Make your changes and commit:**
```bash
   git commit -m "Add amazing feature"
```
4. **Push to your fork:**
```bash
   git push origin feature/amazing-feature
```
5. **Open a Pull Request**

### Contribution Guidelines

- Follow PEP 8 style guide
- Add tests for new features
- Update documentation
- Keep commits atomic and descriptive

---

## 👨‍💻 Author

**Your Name**

- GitHub: [ravigupta97](https://github.com/ravigupta97)
- LinkedIn: [Ravi Gupta](https://www.linkedin.com/in/ravigupta97)
- Email: gupta_ravi@outlook.in

---

## 🙏 Acknowledgments

- [FastAPI](https://fastapi.tiangolo.com/) - Amazing web framework
- [SQLAlchemy](https://www.sqlalchemy.org/) - Powerful ORM
- [Pydantic](https://docs.pydantic.dev/) - Data validation
- [Render](https://render.com/) - Easy deployment
- [Neon](https://neon.tech/) - Serverless PostgreSQL

---

## 📞 Support

If you have any questions or need help:

- 💬 **Issues**: [GitHub Issues](https://github.com/your-username/task-management-api/issues)
- 📖 **Documentation**: [API Docs](https://task-management-api-a775.onrender.com/docs)

---

<div align="center">

**Built with ❤️ using FastAPI and PostgreSQL**

[⬆ Back to Top](#-task-management-api)

</div>
