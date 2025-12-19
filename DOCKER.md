# 🐳 Docker Deployment Guide

Complete guide to run  Military Audio Translator using Docker.

## 📋 Prerequisites

- **Docker Desktop** (Windows/Mac) or **Docker Engine** (Linux)
- **Docker Compose** (included with Docker Desktop)
- **8GB+ RAM** recommended
- **10GB+ free disk space** (for models)

### Install Docker

**Windows/Mac:**
```bash
# Download and install Docker Desktop
https://www.docker.com/products/docker-desktop/
```

**Linux:**
```bash
# Ubuntu/Debian
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

---

## 🚀 Quick Start (One Command)

```bash
# Clone repository
git clone https://github.com/anubhavsingh2004/lt-audio-translator.git
cd lt-audio-translator

# Start everything with Docker Compose
docker-compose up -d
```

That's it! The application will:
1. Build backend and frontend images
2. Download AI models (first run only, ~3-4GB)
3. Start both services
4. Be accessible at **http://localhost:3000**

---

## 📦 What Gets Downloaded (First Run)

On first startup, the backend container will download:
- ✅ Whisper STT model (~300MB)
- ✅ M2M100 translation model (~1.5GB)
- ✅ Piper TTS binary (~50MB)
- ✅ 5 language voice models (~1GB)

**Total:** ~3-4GB (one-time download, persisted in Docker volumes)

---

## 🎯 Usage

### Start the Application
```bash
docker-compose up -d
```

### View Logs
```bash
# All services
docker-compose logs -f

# Backend only
docker-compose logs -f backend

# Frontend only
docker-compose logs -f frontend
```

### Stop the Application
```bash
docker-compose down
```

### Stop and Remove All Data (including models)
```bash
docker-compose down -v
```

### Restart Services
```bash
docker-compose restart
```

---

## 🔧 Configuration

### Environment Variables

Copy `.env.example` to `.env` and customize:

```bash
cp .env.example .env
```

**Available options:**

```env
# GPU Support (requires nvidia-docker)
CUDA_VISIBLE_DEVICES=0

# Ports
BACKEND_PORT=8000
FRONTEND_PORT=3000

# Whisper Model Size
WHISPER_MODEL=small  # Options: tiny, base, small, medium, large

# Logging
LOG_LEVEL=INFO
```



## 📁 Project Structure (Docker)

```
lt-audio-translator/
├── docker-compose.yml          # Orchestrates all services
├── .env.example                # Environment configuration template
├── DOCKER.md                   # This file
├── backend/
│   ├── Dockerfile              # Backend container definition
│   ├── .dockerignore           # Exclude files from image
│   └── ...                     # Application code
├── frontend/
│   ├── Dockerfile              # Frontend container definition
│   ├── nginx.conf              # Web server configuration
│   ├── .dockerignore           # Exclude files from image
│   └── ...                     # React application
```

---

## 🐛 Troubleshooting

### Models Not Downloading

**Problem:** Backend fails to download models

**Solution:**
```bash
# Access backend container
docker exec -it lt-translator-backend bash

# Manually run download script
python download_models.py

# Exit container
exit
```

### Port Already in Use

**Problem:** `Error: port 8000 is already allocated`

**Solution 1 - Change ports in docker-compose.yml:**
```yaml
services:
  backend:
    ports:
      - "8001:8000"  # Host:Container
  frontend:
    ports:
      - "3001:3000"
```

**Solution 2 - Stop conflicting service:**
```bash
# Windows
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# Linux/Mac
lsof -ti:8000 | xargs kill -9
```

### Out of Memory

**Problem:** Container crashes with OOM (Out of Memory)

**Solution:** Increase Docker memory limit
- **Docker Desktop:** Settings → Resources → Memory → 8GB+
- **Linux:** Edit `/etc/docker/daemon.json`:
```json
{
  "default-ulimits": {
    "memlock": {
      "Hard": -1,
      "Name": "memlock",
      "Soft": -1
    }
  }
}
```

### Microphone Not Working

**Problem:** Browser can't access microphone

**Solution:** Use HTTPS or localhost
- Docker Compose already uses `localhost:3000` ✅
- For remote access, set up HTTPS reverse proxy (nginx/traefik)

### Slow Performance

**Problem:** Translation takes >30 seconds

**Solutions:**
1. **Use GPU acceleration** 
2. **Use smaller Whisper model:**
   ```yaml
   environment:
     - WHISPER_MODEL=tiny  # Faster but less accurate
   ```
3. **Increase Docker resources:**
   - Docker Desktop → Settings → Resources
   - CPU: 4+ cores
   - Memory: 8GB+

---

## 🔒 Security Best Practices

### Production Deployment

1. **Use HTTPS:**
```yaml
# Add nginx reverse proxy
services:
  nginx:
    image: nginx:alpine
    ports:
      - "443:443"
    volumes:
      - ./nginx-ssl.conf:/etc/nginx/nginx.conf
      - ./certs:/etc/nginx/certs
```

2. **Restrict Access:**
```yaml
# Bind to localhost only
services:
  backend:
    ports:
      - "127.0.0.1:8000:8000"
```

3. **Update Regularly:**
```bash
docker-compose pull
docker-compose up -d
```

4. **Use Secrets for Sensitive Data:**
```yaml
services:
  backend:
    secrets:
      - api_key
secrets:
  api_key:
    file: ./secrets/api_key.txt
```

---

## 📊 Performance Benchmarks (Docker)

| Hardware | Whisper Model | Processing Time | Memory Usage |
|----------|---------------|-----------------|--------------|
| CPU (i7) | small | ~8-12s | 4GB |
| CPU (i7) | medium | ~15-20s | 6GB |
| GPU (GTX 1660) | small | ~3-5s | 6GB |
| GPU (RTX 3060) | medium | ~2-4s | 8GB |

---

## 🔄 Updates & Maintenance

### Update Application
```bash
# Pull latest code
git pull origin main

# Rebuild containers
docker-compose build

# Restart with new images
docker-compose up -d
```

### Backup Glossary Data
```bash
# Export glossary volume
docker run --rm -v lt-audio-translator_glossary-data:/data -v $(pwd):/backup alpine tar czf /backup/glossary-backup.tar.gz -C /data .

# Restore
docker run --rm -v lt-audio-translator_glossary-data:/data -v $(pwd):/backup alpine tar xzf /backup/glossary-backup.tar.gz -C /data
```

### View Resource Usage
```bash
docker stats
```

### Clean Up Unused Resources
```bash
# Remove unused images
docker image prune -a

# Remove unused volumes
docker volume prune

# Complete cleanup (CAUTION: removes all Docker data)
docker system prune -a --volumes
```



**Quick Help:**
```bash
# Check container status
docker-compose ps

# View all logs
docker-compose logs --tail=100

# Access backend shell
docker exec -it lt-translator-backend bash

# Access frontend shell
docker exec -it lt-translator-frontend sh
```
