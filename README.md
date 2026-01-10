# Book Library - Full Stack Microservices Application

A modern, scalable book management system with FastAPI backend, Streamlit frontend, PostgreSQL database, Redis cache, and Celery background workers - all orchestrated with Docker Compose.

---

## 🌟 Features

### Backend (FastAPI)
- ✅ RESTful API for book management
- ✅ CRUD operations (Create, Read, Update, Delete)
- ✅ User ratings system (0-10 scale)
- ✅ Favorites functionality per user
- ✅ Shopping cart for book orders
- ✅ PostgreSQL database with SQLAlchemy ORM
- ✅ Redis caching for performance
- ✅ Background task processing with Celery
- ✅ Weekly recommendations system (auto-updated)
- ✅ Input validation with Pydantic
- ✅ Interactive API documentation (Swagger UI)
- ✅ CORS middleware
- ✅ Static file serving for book images
- ✅ Docker support

### Frontend (Streamlit)
- ✅ Beautiful modern gallery UI
- ✅ Interactive book cards with cover images (37 books!)
- ✅ Search books by title or author
- ✅ Filter by genre (Fiction, Fantasy, Romance, Thriller, etc.)
- ✅ View modes: All Books, My Favorites, Top Rated, Weekly Top
- ✅ User rating system (slider 0-10)
- ✅ Add/remove favorites with heart button (❤️)
- ✅ Shopping cart functionality (🛒)
- ✅ Detailed book view page
- ✅ About Us page
- ✅ **NEW:** Weekly Top Recommendations (cached in Redis)
- ✅ Real-time updates

### Microservices Architecture
- ✅ **PostgreSQL Database** - Persistent data storage
- ✅ **Redis Cache** - Fast data retrieval and task queue
- ✅ **Backend API** - FastAPI application
- ✅ **Celery Worker** - Background task processing
- ✅ **Docker Compose** - Orchestrates all services

---

## 📚 Book Model

Each book contains:
- `id` (integer) - Auto-generated unique identifier
- `title` (string) - Book title
- `author` (string) - Author name
- `genre` (string) - Book genre
- `description` (string) - Book description
- `image_url` (string) - Path to cover image
- `average_rating` (float) - Average user rating (0-10)
- `total_ratings` (integer) - Number of ratings
- `user_ratings` (dict) - Individual user ratings (JSON)
- `favorites` (list) - List of user IDs who favorited (JSON)
- `borrowed_by` (list) - List of user IDs in cart (JSON)

---

## 📖 Book Collection (37 Books!)

The library comes with 37 carefully selected books across multiple genres:
- **Fantasy:** Harry Potter series, The Hobbit, A Court of Thorns and Roses
- **Fiction:** The Midnight Library, 1984, To Kill a Mockingbird
- **Romance:** It Ends with Us, Pride and Prejudice
- **Thriller:** The Silent Patient, Gone Girl, The Da Vinci Code
- **Children's Books:** The Giving Tree, Charlotte's Web, Where the Wild Things Are
- **And many more!**

All books include cover images stored in `app/images/`.

---

## 🏗️ Architecture
```
┌─────────────────────────────────────────────────────────┐
│                    User (Browser)                        │
└────────────────────┬────────────────────────────────────┘
                     │
                     ↓
┌─────────────────────────────────────────────────────────┐
│              Streamlit Frontend                          │
│              http://localhost:8501                       │
└────────────────────┬────────────────────────────────────┘
                     │ HTTP Requests
                     ↓
┌─────────────────────────────────────────────────────────┐
│              FastAPI Backend                             │
│              http://localhost:8000                       │
└─────┬────────────┬───────────────┬──────────────────────┘
      │            │               │
      ↓            ↓               ↓
┌──────────┐ ┌─────────┐   ┌──────────────┐
│PostgreSQL│ │  Redis  │   │Celery Worker │
│   :5432  │ │  :6379  │   │  (Background)│
└──────────┘ └─────────┘   └──────────────┘
```

### Services:
1. **PostgreSQL** - Stores books, ratings, favorites, cart data
2. **Redis** - Caches weekly recommendations, task queue for Celery
3. **Backend** - API endpoints, business logic
4. **Worker** - Updates recommendations daily, sends notifications
5. **Frontend** - User interface (runs locally, not in Docker)

---

## 🚀 Installation

### Prerequisites
- Python 3.12+
- uv (Python package manager)
- Docker & Docker Compose

### Setup

1. Clone and navigate to project:
```bash
cd ~/projects/book-service
```

2. Install dependencies:
```bash
uv sync
```

3. Environment variables (optional):
```bash
cp .env.example .env
# Edit .env if needed (defaults work fine for local dev)
```

