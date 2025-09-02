# Docker Setup for FeelMate 🐳

This guide will help you run FeelMate using Docker, making it easy to deploy and develop the application.

## 📋 Prerequisites

- **Docker** (version 20.10+)
- **Docker Compose** (version 2.0+)
- **Git**

## 🚀 Quick Start

### 1. Clone the Repository
```bash
git clone https://github.com/Efratsc/FeelMate.git
cd FeelMate
```

### 2. Run with Docker Compose (Production)
```bash
# Build and start all services
docker-compose up --build

# Or run in background
docker-compose up -d --build
```

### 3. Access the Application
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000

## 🛠️ Development Setup

### Development Mode with Hot Reloading
```bash
# Start development environment
docker-compose -f docker-compose.dev.yml up --build

# Or run in background
docker-compose -f docker-compose.dev.yml up -d --build
```

### Development Features
- **Hot Reloading**: Code changes automatically restart services
- **Volume Mounting**: Source code is mounted for live editing
- **Debug Logging**: Enhanced logging for development
- **Fast Refresh**: Next.js fast refresh enabled

## 📁 Docker Files Structure

```
FeelMate/
├── Dockerfile.backend          # Backend production image
├── Dockerfile.frontend         # Frontend production image
├── Dockerfile.frontend.dev     # Frontend development image
├── docker-compose.yml          # Production orchestration
├── docker-compose.dev.yml      # Development orchestration
├── .dockerignore              # Files to exclude from builds
└── DOCKER.md                  # This documentation
```

## 🔧 Docker Commands

### Production Commands
```bash
# Build and start all services
docker-compose up --build

# Start services in background
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down

# Rebuild specific service
docker-compose build backend
docker-compose build frontend

# View service status
docker-compose ps
```

### Development Commands
```bash
# Start development environment
docker-compose -f docker-compose.dev.yml up --build

# View development logs
docker-compose -f docker-compose.dev.yml logs -f

# Stop development environment
docker-compose -f docker-compose.dev.yml down

# Rebuild development services
docker-compose -f docker-compose.dev.yml build
```

### Individual Service Commands
```bash
# Build backend only
docker build -f Dockerfile.backend -t feelmate-backend .

# Build frontend only
docker build -f Dockerfile.frontend -t feelmate-frontend .

# Run backend container
docker run -p 8000:8000 feelmate-backend

# Run frontend container
docker run -p 3000:3000 feelmate-frontend
```

## 🌍 Environment Variables

### Backend Environment Variables
```bash
USE_LANGRAPH=true      # Enable LangGraph mode
LOG_LEVEL=info         # Logging level (debug, info, warning, error)
PORT=8000             # Server port
```

### Frontend Environment Variables
```bash
NODE_ENV=production    # Environment (development, production)
NEXT_PUBLIC_API_URL=http://localhost:8000  # Backend API URL
```

### Custom Environment File
Create a `.env` file in the root directory:
```bash
# Backend
USE_LANGRAPH=true
LOG_LEVEL=info
PORT=8000

# Frontend
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## 🔍 Health Checks

Both services include health checks:

### Backend Health Check
- **Endpoint**: `http://localhost:8000/health`
- **Interval**: 30 seconds
- **Timeout**: 10 seconds
- **Retries**: 3

### Frontend Health Check
- **Endpoint**: `http://localhost:3000/`
- **Interval**: 30 seconds
- **Timeout**: 10 seconds
- **Retries**: 3

## 📊 Monitoring and Logs

### View Service Logs
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f backend
docker-compose logs -f frontend

# Development logs
docker-compose -f docker-compose.dev.yml logs -f
```

### Service Status
```bash
# Check service health
docker-compose ps

# Check container resources
docker stats
```

## 🔧 Troubleshooting

### Common Issues

#### 1. Port Already in Use
```bash
# Check what's using the port
lsof -i :3000
lsof -i :8000

# Stop conflicting services
sudo systemctl stop nginx  # if using nginx
```

#### 2. Build Failures
```bash
# Clean Docker cache
docker system prune -a

# Rebuild without cache
docker-compose build --no-cache
```

#### 3. Permission Issues
```bash
# Fix file permissions
sudo chown -R $USER:$USER .

# Fix Docker permissions (Linux)
sudo usermod -aG docker $USER
```

#### 4. Memory Issues
```bash
# Increase Docker memory limit
# In Docker Desktop: Settings > Resources > Memory

# Or use Docker with more memory
docker run --memory=4g feelmate-backend
```

### Debug Commands
```bash
# Enter running container
docker-compose exec backend bash
docker-compose exec frontend sh

# Check container logs
docker logs feelmate-backend
docker logs feelmate-frontend

# Inspect container
docker inspect feelmate-backend
```

## 🚀 Production Deployment

### Using Docker Compose
```bash
# Production build
docker-compose -f docker-compose.yml up -d --build

# With custom environment
docker-compose -f docker-compose.yml --env-file .env.prod up -d
```

### Using Docker Swarm
```bash
# Initialize swarm
docker swarm init

# Deploy stack
docker stack deploy -c docker-compose.yml feelmate
```

### Using Kubernetes
```bash
# Apply Kubernetes manifests
kubectl apply -f k8s/

# Check deployment
kubectl get pods
kubectl get services
```

## 🔒 Security Considerations

### Production Security
- **Non-root Users**: Both containers run as non-root users
- **Health Checks**: Regular health monitoring
- **Resource Limits**: Memory and CPU limits configured
- **Network Isolation**: Services communicate via internal network

### Security Best Practices
```bash
# Scan images for vulnerabilities
docker scan feelmate-backend
docker scan feelmate-frontend

# Use specific image tags
# Instead of 'latest', use specific versions

# Regular updates
docker-compose pull
docker-compose up -d
```

## 📈 Performance Optimization

### Image Optimization
- **Multi-stage Builds**: Frontend uses multi-stage build
- **Layer Caching**: Optimized layer ordering
- **Alpine Images**: Lightweight base images
- **Docker Ignore**: Excludes unnecessary files

### Resource Optimization
```bash
# Set resource limits
docker-compose up -d --scale backend=2 --scale frontend=2

# Monitor resource usage
docker stats
```

## 🔄 CI/CD Integration

### GitHub Actions Example
```yaml
name: Docker Build and Deploy

on:
  push:
    branches: [main]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Build and push Docker images
        run: |
          docker-compose build
          docker-compose push
```

## 📚 Additional Resources

- [Docker Documentation](https://docs.docker.com/)
- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [Next.js Docker Guide](https://nextjs.org/docs/deployment#docker-image)
- [FastAPI Docker Guide](https://fastapi.tiangolo.com/deployment/docker/)

## 🤝 Contributing with Docker

When contributing to FeelMate:

1. **Use Development Environment**:
   ```bash
   docker-compose -f docker-compose.dev.yml up --build
   ```

2. **Test Your Changes**:
   ```bash
   # Test backend
   docker-compose exec backend python -m pytest
   
   # Test frontend
   docker-compose exec frontend npm test
   ```

3. **Build Production Images**:
   ```bash
   docker-compose build
   ```

4. **Verify Everything Works**:
   ```bash
   docker-compose up --build
   ```

---

**Happy Dockerizing! 🐳✨**
