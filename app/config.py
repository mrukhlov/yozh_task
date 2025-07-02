"""Configuration settings for the application."""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings."""

    # Database
    database_url: str = "postgresql://postgres:password@localhost:5432/task_management"

    # Individual database settings (for Docker Compose)
    postgres_db: str = "task_management"
    postgres_user: str = "postgres"
    postgres_password: str = "password"
    db_port: str = "5432"  # External port for host access
    postgres_host: str = "localhost"

    # JWT
    secret_key: str = "your-secret-key-here-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    # API
    title: str = "Task Management System"
    description: str = "A comprehensive task management API with user authentication"
    version: str = "1.0.0"

    # Application
    app_host: str = "0.0.0.0"
    app_port: int = 8000
    app_port_host: str = "8000"  # For Docker Compose
    debug: bool = True

    @property
    def get_database_url(self) -> str:
        """Get database URL, preferring Docker environment variables."""
        if hasattr(self, "postgres_host") and self.postgres_host != "localhost":
            # Use Docker environment variables - always use port 5432 for internal
            return (
                f"postgresql://{self.postgres_user}:{self.postgres_password}"
                f"@{self.postgres_host}:5432/{self.postgres_db}"
            )
        else:
            # Use the default database_url
            return self.database_url

    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
