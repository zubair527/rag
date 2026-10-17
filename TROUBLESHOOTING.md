# Troubleshooting Guide

## Common Issues and Solutions

### 1. "docker-compose: command not found"

**Problem**: You have an older version of Docker that uses `docker-compose` instead of `docker compose`.

**Solution**:

**Option A (Recommended)**: Update Docker Desktop
```bash
# Update Docker Desktop to the latest version
# Download from: https://www.docker.com/products/docker-desktop
```

**Option B**: Check your Docker version
```bash
# Check if Docker Compose V2 is available
docker compose version

# If not, check for V1
docker-compose version
```

**Option C**: Use docker-compose directly (if you must)
```bash
# Instead of 'make init', run:
cp .env.example .env
docker-compose build
docker-compose up -d
docker exec rag-ollama ollama pull llama3.2:1b
```

---

### 2. Port Already in Use

**Problem**: Port 80, 8080, or other ports are already in use.

**Solution**: Change the port in `docker-compose.yml`

```yaml
# For Nginx (main UI)
nginx:
  ports:
    - "8080:80"  # Change 80 to 8080 or any free port

# Then access at: http://localhost:8080
```

---

### 3. Services Won't Start

**Problem**: One or more services fail to start.

**Check service status**:
```bash
docker compose ps
docker compose logs [service-name]
```

**Common causes**:
1. Insufficient memory - Allocate at least 8GB to Docker
2. Port conflicts - Change ports in docker-compose.yml
3. Disk space - Need at least 10GB free

**Solution**:
```bash
# Stop everything
docker compose down

# Check Docker resources
docker system df

# Restart
docker compose up -d
```

---

### 4. Ollama Model Not Downloaded

**Problem**: LLM queries fail with "model not found".

**Solution**:
```bash
# Pull the model manually
docker exec rag-ollama ollama pull llama3.2:1b

# Verify it's available
docker exec rag-ollama ollama list

# Restart FastAPI
docker compose restart fastapi
```

---

### 5. Database Connection Errors

**Problem**: Application can't connect to MariaDB.

**Check database health**:
```bash
docker compose ps mariadb
docker compose logs mariadb
```

**Solution**:
```bash
# Restart database
docker compose restart mariadb

# Wait 10 seconds for it to be healthy
sleep 10

# Restart application
docker compose restart fastapi
```

---

### 6. Weaviate Connection Errors

**Problem**: Vector database is not responding.

**Check Weaviate**:
```bash
curl http://localhost:8080/v1/.well-known/ready
docker compose logs weaviate
```

**Solution**:
```bash
# Restart Weaviate
docker compose restart weaviate

# Wait for it to be ready (can take 30-60 seconds)
sleep 30

# Restart application
docker compose restart fastapi
```

---

### 7. High Memory Usage

**Problem**: Docker is using too much RAM.

**Check resource usage**:
```bash
docker stats
```

**Solutions**:

1. **Use smaller model**:
   ```bash
   # In .env file
   OLLAMA_MODEL=llama3.2:1b  # Already smallest
   ```

2. **Reduce resource limits** in `docker-compose.yml`:
   ```yaml
   ollama:
     deploy:
       resources:
         limits:
           memory: 4G  # Reduce from 8G
   ```

3. **Disable services you don't need**:
   ```bash
   # Comment out Prometheus in docker-compose.yml
   # prometheus:
   #   ...
   ```

---

### 8. Slow Performance

**Problem**: Queries take too long.

**Causes & Solutions**:

1. **CPU-only inference** (no GPU):
   - Expected: 2-5 seconds per query
   - Use smallest model (llama3.2:1b)

2. **Enable caching**:
   ```bash
   # Verify Redis is running
   docker compose ps redis

   # Check cache hit rate in logs
   docker compose logs fastapi | grep cache
   ```

3. **Reduce chunk size** in `.env`:
   ```bash
   CHUNK_SIZE=500
   CHUNK_OVERLAP=100
   ```

---

### 9. API Returns Errors

**Problem**: API endpoints return 500 errors.

**Debug steps**:
```bash
# Check API logs
docker compose logs fastapi -f

# Test health endpoint
curl http://localhost/api/v1/health | python3 -m json.tool

# Check all services are healthy
./scripts/verify_setup.sh
```

---

### 10. Can't Access UI

**Problem**: http://localhost shows nothing or error.

**Check Nginx and Streamlit**:
```bash
docker compose ps nginx
docker compose ps streamlit
docker compose logs nginx
docker compose logs streamlit
```

**Solution**:
```bash
# Restart both
docker compose restart nginx streamlit

# Wait a few seconds
sleep 5

# Try again
open http://localhost
```

---

### 11. Docker Desktop Not Enough Resources

**Problem**: Docker Desktop shows insufficient resources.

**Solution**:

**macOS/Windows**:
1. Open Docker Desktop
2. Go to Settings/Preferences
3. Resources → Advanced
4. Allocate:
   - **Memory**: At least 8GB (12GB recommended)
   - **CPUs**: At least 4 cores
5. Click "Apply & Restart"

**Linux**:
- Docker uses all available resources by default
- Check with: `docker info | grep -i memory`

---

### 12. Build Fails

**Problem**: `docker compose build` fails.

**Common causes**:
1. Network issues downloading packages
2. Disk space
3. Docker daemon issues

**Solution**:
```bash
# Clean up Docker
docker system prune -a

# Retry build with no cache
docker compose build --no-cache

# If still fails, check logs
docker compose build 2>&1 | tee build.log
```

---

### 13. Volume Permission Issues

**Problem**: "Permission denied" errors accessing volumes.

**Solution**:
```bash
# Linux only - fix volume permissions
sudo chown -R $USER:$USER .

# Or run with sudo (not recommended)
sudo docker compose up -d
```

---

### 14. Clean Slate (Nuclear Option)

**Problem**: Everything is broken, need to start fresh.

**Warning**: This deletes ALL data including uploaded documents!

```bash
# Stop and remove everything
docker compose down -v

# Remove all Docker resources
docker system prune -a --volumes

# Start fresh
make init
```

---

## Getting Help

If none of the above work:

1. **Check logs**:
   ```bash
   make logs
   ```

2. **Verify setup**:
   ```bash
   ./scripts/verify_setup.sh
   ```

3. **Check system resources**:
   ```bash
   docker stats
   docker system df
   ```

4. **Review documentation**:
   - [README.md](README.md) - Full documentation
   - [ARCHITECTURE.md](ARCHITECTURE.md) - Technical details
   - [QUICKSTART.md](QUICKSTART.md) - Quick start guide

5. **Common commands**:
   ```bash
   make help           # Show all commands
   make health         # Check service health
   docker compose ps   # Show container status
   ```

---

## Prevention Tips

1. **Regular cleanup**:
   ```bash
   docker system prune
   ```

2. **Monitor resources**:
   ```bash
   docker stats
   ```

3. **Keep backups**:
   ```bash
   make backup-db
   ```

4. **Update regularly**:
   ```bash
   docker compose pull
   ```

5. **Check health**:
   ```bash
   make health
   ```
