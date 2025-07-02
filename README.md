# Task Management System

A comprehensive FastAPI-based task management system with user authentication, task CRUD operations, commenting, and assignment features.

## Features

- ✅ User authentication with JWT tokens
- ✅ Create, read, update, and delete tasks
- ✅ Assign tasks to other users
- ✅ Mark tasks as completed
- ✅ Comment on tasks
- ✅ PostgreSQL database integration
- ✅ Docker and docker-compose setup
- ✅ Comprehensive API documentation (Swagger)
- ✅ Unit tests with pytest

## Quick Start

### Using Docker Compose & Makefile (Recommended)

1. Clone the repository:
```bash
git clone <repository-url>
cd test_task_1
```

2. Build and start the application:
```bash
make docker-build
make docker-run
```

3. Access the application:
- API: http://localhost:8060
- Swagger Documentation: http://localhost:8060/docs

4. To stop the application:
```bash
make docker-stop
```

5. To view logs:
```bash
make docker-logs
```

### Testing with Postman

A comprehensive Postman collection and environment are included in the repository for easy API testing:

#### Setup Instructions:

1. **Import the Environment:**
   - Open Postman
   - Click "Environments" in the left sidebar
   - Click "Import" button
   - Select `Task_Management_API_Local.postman_environment.json`
   - The environment will be added to your environments list

2. **Import the Collection:**
   - Click "Collections" in the left sidebar
   - Click "Import" button
   - Select `Task_Management_API.postman_collection.json`
   - The collection will be added to your collections list

3. **Set the Environment:**
   - In the top-right corner of Postman, select "Task Management API - Local" from the environment dropdown
   - This ensures all requests use the correct base URL and variables

4. **Test the API:**
   - Start with the "Authentication" folder
   - First run "Register User" to create an account
   - Then run "Login User" - this will automatically set the `access_token` variable
   - All subsequent requests will use Bearer token authorization automatically

#### Included Files:
- `Task_Management_API.postman_collection.json` - Complete API collection with all endpoints
- `Task_Management_API_Local.postman_environment.json` - Local environment with variables

#### Environment Variables:
- `base_url`: `http://localhost:8060` (your Docker app port)
- `access_token`: Automatically populated after login
- `user_email`: `user@example.com`
- `user_password`: `password123`
- `admin_email`: `admin@example.com`
- `admin_password`: `admin123`

#### Features:
- **Automatic Authorization**: All requests automatically include Bearer token
- **Environment Variables**: Easy to switch between different environments
- **Pre-configured Requests**: All endpoints with example data
- **Test Scripts**: Login automatically captures and stores the access token

### Manual Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Set up environment variables:
```bash
# Copy the example environment file
cp .env.example .env

# Edit .env file with your configuration
# The file contains all necessary environment variables
```

3. Run database migrations:
```bash
alembic upgrade head
```

4. Start the application:
```bash
uvicorn app.main:app --reload
```

## API Endpoints

### Authentication
- `POST /auth/register` - Register a new user
- `POST /auth/login` - Login and get JWT token

### Users
- `GET /users/me` - Get current user profile
- `GET /users/` - Get all users (admin only)

### Tasks
- `GET /tasks/` - Get all tasks (with filtering)
- `POST /tasks/` - Create a new task
- `GET /tasks/{task_id}` - Get specific task
- `PUT /tasks/{task_id}` - Update task
- `DELETE /tasks/{task_id}` - Delete task
- `POST /tasks/{task_id}/complete` - Mark task as completed
- `POST /tasks/{task_id}/assign` - Assign task to user

### Comments
- `GET /tasks/{task_id}/comments` - Get task comments
- `POST /tasks/{task_id}/comments` - Add comment to task
- `PUT /comments/{comment_id}` - Update comment
- `DELETE /comments/{comment_id}` - Delete comment

## Testing

Run the test suite:
```bash
pytest
```

Run tests with coverage:
```bash
pytest --cov=app
```

## Database Schema

The application uses the following main tables:
- `users` - User accounts and authentication
- `tasks` - Task information and status
- `comments` - Task comments
- `task_assignments` - Task assignments to users

## Environment Variables

All environment variables are configured in the `.env` file. Copy `.env.example` to `.env` and customize as needed:

### Database Configuration
- `POSTGRES_DB` - Database name
- `POSTGRES_USER` - Database user
- `POSTGRES_PASSWORD` - Database password
- `DATABASE_URL` - Full PostgreSQL connection string
- `DB_PORT` - Database port for Docker (host mapping)

### JWT Configuration
- `SECRET_KEY` - JWT secret key (change in production!)
- `ALGORITHM` - JWT algorithm (default: HS256)
- `ACCESS_TOKEN_EXPIRE_MINUTES` - JWT token expiration time

### Application Configuration
- `APP_HOST` - Application host (default: 0.0.0.0)
- `APP_PORT` - Application port (default: 8000)
- `APP_PORT_HOST` - Application port for Docker (host mapping)
- `DEBUG` - Debug mode (default: true)

## Development

### Code Style
The project follows PEP 8 standards and uses:
- Black for code formatting
- isort for import sorting
- flake8 for linting

### CI/CD Pipeline

This project uses GitHub Actions for continuous integration and deployment:

#### Workflows:

1. **Test Workflow** (`.github/workflows/test.yml`)
   - Runs on every pull request and push to main/master
   - Installs dependencies with Poetry
   - Runs linting (black, isort, flake8)
   - Runs type checking (mypy)
   - Runs tests with coverage
   - Uploads coverage to Codecov

2. **CI/CD Pipeline** (`.github/workflows/ci-cd.yml`)
   - Runs on push to main/master only
   - Includes all test workflow steps
   - Builds and pushes Docker image to GitHub Container Registry
   - Runs Docker container tests
   - Performs security scanning with Trivy
   - Deploys to production (configurable)

#### Features:
- **Multi-Python Testing**: Tests against Python 3.11 and 3.12
- **Dependency Caching**: Caches Poetry dependencies for faster builds
- **Docker Integration**: Builds and tests Docker containers
- **Security Scanning**: Vulnerability scanning with Trivy
- **Coverage Reporting**: Code coverage tracking with Codecov
- **Container Registry**: Automatic Docker image publishing to GHCR

#### Badges:
- Test status: Shows if tests are passing
- CI/CD status: Shows if the full pipeline is successful
- Code coverage: Shows test coverage percentage

### Project Structure
```
app/
├── __init__.py
├── main.py              # FastAPI application entry point
├── config.py            # Configuration settings
├── database.py          # Database connection and session
├── models/              # SQLAlchemy models
├── schemas/             # Pydantic schemas
├── api/                 # API routes
├── core/                # Core functionality (auth, security)
└── tests/               # Test files
```

## License

MIT License
