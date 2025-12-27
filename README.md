# Book Service - Full Stack Application

A complete book management system with FastAPI backend and Streamlit frontend.

## 🌟 Features

### Backend (FastAPI)
- ✅ RESTful API for book management
- ✅ CRUD operations (Create, Read, Update, Delete)
- ✅ In-memory storage
- ✅ Input validation with Pydantic
- ✅ Interactive API documentation (Swagger UI)
- ✅ Full test coverage with pytest
- ✅ Docker support

### Frontend (Streamlit)
- ✅ Beautiful pink-themed UI
- ✅ Search books by title or author
- ✅ Sort books (by title, rating, author)
- ✅ Add new books with form validation
- ✅ Edit existing books
- ✅ Delete books
- ✅ Library statistics dashboard
- ✅ "Recommended" badge for highly-rated books (8+)
- ✅ Export books to CSV
- ✅ Real-time updates

## 📚 Book Model

Each book contains:
- `id` (integer) - Auto-generated unique identifier
- `title` (string) - Book title
- `author` (string) - Author name
- `genre` (string) - Genre (dropdown selection)
- `rating` (float) - Rating from 0-10

Available genres:
- Fantasy, Science Fiction, Mystery, Romance, Thriller, Non-Fiction, Biography, History, Other

## 🚀 Installation

### Prerequisites
- Python 3.11+
- uv (Python package manager)
- Docker (optional)

### Setup

1. Navigate to project directory:
```bash
cd ~/projects/book-service
```

2. Install dependencies:
```bash
uv sync
```

## 🎯 Running the Application

### Option 1: Run Locally

**Terminal 1 - Start the API:**
```bash
uv run uvicorn app.main:app --reload
```
API will be available at: `http://localhost:8000`

**Terminal 2 - Start the Streamlit UI:**
```bash
uv run streamlit run app/streamlit_app.py
```
UI will open automatically in your browser at: `http://localhost:8501`

### Option 2: Run with Docker (API only)
```bash
docker build -t book-service .
docker run -p 8000:8000 book-service
```

Note: Streamlit runs separately from Docker. After starting the Docker container, run Streamlit locally in a second terminal.

## 📖 API Documentation

Once the API is running, visit:
- **Swagger UI:** `http://localhost:8000/docs`
- **ReDoc:** `http://localhost:8000/redoc`

### API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Welcome message |
| GET | `/books` | Get all books |
| GET | `/books/{id}` | Get specific book |
| POST | `/books` | Create new book |
| PUT | `/books/{id}` | Update book |
| DELETE | `/books/{id}` | Delete book |

### Example API Usage

**Create a book:**
```bash
curl -X POST "http://localhost:8000/books" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "1984",
    "author": "George Orwell",
    "genre": "Science Fiction",
    "rating": 9.0
  }'
```

**Get all books:**
```bash
curl "http://localhost:8000/books"
```

## 🎨 Streamlit UI Features

### 1. Search & Sort
- Search by title or author with real-time filtering
- Sort by: Title (A-Z/Z-A), Rating (High-Low/Low-High), Author (A-Z)

### 2. Book Display
- Clean card-based layout
- Star rating visualization (⭐☆)
- "🏅 recommended" badge for books rated 8+
- Edit and Delete buttons for each book

### 3. Add New Book
- Form with validation
- Genre dropdown (no free text)
- Rating slider (0-10)
- Success animation on add

### 4. Edit Book
- Click "Edit" button on any book
- Update any field
- Save or Cancel changes

### 5. Export to CSV
- Download all books as CSV file
- Includes: id, title, author, genre, rating
- File name: `my_books.csv`

### 6. Statistics Dashboard
- 📚 Total Books
- ⭐ Average Rating
- 🎭 Most Popular Genre
- 🏆 Highest Rated Book

## 🧪 Running Tests

Run all tests:
```bash
uv run pytest
```

Run with verbose output:
```bash
uv run pytest -v
```

Run with coverage:
```bash
uv run pytest --cov=app
```

## 📁 Project Structure
```
book-service/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI backend
│   ├── models.py            # Pydantic models
│   ├── repository.py        # In-memory storage
│   └── streamlit_app.py     # Streamlit frontend
├── tests/
│   ├── __init__.py
│   └── test_api.py          # API tests
├── Dockerfile               # Docker configuration
├── .dockerignore
├── pyproject.toml           # Project configuration
├── uv.lock                  # Dependency lock file
├── requirements.txt         # Python dependencies
└── README.md                # This file

**Student:** Shiri Barzilay