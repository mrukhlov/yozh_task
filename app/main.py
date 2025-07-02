"""Main FastAPI application entry point."""

from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi

from app.api import auth, comment, task, user
from app.config import settings


def custom_openapi():
    """Custom OpenAPI schema with enhanced documentation."""
    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema = get_openapi(
        title=settings.title,
        version=settings.version,
        description=(
            "# Task Management API\n\n"
            "A comprehensive FastAPI-based task management system with user "
            "authentication, task CRUD operations, commenting, and assignment "
            "features.\n\n"
            "## Features\n\n"
            "- ✅ User authentication with JWT tokens\n"
            "- ✅ Create, read, update, and delete tasks\n"
            "- ✅ Assign tasks to other users\n"
            "- ✅ Mark tasks as completed\n"
            "- ✅ Comment on tasks\n"
            "- ✅ PostgreSQL database integration\n\n"
            "## Authentication\n\n"
            "This API uses JWT (JSON Web Tokens) for authentication. To access "
            "protected endpoints:\n\n"
            "1. Register a new user using `POST /auth/register`\n"
            "2. Login using `POST /auth/login` to get an access token\n"
            "3. Include the token in the Authorization header: "
            "`Bearer <your_token>`\n\n"
            "## Example Usage\n\n"
            "### Register a new user:\n"
            "```json\n"
            "{\n"
            '  "email": "user@example.com",\n'
            '  "username": "testuser",\n'
            '  "password": "password123"\n'
            "}\n"
            "```\n\n"
            "### Login:\n"
            "```json\n"
            "{\n"
            '  "username": "user@example.com",\n'
            '  "password": "password123"\n'
            "}\n"
            "```\n\n"
            "### Create a task:\n"
            "```json\n"
            "{\n"
            '  "title": "Complete project documentation",\n'
            '  "description": "Write comprehensive documentation for the new feature",\n'  # noqa: E501
            '  "priority": "high"\n'
            "}\n"
            "```\n\n"
            "## Environment Variables\n\n"
            "The API uses the following environment variables:\n"
            "- `base_url`: http://localhost:8060 (for local development)\n"
            "- `access_token`: JWT token obtained after login\n\n"
            "## Testing\n\n"
            "You can test this API using the included Postman collection:\n"
            "- Import `Task_Management_API.postman_collection.json`\n"
            "- Import `Task_Management_API_Local.postman_environment.json`\n"
            '- Set the environment to "Task Management API - Local"\n'
            "- Start with the Authentication endpoints"
        ),
        routes=app.routes,
    )

    # Add contact information
    openapi_schema["info"]["contact"] = {
        "name": "API Support",
        "email": "support@example.com",
    }

    # Add license information
    openapi_schema["info"]["license"] = {
        "name": "MIT License",
        "url": "https://opensource.org/licenses/MIT",
    }

    # Add servers
    openapi_schema["servers"] = [
        {"url": "http://localhost:8060", "description": "Local Development Server"},
        {"url": "http://localhost:8000", "description": "Default Development Server"},
    ]

    # Add security schemes
    openapi_schema["components"]["securitySchemes"] = {
        "BearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
            "description": "JWT token obtained from /auth/login endpoint",
        }
    }

    app.openapi_schema = openapi_schema
    return app.openapi_schema


app = FastAPI(
    title=settings.title,
    description=settings.description,
    version=settings.version,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

# Set custom OpenAPI schema
app.openapi = custom_openapi  # type: ignore

# Routers
app.include_router(auth.router)
app.include_router(user.router)
app.include_router(task.router)
app.include_router(comment.router)


# Health check
@app.get("/ping", tags=["health"])
def ping():
    """
    Health check endpoint to verify API status.

    Returns:
        dict: Simple response indicating the API is running
    """
    return {"message": "pong"}
