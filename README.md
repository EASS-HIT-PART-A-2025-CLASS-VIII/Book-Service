# Book Library - Full Stack Application

A modern book management system with FastAPI backend and interactive Streamlit gallery frontend.


## 🌟 Features

### Backend (FastAPI)
- ✅ RESTful API for book management
- ✅ CRUD operations (Create, Read, Update, Delete)
- ✅ User ratings system (0-10 scale)
- ✅ Favorites functionality per user
- ✅ In-memory storage with 15 pre-loaded books
- ✅ Input validation with Pydantic
- ✅ Interactive API documentation (Swagger UI)
- ✅ Full test coverage with pytest
- ✅ Docker support
- ✅ Environment variables configuration

### Frontend (Streamlit)
- ✅ Beautiful pink-themed gallery UI
- ✅ Interactive book cards with cover images
- ✅ Search books by title or author (sidebar)
- ✅ Filter by genre
- ✅ View modes: All Books, My Favorites, Top Rated
- ✅ User rating system (slider 0-10)
- ✅ Add/remove favorites with heart button
- ✅ Detailed book view page
- ✅ "Most Recommended" section showing highest-rated books
- ✅ Real-time updates

## 📚 Book Model

Each book contains:
- `id` (integer) - Auto-generated unique identifier
- `title` (string) - Book title
- `author` (string) - Author name
- `genre` (string) - Book genre
- `description` (string) - Book description
- `image_url` (string) - Cover image URL
- `average_rating` (float) - Average user rating (0-10)
- `total_ratings` (integer) - Number of ratings
- `user_ratings` (dict) - Individual user ratings
- `favorites` (list) - List of users who favorited this book

## 📖 Pre-loaded Books (15)

The library comes with 15 carefully selected books:
1. **The Midnight Library** - Matt Haig (Fiction)
2. **It Ends with Us** - Colleen Hoover (Romance)
3. **The Silent Patient** - Alex Michaelides (Thriller)
4. **Educated** - Tara Westover (Biography)
5. **Harry Potter and the Philosopher's Stone** - J.K. Rowling (Fantasy)
6. **The Hobbit** - J.R.R. Tolkien (Fantasy)
7. **Pride and Prejudice** - Jane Austen (Romance)
8. **1984** - George Orwell (Dystopian)
9. **To Kill a Mockingbird** - Harper Lee (Fiction)
10. **The Kite Runner** - Khaled Hosseini (Fiction)
11. **The Book Thief** - Markus Zusak (Historical Fiction)
12. **Where the Crawdads Sing** - Delia Owens (Mystery)
13. **The Da Vinci Code** - Dan Brown (Thriller)
14. **Gone Girl** - Gillian Flynn (Thriller)
15. **The Martian** - Andy Weir (Science Fiction)

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

### Option 1: Run Locally (Recommended)

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

Note: Streamlit runs separately. After starting Docker, run Streamlit locally in a second terminal.

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
| POST | `/books` | Create new book (admin) |
| PUT | `/books/{id}` | Update book (admin) |
| DELETE | `/books/{id}` | Delete book (admin) |
| POST | `/books/{id}/rate` | Rate a book (user) |
| POST | `/books/{id}/favorite` | Toggle favorite status (user) |

## 🎨 User Interface Features

### Gallery View
- **Book Cards:** Beautiful cards with cover images, titles, authors, and average ratings
- **Quick Actions:** 🔍 (View Details) and ❤️ (Add to Favorites) buttons on each card
- **Rating System:** Slider below each card to rate books (0-10)
- **Sidebar Navigation:**
  - Search books by title or author
  - Filter by genre
  - View modes: All Books, My Favorites, Top Rated

### Book Details View
- Large cover image
- Full book information (title, author, genre, description)
- Average rating and total ratings count
- Back to Library button

### Most Recommended Section
- Displays books with the highest rating
- Shows up to 5 top-rated books
- Compact card format at the bottom of the page

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
│   ├── main.py              # FastAPI application and endpoints
│   ├── models.py            # Pydantic models
│   ├── repository.py        # In-memory data storage
│   ├── config.py            # Configuration settings
│   ├── initial_books.py     # Pre-loaded book data
│   └── streamlit_app.py     # Streamlit gallery frontend
├── tests/
│   ├── __init__.py
│   └── test_api.py          # API tests
├── .env                     # Environment variables (not in git)
├── .env.example             # Environment variables template
├── .gitignore               # Git ignore file
├── Dockerfile               # Docker configuration
├── .dockerignore            # Docker ignore file
├── pyproject.toml           # Project configuration
├── uv.lock                  # Dependency lock file
├── requirements.txt         # Python dependencies
└── README.md                # This file
```

## 🤖 AI Assistance

This project was developed with assistance from Claude (Anthropic). 


## 🔮 Technical Highlights

- **User Session Management:** Each user gets a unique UUID for personalized ratings and favorites
- **Real-time Updates:** All actions (rating, favoriting) update immediately
- **Persistent User Data:** Ratings and favorites persist during the session
- **Pre-loaded Content:** 15 books with real cover images and descriptions
- **Responsive Design:** Clean, modern UI with hover effects and smooth transitions
- **Two-View System:** Gallery view for browsing, details view for in-depth information

## 📝 Notes

- Data is stored in-memory and will be lost when servers restart
- API and Streamlit must run simultaneously for full functionality
- Default port for API: 8000
- Default port for Streamlit: 8501
- User ratings and favorites are tracked per user session
- Books are pre-loaded from `app/initial_books.py`


**Developed with ❤️ by Shiri Barzilay**