# Docker Compose Runbook

Complete guide for managing the Book Service application using Docker Compose.

## Prerequisites

- Docker Engine 20.10+
- Docker Compose 2.0+
- 4GB RAM minimum
- Ports available: 8000, 5432, 6379

## Quick Start

### 1. First Time Setup
```bash
# Clone repository
git clone <your-repo-url>
cd book-service

# Start all services
docker compose up --build
```

**Expected output:**
```
✅ Successfully connected to database!
⚠️ No OPENAI_API_KEY found. LLM recommendations will use fallback mode.
INFO: Uvicorn running on http://0.0.0.0:8000
```

### 2. Access the Application

- **API Documentation**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health
- **PostgreSQL**: localhost:5432 (user: `postgres`, password: `postgres`)
- **Redis**: localhost:6379

## Common Operations

### Start Services
```bash
# Start in foreground (see logs)
docker compose up

# Start in background
docker compose up -d

# Rebuild and start
docker compose up --build
```

### Stop Services
```bash
# Stop all services
docker compose down

# Stop and remove volumes (⚠️ deletes all data!)
docker compose down -v
```

### View Logs
```bash
# All services
docker compose logs -f

# Specific service
docker compose logs -f backend
docker compose logs -f worker
docker compose logs -f db
docker compose logs -f redis

# Last 100 lines
docker compose logs --tail=100 backend
```

### Restart Services
```bash
# Restart all
docker compose restart

# Restart specific service
docker compose restart backend
```

## Service Architecture

### Services Overview
```yaml
backend:      # FastAPI application (port 8000)
worker:       # Celery worker (async tasks)
db:           # PostgreSQL 15 (port 5432)
redis:        # Redis 7 (port 6379)
```

### Service Dependencies
```
backend → db (required)
backend → redis (required)
worker → db (required)
worker → redis (required)
```

## Troubleshooting

### Backend Won't Start

**Symptom:**
```
backend exited with code 1
```

**Solution:**
```bash
# Check logs
docker compose logs backend

# Rebuild from scratch
docker compose down
docker compose build --no-cache backend
docker compose up backend
```

### Database Connection Errors

**Symptom:**
```
FATAL: password authentication failed
```

**Solution:**
```bash
# Reset database
docker compose down -v
docker compose up db
# Wait for: "database system is ready to accept connections"
docker compose up
```

### Worker Not Processing Tasks

**Symptom:**
```
No Celery workers visible in logs
```

**Solution:**
```bash
# Check worker logs
docker compose logs worker

# Restart worker
docker compose restart worker

# Verify Redis connection
docker compose exec redis redis-cli ping
# Should return: PONG
```

### Port Already in Use

**Symptom:**
```
Error: port is already allocated
```

**Solution:**
```bash
# Find process using port 8000
sudo lsof -i :8000

# Kill process
sudo kill -9 <PID>

# Or change port in docker-compose.yml
ports:
  - "8001:8000"  # Use 8001 instead
```

### Out of Memory

**Symptom:**
```
Cannot allocate memory
```

**Solution:**
```bash
# Check Docker resources
docker system df

# Clean up unused resources
docker system prune -a

# Increase Docker memory limit (Docker Desktop)
# Settings → Resources → Memory → 4GB+
```

## Database Operations

### Access PostgreSQL
```bash
# Connect to database
docker compose exec db psql -U postgres -d book_library

# Run SQL queries
\dt              # List tables
\d books         # Describe books table
SELECT * FROM books LIMIT 5;
```

### Backup Database
```bash
# Create backup
docker compose exec db pg_dump -U postgres book_library > backup.sql

# Restore backup
docker compose exec -T db psql -U postgres book_library < backup.sql
```

### Reset Database
```bash
# ⚠️ WARNING: This deletes ALL data!
docker compose down -v
docker compose up db
# Wait for initialization
docker compose up
```

## Redis Operations

### Access Redis
```bash
# Connect to Redis CLI
docker compose exec redis redis-cli

# Common commands
KEYS *                          # List all keys
GET refresh:completed:abc123    # Get value
TTL refresh:completed:abc123    # Check TTL
FLUSHALL                        # ⚠️ Delete all data
```

### Monitor Redis
```bash
# Real-time monitoring
docker compose exec redis redis-cli MONITOR

# Check stats
docker compose exec redis redis-cli INFO stats
```

## Performance Tuning

### Backend Scaling
```bash
# Run multiple backend instances
docker compose up --scale backend=3
```

**Note:** Requires load balancer configuration.

### Worker Scaling
```bash
# Run multiple workers
docker compose up --scale worker=4
```

**Increases concurrent task processing.**

### Database Optimization
```bash
# Vacuum database
docker compose exec db psql -U postgres -d book_library -c "VACUUM ANALYZE;"

# Check index usage
docker compose exec db psql -U postgres -d book_library -c "
SELECT schemaname, tablename, indexname 
FROM pg_indexes 
WHERE schemaname = 'public';"
```

## Security Notes

### Production Checklist

- [ ] Change default passwords in `.env`
- [ ] Use secrets for sensitive data
- [ ] Enable SSL/TLS for PostgreSQL
- [ ] Use Redis AUTH
- [ ] Set `SECRET_KEY` in `app/auth.py`
- [ ] Enable firewall rules
- [ ] Regular security updates

### Environment Variables

Create `.env` file:
```bash
POSTGRES_PASSWORD=your-secure-password
REDIS_PASSWORD=your-redis-password
SECRET_KEY=your-jwt-secret-key
OPENAI_API_KEY=your-openai-key
```

Update `docker-compose.yml`:
```yaml
services:
  db:
    environment:
      - POSTGRES_PASSWORD=${POSTGRES_PASSWORD}
```

## Monitoring

### Health Checks
```bash
# Check all services
curl http://localhost:8000/health

# Check database
docker compose exec db pg_isready

# Check Redis
docker compose exec redis redis-cli ping
```

### Resource Usage
```bash
# Real-time stats
docker stats

# Specific service
docker stats book_library_backend
```

## Development Workflow

### Live Code Updates
```bash
# Backend auto-reloads on code changes (uvicorn --reload)
# Edit app/*.py → Automatic restart

# Worker requires manual restart
docker compose restart worker
```

### Running Tests
```bash
# Run all tests
docker compose exec backend pytest

# Run specific test file
docker compose exec backend pytest tests/test_auth.py -v

# Run with coverage
docker compose exec backend pytest --cov=app tests/
```

### Database Migrations
```bash
# Create migration
docker compose exec backend alembic revision --autogenerate -m "Add new table"

# Apply migrations
docker compose exec backend alembic upgrade head

# Rollback
docker compose exec backend alembic downgrade -1
```

## Cleanup

### Remove Everything
```bash
# Stop services and remove volumes
docker compose down -v

# Remove images
docker compose down --rmi all

# Complete cleanup
docker system prune -a --volumes
```

## Quick Reference

| Task | Command |
|------|---------|
| Start | `docker compose up` |
| Stop | `docker compose down` |
| Rebuild | `docker compose up --build` |
| Logs | `docker compose logs -f` |
| Shell | `docker compose exec backend bash` |
| Tests | `docker compose exec backend pytest` |
| DB Access | `docker compose exec db psql -U postgres book_library` |
| Redis CLI | `docker compose exec redis redis-cli` |

## Support

For issues:
1. Check logs: `docker compose logs -f`
2. Verify services: `docker compose ps`
3. Check resources: `docker stats`
4. Review this runbook
5. Check API docs: http://localhost:8000/docs
