# FeelMate Makefile
# Common commands for Docker management

.PHONY: help build up down logs clean dev prod test

# Default target
help:
	@echo "FeelMate Docker Management Commands:"
	@echo ""
	@echo "Production Commands:"
	@echo "  make build    - Build production Docker images"
	@echo "  make up       - Start production services"
	@echo "  make down     - Stop all services"
	@echo "  make logs     - View service logs"
	@echo "  make clean    - Clean up Docker resources"
	@echo ""
	@echo "Development Commands:"
	@echo "  make dev      - Start development environment"
	@echo "  make dev-down - Stop development environment"
	@echo "  make dev-logs - View development logs"
	@echo ""
	@echo "Utility Commands:"
	@echo "  make test     - Run tests in containers"
	@echo "  make status   - Show service status"
	@echo "  make restart  - Restart all services"

# Production commands
build:
	docker-compose build

up:
	docker-compose up -d

down:
	docker-compose down

logs:
	docker-compose logs -f

clean:
	docker-compose down -v --remove-orphans
	docker system prune -f

# Development commands
dev:
	docker-compose -f docker-compose.dev.yml up --build

dev-down:
	docker-compose -f docker-compose.dev.yml down

dev-logs:
	docker-compose -f docker-compose.dev.yml logs -f

# Utility commands
test:
	docker-compose exec backend python -m pytest
	docker-compose exec frontend npm test

status:
	docker-compose ps

restart:
	docker-compose restart

# Individual service commands
build-backend:
	docker-compose build backend

build-frontend:
	docker-compose build frontend

up-backend:
	docker-compose up -d backend

up-frontend:
	docker-compose up -d frontend

logs-backend:
	docker-compose logs -f backend

logs-frontend:
	docker-compose logs -f frontend

# Health checks
health:
	@echo "Checking service health..."
	@curl -f http://localhost:8000/health && echo "Backend: OK" || echo "Backend: FAILED"
	@curl -f http://localhost:3000/ && echo "Frontend: OK" || echo "Frontend: FAILED"

# Development with specific services
dev-backend:
	docker-compose -f docker-compose.dev.yml up --build backend-dev

dev-frontend:
	docker-compose -f docker-compose.dev.yml up --build frontend-dev

# Production deployment
deploy:
	@echo "Deploying FeelMate to production..."
	docker-compose -f docker-compose.yml up -d --build
	@echo "Deployment complete! Access at http://localhost:3000"

# Backup and restore (if needed in future)
backup:
	@echo "Creating backup..."
	@mkdir -p backups
	@docker-compose exec backend tar -czf /tmp/backup.tar.gz /app/data 2>/dev/null || echo "No data to backup"
	@docker cp feelmate-backend:/tmp/backup.tar.gz ./backups/backup-$(shell date +%Y%m%d-%H%M%S).tar.gz 2>/dev/null || echo "Backup completed"

# Monitoring
monitor:
	@echo "Service Status:"
	@docker-compose ps
	@echo ""
	@echo "Resource Usage:"
	@docker stats --no-stream
	@echo ""
	@echo "Recent Logs:"
	@docker-compose logs --tail=10

# Quick start for new users
quickstart:
	@echo "🚀 Starting FeelMate for the first time..."
	@echo "Building and starting services..."
	docker-compose up --build -d
	@echo ""
	@echo "⏳ Waiting for services to be ready..."
	@sleep 10
	@echo ""
	@echo "✅ FeelMate is ready!"
	@echo "🌐 Frontend: http://localhost:3000"
	@echo "🔧 Backend API: http://localhost:8000"
	@echo "📚 API Docs: http://localhost:8000/docs"
	@echo ""
	@echo "📋 Useful commands:"
	@echo "  make logs     - View logs"
	@echo "  make down     - Stop services"
	@echo "  make dev      - Start development mode"