---

## 🎯 Running the Application

### **Quick Start (Recommended)**

**Terminal 1 - Start all backend services:**
```bash
docker compose up
```

This starts:
- ✅ PostgreSQL (port 5432)
- ✅ Redis (port 6379)
- ✅ FastAPI Backend (port 8000)
- ✅ Celery Worker (background)

**Terminal 2 - Start Streamlit UI:**
```bash
uv run streamlit run app/streamlit_app.py
```

**Open browser:** `http://localhost:8501`

### Stopping the Application
```bash
# Terminal 1: Press Ctrl+C
docker compose down

# Terminal 2: Press Ctrl+C
```

---

## 📖 API Documentation

Once the API is running, visit:
- **Swagger UI:** `http://localhost:8000/docs`
- **ReDoc:** `http://localhost:8000/redoc`

### Main API Endpoints

#### Books
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Welcome message |
| GET | `/books` | Get all books |
| GET | `/books/{id}` | Get specific book |
| POST | `/books` | Create new book |
| PUT | `/books/{id}` | Update book |
| DELETE | `/books/{id}` | Delete book |

#### User Actions
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/books/{id}/rate` | Rate a book (0-10) |
| POST | `/books/{id}/favorite` | Toggle favorite status |
| POST | `/books/{id}/borrow` | Add/remove from cart |
| GET | `/books/cart/{user_id}` | Get user's cart |

#### Recommendations (NEW!)
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/recommendations/weekly` | Get top 5 books (cached) |
| POST | `/recommendations/refresh` | Manually trigger refresh |
| GET | `/tasks/{task_id}` | Check background task status |

#### Background Tasks (NEW!)
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/notifications/test` | Send test notification |

---

## 🎨 User Interface Features

### Main Gallery
- **5 books per row** in a beautiful grid layout
- **Book cards** with cover images, titles, authors, ratings
- **Quick actions:**
  - 🔍 View Details
  - ❤️ Add to Favorites
  - 🛒 Add to Cart
  - ⭐ Rate (0-10 slider)

### Navigation Menu
- 📚 **Books** - Browse all books with genre filter
- 👶 **Children's Books** - Filter for kids
- 🏆 **Recommended** - Top rated books
- ❤️ **Favorites** - Your favorited books
- 🌟 **Weekly Top** - Auto-updated top 5 (from cache!)
- ℹ️ **About Us** - Information page

### Book Details View
- Full-size cover image
- Complete book information
- Rating statistics
- Back to library button

### Shopping Cart
- View all selected books
- Remove books from cart
- Complete order button

### Weekly Top Recommendations ⭐ NEW!
- Shows top 5 highest-rated books
- **Cached in Redis** for speed
- Auto-updates every 24 hours via background worker
- Manual refresh button available
- Shows data source (cache vs database)

---

## 🔧 Development

### Project Structure
```
book-service/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI application & API endpoints
│   ├── models.py            # Pydantic models (API validation)
│   ├── db_models.py         # SQLAlchemy models (database schema)
│   ├── database.py          # PostgreSQL connection & session
│   ├── repository.py        # Data access layer (CRUD operations)
│   ├── worker.py            # Celery tasks (background jobs)
│   ├── config.py            # Configuration settings
│   ├── initial_books.py     # 37 pre-loaded books
│   ├── streamlit_app.py     # Streamlit frontend UI
│   ├── auth.py              # JWT authentication (for future use)
│   ├── user_models.py       # User database models (for future use)
│   └── images/              # Book cover images (37 images)
├── tests/
│   ├── __init__.py
│   └── test_api.py          # API tests
├── docker-compose.yml       # Docker services orchestration
├── Dockerfile.backend       # Backend container definition
├── Dockerfile.frontend      # Frontend container (unused - runs locally)
├── .dockerignore            # Files to exclude from Docker
├── .env                     # Environment variables (not in git)
├── .env.example             # Environment template
├── pyproject.toml           # Project dependencies & config
├── uv.lock                  # Locked dependency versions
├── requirements.txt         # Alternative dependency list
└── README.md                # This file
```

### Docker Compose Services

**`docker-compose.yml` defines 4 services:**
```yaml
services:
  db:          # PostgreSQL database
  redis:       # Redis cache & queue
  backend:     # FastAPI API server
  worker:      # Celery background worker
```

### Key Technologies
- **FastAPI** - Modern Python web framework
- **Streamlit** - Interactive web UI
- **PostgreSQL** - Relational database
- **SQLAlchemy** - Python ORM
- **Redis** - In-memory data store
- **Celery** - Distributed task queue
- **Docker** - Containerization
- **Pydantic** - Data validation
- **uvicorn** - ASGI server

---

## 🧪 Running Tests
```bash
# Run all tests
uv run pytest

