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

# Test model router
test-routing:
	@echo "--- Testing Simple Query (Expected: Granite) ---"
	@docker compose exec backend uv run python -c "from app.core.model_router import get_model_for_query; print(f'MODEL: {get_model_for_query(\"What is FastAPI?\")}')"
	
	@echo "\n--- Testing Complex Query (Expected: Qwen) ---"
	@docker compose exec backend uv run python -c "from app.core.model_router import get_model_for_query; print(f'MODEL: {get_model_for_query(\"Compare the performance of FastAPI vs Flask in a RAG system\")}')"
	
	@echo "\n--- Testing Long Query (Expected: Qwen) ---"
	@docker compose exec backend uv run python -c "from app.core.model_router import get_model_for_query; print(f'MODEL: {get_model_for_query(\"This is a very long question designed specifically to exceed the 150 character threshold that we have configured in our model router to ensure that long queries go to the reasoning model.\")}')"

	@echo "\n--- Time with simple routing (Granite) ---"
	@time docker compose exec backend uv run python -c "from app.core.model_router import get_model_for_query; get_model_for_query('Hi')"