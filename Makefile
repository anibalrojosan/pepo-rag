# Variables
BACKEND_URL=http://localhost:8002
FRONTEND_URL=http://localhost:8501

.PHONY: up down status health logs

# Start the entire system
up:
	docker compose up -d

# Stop the entire system
down:
	docker compose down

# Check the status of the containers
status:
	docker compose ps

# Check the logs in real time
logs:
	docker compose logs -f

# Check the health of the system
health:
	@echo "--- Checking Backend ---"
	@curl -f $(BACKEND_URL)/health || echo "❌ Backend is DOWN"
	@echo "\n--- Checking Frontend ---"
	@curl -f $(FRONTEND_URL)/_stcore/health || echo "❌ Frontend is DOWN"