# Verbose output
uv run pytest -v

# With coverage
uv run pytest --cov=app

# Specific test file
uv run pytest tests/test_api.py
```

---

## 🤖 AI Assistance

This project was developed with extensive assistance from **Claude (Anthropic AI)**.

### AI Usage:
- ✅ Architecture design and microservices setup
- ✅ Docker Compose configuration
- ✅ FastAPI endpoint implementation
- ✅ SQLAlchemy models and database schema
- ✅ Celery worker setup and task definitions
- ✅ Redis caching strategy
- ✅ Streamlit UI design and implementation
- ✅ Debugging and troubleshooting
- ✅ Code organization and best practices
- ✅ Documentation writing

All AI-generated code was reviewed, tested, and verified locally before integration.

---

## 🔮 Technical Highlights

### Performance Optimizations
- **Redis Caching:** Weekly recommendations cached for 24 hours (5ms vs 2000ms)
- **Background Workers:** Heavy computations don't block user requests
- **Database Indexing:** Fast queries on titles, authors, genres
- **Persistent Storage:** All data survives restarts

### User Experience
- **Persistent Sessions:** User ID stored in URL query params
- **Real-time Updates:** All actions update immediately
- **Responsive Design:** Clean, modern UI with hover effects
- **Image Optimization:** Local images for fast loading

### Scalability
- **Microservices:** Each service can scale independently
- **Docker Compose:** Easy deployment and orchestration
- **Background Tasks:** Async processing with Celery
- **Cache Layer:** Redis reduces database load

---

## 📊 Data Flow Examples

### 1. User Rates a Book
```
User (Frontend) → POST /books/1/rate?rating=9.5
    ↓
Backend validates & updates database
    ↓
PostgreSQL stores new rating
    ↓
Average rating recalculated
    ↓
Response sent back to Frontend
    ↓
UI updates instantly
```

### 2. Weekly Recommendations (Cached)
```
Celery Worker (every 24 hours)
    ↓
Query: SELECT TOP 5 books ORDER BY rating
    ↓
Store in Redis (key: "weekly_recommendations")
    ↓
User visits "Weekly Top" page
    ↓
Backend reads from Redis (5ms - super fast!)
    ↓
Display to user
```

### 3. Background Notification
```
User action triggers notification
    ↓
Backend: send_notification.delay()  # Non-blocking!
    ↓
Task added to Redis queue
    ↓
Celery Worker picks up task
    ↓
Notification sent in background
    ↓
User continues using app (no waiting!)
```

---

## 🚧 Future Enhancements (Roadmap)

### Planned Features:
- [ ] JWT Authentication & user accounts
- [ ] Async refresh script with bounded concurrency
- [ ] LLM-powered book recommendations (Pydantic AI)
- [ ] Email notifications for new recommendations
- [ ] CSV/PDF export functionality
- [ ] Advanced search with filters
- [ ] Unit & integration tests
- [ ] CI/CD pipeline
- [ ] Production deployment guide

---

## 📝 Environment Variables
```bash
# Database
DATABASE_URL=postgresql://bookuser:bookpass@localhost:5432/bookdb

# Redis
REDIS_URL=redis://localhost:6379/0

# API
API_URL=http://localhost:8000
```

*(Defaults work for local development via Docker Compose)*

---

## 🐛 Troubleshooting

### Backend won't start
```bash
# Check if containers are running
docker compose ps

# View logs
docker compose logs backend
docker compose logs db
docker compose logs redis
docker compose logs worker

# Restart everything
docker compose down
docker compose up --build
```

### Database connection issues
```bash
# Check PostgreSQL is healthy
docker compose logs db

# Reset database
docker compose down -v  # ⚠️ Deletes all data!
docker compose up
```

### Redis connection issues
```bash
# Check Redis is running
docker compose logs redis

# Test Redis connection
docker exec -it book_library_redis redis-cli ping
# Should return: PONG
```

### Images not loading
- Ensure `app/images/` folder exists with 37 images
- Check that Backend is serving `/images` static files
- Verify image URLs in browser console (F12)

---

## 📄 License

This project is for educational purposes as part of a university assignment.

---

## 👤 Author

**Shiri Barzilay**

Developed with ❤️ and lots of ☕

---

## 🙏 Acknowledgments

- **Claude AI (Anthropic)** - For extensive development assistance
- **FastAPI** - For the amazing Python web framework
- **Streamlit** - For the beautiful UI framework
- **Docker** - For containerization magic

---

**Happy Reading! 📚✨**