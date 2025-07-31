HEAD
# LIBRARY-BPMN_Graph_Transformation

# 📚 Flask API Project Documentation

## 📋 Table of Contents

- [Project Overview](#-project-overview)
- [Architecture](#-architecture)
- [Folder Structure](#-folder-structure)
- [Getting Started](#-getting-started)
  - [With Make](#with-make)
  - [Without Make](#without-make)
- [API Endpoints](#-api-endpoints)
- [Development Workflow](#-development-workflow)
- [Testing](#-testing)
- [Deployment](#-deployment)
- [Common Issues](#-common-issues)

## 🔍 Project Overview

This project is a RESTful API built with Flask and MongoDB, designed with a clean architecture approach to separate concerns. The API currently manages blog posts with full CRUD operations, proper validation, error handling, and logging.

### Key Features

- **Layered Architecture**: Separating API controllers, business logic, data access, and infrastructure
- **MongoDB Integration**: Using PyMongo for document storage
- **Error Handling**: Comprehensive exception handling with proper HTTP status codes
- **Validation**: Request data validation
- **Logging**: Structured logging throughout the application
- **Health Checks**: Endpoints for API and database health monitoring

## 🏗️ Architecture

The project follows a clean architecture design with clear separation of concerns:

![Architecture Diagram](https://mermaid.ink/img/pako:eNqFkUFrwzAMhf-K8TUdBDp22GGw0cGgO-xUhjGMYDuOptvJsCMllP73OemSQgc7GL3npw_JQmcVEkpo9cEgFGawy_1AniVMfXQDi4xk0LLBLMGxcehJaV2KOOPYe1jCvN6mj3v2YhzsjEhqbzgnGIZu5LHztELvdgjfBYL19WtZlk2nQFHPMheJgprE8fPR97RDz5rNe1P1b5ajCySF-r9ofa0MK44T3iUo4WKsY_xCpzHEeEKhT8hseS7leYkl9No6KUHrTsoKnMJRkVEq6HmittAB5oQlUc8rUN0ZF0dqY7KIp13KcDuXbnva2vF88Q_rpJkK?type=png)

1. **API Layer**: Handles HTTP requests/responses and routes
2. **Service Layer**: Implements business logic and validation
3. **Repository Layer**: Handles data access operations
4. **Infrastructure**: Manages database connections, configurations, and other technical concerns

## 📂 Folder Structure

```
project-root/
├── app/
│   ├── api/
│   │   └── v1/
│   │       ├── check_controller.py    # Health/debug endpoints
│   │       ├── post_controller.py     # Post CRUD endpoints
│   │       └── routes.py              # Route registration
│   ├── core/
│   │   ├── models/                    # Domain models/entities
│   │   ├── repositories/
│   │   │   └── post_repository.py     # Database access for posts
│   │   ├── schemas/
│   │   │   └── post_schema.py         # Validation schemas
│   │   ├── parsers/
│   │   │   └── parser.py              # Parser logic
│   │   └── services/
│   │       └── post_service.py        # Business logic for posts
│   ├── infrastructure/
│   │   ├── config/                    # App configuration
│   │   └── db/
│   │       └── mongo_client.py        # MongoDB connection
│   └── utils/
│       ├── exceptions/                # Custom exceptions
│       └── logger.py                  # Logging utility
├── tests/                             # Test files
├── main.py                            # Application entry point
├── .env.example                       # Example env vars
├── Makefile                           # Automation commands
└── requirements.txt                   # Dependencies
```

### Detailed Component Descriptions

#### 🌐 `app/api/`

Contains all HTTP-related code organized by API versions (v1, v2, etc.)

- **Controllers**: Handle HTTP requests/responses, status codes, and calling appropriate services
- **Routes**: Register API endpoints with Flask blueprints

#### 🧠 `app/core/`

Contains the application's business logic and domain models

- **Models**: Domain entities representing business objects (Post, User, etc.)
- **Repositories**: Data access layer with CRUD operations for each entity
- **Schemas**: Validation logic for request/response data
- - **Paarsers**: Parser logic for Syntactic Analysis data
- **Services**: Business logic implementation that orchestrates operations between controllers and repositories

#### 🔧 `app/infrastructure/`

Technical implementations that support the application

- **Config**: Environment-specific configurations
- **DB**: Database connections and configurations

#### 🛠️ `app/utils/`

Shared utilities used throughout the application

- **Exceptions**: Custom exception classes for business, validation, and technical errors
- **Logger**: Centralized logging configuration

#### 🧪 `tests/`

Unit and integration tests organized to mirror the application structure

## 🚦 Getting Started

### With Make

The project includes a Makefile for common operations:

1. **Clone the Repository**

   ```bash
   git clone https://github.com/your-username/your-repo.git
   cd your-repo
   ```

2. **Setup Environment Variables**

   ```bash
   cp .env.example .env
   # Edit .env with your settings
   ```

3. **Create Python Environment and Install Dependencies**

   ```bash
   make env
   make upgrade
   ```

4. **Run Development Server**
   ```bash
   make dev
   ```

### Without Make

If you're not using make, here are the manual commands:

1. **Clone the Repository**

   ```bash
   git clone https://github.com/your-username/your-repo.git
   cd your-repo
   ```

2. **Setup Environment Variables**

   ```bash
   cp .env.example .env
   # Edit .env with your settings
   ```

3. **Create Python Virtual Environment**

   **Linux/Mac**

   ```bash
   python -m venv .venv
   source .venv/bin/activate
   pip install --upgrade pip setuptools wheel
   pip install -r requirements.txt
   ```

   **Windows (CMD)**

   ```cmd
   python -m venv .venv
   .venv\Scripts\activate
   pip install --upgrade pip setuptools wheel
   pip install -r requirements.txt
   ```

   **Windows (PowerShell)**

   ```powershell
   python -m venv .venv
   .\.venv\Scripts\Activate
   pip install --upgrade pip setuptools wheel
   pip install -r requirements.txt
   ```

4. **Run Development Server**

   **Linux/Mac**

   ```bash
   source .venv/bin/activate
   export FLASK_APP=main.py
   export FLASK_ENV=development
   export FLASK_DEBUG=1
   flask run --host=0.0.0.0 --port=5000
   ```

   **Windows (CMD)**

   ```cmd
   .venv\Scripts\activate
   set FLASK_APP=main.py
   set FLASK_ENV=development
   set FLASK_DEBUG=1
   flask run --host=0.0.0.0 --port=5000
   ```

   **Windows (PowerShell)**

   ```powershell
   .\.venv\Scripts\Activate
   $env:FLASK_APP = "main.py"
   $env:FLASK_ENV = "development"
   $env:FLASK_DEBUG = 1
   flask run --host=0.0.0.0 --port=5000
   ```

## 🌐 API Endpoints

### Health and Debug Endpoints

- **GET** `/api/v1/check/health`

  - Checks API and database health
  - Returns status information

- **GET** `/api/v1/check/debug`
  - Returns request debug information
  - Useful for troubleshooting

### Post Endpoints

- **POST** `/api/v1/posts/`

  - Creates a new post
  - Requires `title` and `content` in JSON body

- **GET** `/api/v1/posts/{post_id}`

  - Gets a post by ID
  - Returns 404 if not found

- **PUT** `/api/v1/posts/{post_id}`

  - Updates an existing post
  - Requires `title` and `content` in JSON body
  - Returns 404 if not found

- **DELETE** `/api/v1/posts/{post_id}`
  - Deletes a post by ID
  - Returns 404 if not found

## 👨‍💻 Development Workflow

### Code Organization Principles

1. **Separation of Concerns**

   - Controllers handle HTTP requests/responses
   - Services handle business logic
   - Repositories handle data access
   - Each layer has a single responsibility

2. **Error Handling**

   - Business errors (ValidationError) return 422
   - Not found errors return 404
   - Database errors return appropriate error codes
   - Unhandled exceptions return 500

3. **Validation**
   - Input validation in schema layer
   - Business validation in service layer

### Adding a New Feature

1. **Create Repository** (data access)

   - Implement CRUD operations
   - Handle database-specific errors

2. **Create Schema** (validation)

   - Define input validation rules

3. **Create Service** (business logic)

   - Use repository for data access
   - Implement business rules

4. **Create Controller** (API endpoints)

   - Define routes and HTTP methods
   - Handle HTTP-specific concerns

5. **Register Routes** in `routes.py`
   - Add your new blueprint

## 🧪 Testing

### With Make

```bash
make test
```

### Without Make

#### Linux/Mac

```bash
source .venv/bin/activate
export PYTHONPATH=.
pytest --cov=app tests/
```

#### Windows (CMD)

```cmd
.venv\Scripts\activate
set PYTHONPATH=.
pytest --cov=app tests/
```

#### Windows (PowerShell)

```powershell
.\.venv\Scripts\Activate
$env:PYTHONPATH = "."
pytest --cov=app tests/
```

## 🚀 Deployment

### Production with Gunicorn

#### With Make

```bash
make run
```

#### Without Make

##### Linux/Mac

```bash
source .venv/bin/activate
export PYTHONPATH=.
gunicorn --bind 0.0.0.0:5000 --workers 4 'main:app'
```

##### Windows

For Windows, it's recommended to use waitress instead of gunicorn:

```cmd
.venv\Scripts\activate
set PYTHONPATH=.
pip install waitress
waitress-serve --port=5000 main:app
```

### Docker Deployment

1. **Build the Docker image**

   ```bash
   docker build -t flask-api .
   ```

2. **Run the container**
   ```bash
   docker run -p 5000:5000 -e MONGO_URI=your_mongo_uri flask-api
   ```

## 🔧 Common Issues

### Environment Variable Issues

- Make sure all required environment variables are set in `.env`
- Check for environment-specific issues (e.g., development vs. production)

### Database Connection Problems

- Verify MongoDB is running and accessible
- Check connection string in `.env`
- Ensure network connectivity between API and database

### Import Errors

- Make sure PYTHONPATH includes the project root
- Check for circular imports

---

## 📝 Project Design Patterns

This project uses several design patterns:

1. **Repository Pattern**: Abstracts data access operations
2. **Service Layer Pattern**: Encapsulates business logic
3. **Factory Pattern**: Used in app creation (create_app)
4. **Dependency Injection**: Services receive repositories as dependencies

## 🔄 Data Flow

1. HTTP request arrives → Controller
2. Controller parses request → calls Service
3. Service validates input (Schema) → processes business logic
4. Service calls Repository for data access
5. Repository interacts with database
6. Results flow back up the chain
7. Controller formats HTTP response

---

Happy coding! 🎉
 0d354bf (feat(json-graph): add BPMN JSON to Neo4j graph conversion module)
