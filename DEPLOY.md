# Salarium Deployment Guide

## Single-Container Deployment

This application uses a single-container deployment strategy where FastAPI serves both the API endpoints and the Vue.js frontend static files.

### Architecture

- **Frontend**: Vue 3 + Vite SPA compiled to static files
- **Backend**: FastAPI with Tortoise ORM and SQLite
- **Container**: Single Docker container with multi-stage build
- **Port**: 8080 (host) → 8000 (container)
- **Database**: SQLite persisted to `./data/` directory

### Prerequisites

- Docker and Docker Compose installed
- Ports 8080 available on the host

### Quick Start

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd salarium
   ```

2. **Create environment file** (optional)
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

3. **Build and run the container**
   ```bash
   docker compose up -d --build
   ```

4. **Access the application**
   - Frontend: http://localhost:8080
   - API Docs: http://localhost:8080/docs
   - API: http://localhost:8080/api

5. **View logs**
   ```bash
   docker compose logs -f app
   ```

6. **Stop the container**
   ```bash
   docker compose down
   ```

### Configuration

#### Environment Variables

Create a `.env` file in the project root with the following variables:

```env
# JWT Configuration
JWT_SECRET=your-secure-secret-key

# CORS Configuration (comma-separated origins)
CORS_ORIGINS=*

# Database Configuration
DATABASE_PATH=/app/data/salarium.db

# Uvicorn Configuration
UVICORN_HOST=0.0.0.0
UVICORN_PORT=8000
UVICORN_WORKERS=2
```

#### Production Recommendations

For production deployments:

1. **Change JWT_SECRET**: Use a strong, random secret key
   ```bash
   JWT_SECRET=$(openssl rand -hex 32)
   ```

2. **Configure CORS**: Limit to specific origins
   ```env
   CORS_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
   ```

3. **Increase Workers**: Adjust based on CPU cores
   ```env
   UVICORN_WORKERS=4
   ```

4. **Use HTTPS**: Deploy behind a reverse proxy (Nginx, Traefik, Caddy)

### Data Persistence

The SQLite database is persisted in the `./data/` directory on the host machine. This directory is automatically created when the container starts.

**Backup the database**:
```bash
cp ./data/salarium.db ./data/salarium.db.backup
```

**Restore from backup**:
```bash
docker compose down
cp ./data/salarium.db.backup ./data/salarium.db
docker compose up -d
```

### Health Check

The container includes a health check that monitors the FastAPI docs endpoint:
```bash
curl -f http://localhost:8080/docs
```

Check health status:
```bash
docker compose ps
```

### Troubleshooting

#### Container won't start
```bash
# Check logs
docker compose logs app

# Rebuild from scratch
docker compose down -v
docker compose build --no-cache
docker compose up -d
```

#### Permission issues with data directory
```bash
# Ensure correct permissions
mkdir -p data
chmod 755 data
```

#### Frontend routes return 404 on refresh
This should not happen with the current configuration. The `StaticFiles` middleware with `html=True` provides SPA fallback. If you encounter this:

1. Verify the static files were copied correctly:
   ```bash
   docker exec salarium ls -la /app/static
   ```

2. Check that the static mount is configured in `main.py`

### Advanced Deployment

#### Using Gunicorn with Uvicorn workers

For better process management in production, you can use Gunicorn:

1. Add to `requirements.txt`:
   ```
   gunicorn==21.2.0
   ```

2. Update Dockerfile CMD:
   ```dockerfile
   CMD ["gunicorn", "app.main:app", "-k", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:8000", "--workers", "4"]
   ```

#### Reverse Proxy Setup (Nginx)

Example Nginx configuration:

```nginx
server {
    listen 80;
    server_name yourdomain.com;

    location / {
        proxy_pass http://localhost:8080;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

#### Database Migration to PostgreSQL/MySQL

To migrate from SQLite to PostgreSQL or MySQL:

1. Update `docker-compose.yml` to add database service
2. Update `config.py` to use the new database URL
3. Update Tortoise ORM connection string
4. Export data from SQLite and import to new database

### Development vs Production

**Development** (local):
```bash
# Backend
cd backend
python -m uvicorn app.main:app --reload

# Frontend
cd frontend
npm run dev
```

**Production** (Docker):
```bash
docker compose up -d --build
```

### Support

For issues or questions, please refer to:
- [README.md](./README.md) - General project information
- [GitHub Issues](link-to-issues) - Report bugs or request features
