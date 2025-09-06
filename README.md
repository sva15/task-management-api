# Task Management API

A simple FastAPI-based task management system demonstrating DevSecOps best practices with comprehensive testing and security scanning.

## Features

- **CRUD Operations**: Create, read, update, and delete tasks
- **Task Filtering**: Filter by completion status and priority
- **Task Statistics**: Get summary statistics of all tasks
- **Input Validation**: Comprehensive request validation using Pydantic
- **Error Handling**: Proper HTTP status codes and error messages
- **Type Safety**: Full type hints and mypy compatibility

## API Endpoints

### Core Endpoints
- `GET /` - API information
- `GET /health` - Health check

### Task Management
- `POST /tasks` - Create a new task
- `GET /tasks` - Get all tasks (with optional filtering)
- `GET /tasks/{task_id}` - Get a specific task
- `PUT /tasks/{task_id}` - Update a task
- `DELETE /tasks/{task_id}` - Delete a task

### Statistics
- `GET /tasks/stats/summary` - Get task statistics

## Quick Start

### Prerequisites
- Python 3.8 or higher
- pip package manager

### Installation

1. **Clone or navigate to the project directory**:
   ```bash
   cd C:\Users\svara\Downloads\Terraform_In_3_days\Task-mgm-flask
   ```

2. **Create a virtual environment**:
   ```bash
   python -m venv venv
   
   # Windows
   venv\Scripts\activate
   
   # Linux/Mac
   source venv/bin/activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   pip install -r requirements-dev.txt
   ```

### Running the Application

1. **Start the development server**:
   ```bash
   uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
   ```

2. **Access the API**:
   - API: http://localhost:8000
   - Interactive docs: http://localhost:8000/docs
   - ReDoc: http://localhost:8000/redoc

### Example Usage

```bash
# Create a task
curl -X POST "http://localhost:8000/tasks" \
     -H "Content-Type: application/json" \
     -d '{"title": "Learn DevSecOps", "priority": "high"}'

# Get all tasks
curl "http://localhost:8000/tasks"

# Get task statistics
curl "http://localhost:8000/tasks/stats/summary"
```

## Development

### Running Tests

```bash
# Run all tests with coverage
pytest

# Run specific test file
pytest tests/test_main.py

# Run with verbose output
pytest -v

# Generate HTML coverage report
pytest --cov=src --cov-report=html
```

### Code Quality Checks

```bash
# Format code
black .
isort .

# Check formatting (without changes)
black --check .
isort --check-only .

# Lint code
flake8 .

# Type checking
mypy .
```

### Security Scanning

```bash
# Dependency vulnerability scanning
pip-audit
safety check

# SAST scanning
bandit -r .

# Secret scanning (requires gitleaks)
gitleaks detect
```

## DevSecOps Pipeline

This project includes a comprehensive GitHub Actions workflow that runs:

### Code Quality
- **Black**: Code formatting
- **isort**: Import sorting
- **flake8**: Linting and style checks
- **mypy**: Static type checking

### Testing
- **pytest**: Unit tests with coverage reporting
- **Coverage threshold**: 90% minimum

### Security Scanning
- **bandit**: SAST (Static Application Security Testing)
- **safety**: Dependency vulnerability scanning
- **pip-audit**: Modern dependency auditing
- **gitleaks**: Secret detection
- **SonarQube**: Code quality and security analysis (on main branch)

### Workflow Triggers
- **Feature branches**: Full validation on every push
- **Pull requests**: Complete pipeline with PR comments
- **Main branch**: Includes SonarQube analysis

## Project Structure

```
frontend/
├── src/
│   ├── __init__.py
│   └── main.py              # FastAPI application
├── tests/
│   ├── __init__.py
│   └── test_main.py         # Comprehensive test suite
├── .github/
│   └── workflows/
│       └── ci-cd.yml        # DevSecOps pipeline
├── requirements.txt         # Production dependencies
├── requirements-dev.txt     # Development dependencies
├── pyproject.toml          # Tool configurations
└── README.md               # This file
```

## Configuration

All tool configurations are centralized in `pyproject.toml`:

- **pytest**: Test discovery and coverage settings
- **black**: Code formatting rules
- **isort**: Import sorting configuration
- **mypy**: Type checking settings
- **bandit**: Security scanning options
- **flake8**: Linting configuration

## API Documentation

The API automatically generates interactive documentation:

- **Swagger UI**: Available at `/docs`
- **ReDoc**: Available at `/redoc`
- **OpenAPI Schema**: Available at `/openapi.json`

## Task Model

```json
{
  "id": "uuid4-string",
  "title": "Task title (1-100 chars)",
  "description": "Optional description (max 500 chars)",
  "priority": "low|medium|high",
  "completed": false,
  "created_at": "2024-01-15T10:30:00",
  "updated_at": "2024-01-15T10:30:00"
}
```

## Error Handling

The API returns appropriate HTTP status codes:

- `200` - Success
- `201` - Created
- `204` - No Content (for deletions)
- `404` - Not Found
- `422` - Validation Error

Error responses include detailed messages:

```json
{
  "detail": "Task with id abc123 not found"
}
```

## Testing Strategy

The test suite covers:

- **All endpoints** with success and error cases
- **Input validation** with edge cases
- **Business logic** and data integrity
- **Error handling** and HTTP status codes
- **Unicode support** and special characters
- **Concurrent operations** simulation
- **Statistics calculations** accuracy

## Security Considerations

- **Input validation** using Pydantic models
- **No SQL injection** (using in-memory storage)
- **Type safety** with comprehensive type hints
- **Dependency scanning** for known vulnerabilities
- **Secret scanning** to prevent credential leaks
- **SAST analysis** for security anti-patterns

## Performance Notes

- **In-memory storage** for simplicity (not production-ready)
- **Async endpoints** for better concurrency
- **Efficient filtering** with list comprehensions
- **Proper HTTP caching** headers where applicable

## Contributing

1. Create a feature branch from `develop`
2. Make changes with comprehensive tests
3. Ensure all DevSecOps checks pass
4. Create a pull request to `develop`
5. Address any feedback from code review
6. Merge after approval and passing CI/CD

## License

This project is for educational purposes demonstrating DevSecOps best practices.
