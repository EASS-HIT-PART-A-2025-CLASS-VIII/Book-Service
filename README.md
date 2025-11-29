# Book Service API
A simple REST API for managing a book collection, built with FastAPI.

## Features
- Create, read, update, and delete books
- In-memory storage (no database required)
- Full test coverage with pytest
- Interactive API documentation (Swagger UI)
- Docker support for easy deployment

## Book Model
Each book has the following fields:
- `id` (integer) - Unique identifier (auto-generated)
- `title` (string) - Book title
- `author` (string) - Book author
- `genre` (string) - Book genre
- `rating` (float, optional) - Rating between 0-10

## Installation
### Prerequisites
- Python 3.11+
- uv (Python package manager)
- Docker (optional, for containerized deployment)

### Setup
1. Clone the repository and navigate to the project directory:
```bash
cd ~/projects/book-service
```

2. Install dependencies:
```bash
uv sync
```

## Running the API
### Option 1: Run locally with uv
Start the development server:
```bash
uv run uvicorn app.main:app --reload
```
The API will be available at: `http://localhost:8000`

### Option 2: Run with Docker
1. Build the Docker image:
```bash
docker build -t book-service .
```

2. Run the container:
```bash
docker run -p 8000:8000 book-service
```

3. Stop the container:
Press `Ctrl+C` in the terminal

The API will be available at: `http://localhost:8000`

### API Documentation
Once the server is running, visit:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## API Endpoints
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Welcome message |
| GET | `/books` | Get all books |
| GET | `/books/{id}` | Get a specific book |
| POST | `/books` | Create a new book |
| PUT | `/books/{id}` | Update a book |
| DELETE | `/books/{id}` | Delete a book |

## Example Usage
### Create a book:
```bash
curl -X POST "http://localhost:8000/books" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "1984",
    "author": "George Orwell",
    "genre": "Dystopian",
    "rating": 9.0
  }'
```

### Get all books:
```bash
curl "http://localhost:8000/books"
```

### Get a specific book:
```bash
curl "http://localhost:8000/books/1"
```

### Update a book:
```bash
curl -X PUT "http://localhost:8000/books/1" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "1984",
    "author": "George Orwell",
    "genre": "Dystopian",
    "rating": 9.5
  }'
```

### Delete a book:
```bash
curl -X DELETE "http://localhost:8000/books/1"
```

## Running Tests
Run all tests:
```bash
uv run pytest
```

Run tests with verbose output:
```bash
uv run pytest -v
```

Run tests with coverage:
```bash
uv run pytest --cov=app
```

## Project Structure
book-service/
├── app/
│   ├── __init__.py
│   ├── main.py          # FastAPI application and endpoints
│   ├── models.py        # Pydantic models
│   └── repository.py    # In-memory data storage
├── tests/
│   ├── __init__.py
│   └── test_api.py      # API tests
├── Dockerfile           # Docker configuration
├── .dockerignore        # Docker ignore file
├── pyproject.toml       # Project configuration
├── uv.lock              # Dependency lock file
└── README.md            # This file

## AI Assistance
This project was developed with assistance from Claude (Anthropic). 
All generated code was reviewed, tested locally, and verified to work correctly.

# Name: Shiri Barzilay, id 214326902