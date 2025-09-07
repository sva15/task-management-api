"""
Comprehensive test suite for Task Management API
Tests all endpoints, error cases, and business logic with high coverage.
"""

import pytest
from fastapi.testclient import TestClient
from datetime import datetime
from unittest.mock import patch
import sys
import os

# Add the parent directory to Python path to import src module
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.main import app, tasks_db


@pytest.fixture
def client():
    """Create a test client for the FastAPI app."""
    return TestClient(app)


@pytest.fixture(autouse=True)
def clear_tasks_db():
    """Clear the tasks database before each test."""
    tasks_db.clear()
    yield
    tasks_db.clear()


class TestRootEndpoints:
    """Test root and health endpoints."""
    
    def test_root_endpoint(self, client):
        """Test the root endpoint returns correct information."""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Task Management API"
        assert data["version"] == "1.0.0"
        assert data["status"] == "healthy"
    
    def test_health_check(self, client):
        """Test the health check endpoint."""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "timestamp" in data
        # Verify timestamp is valid ISO format
        datetime.fromisoformat(data["timestamp"])


class TestTaskCreation:
    """Test task creation functionality."""
    
    def test_create_task_success(self, client):
        """Test successful task creation."""
        task_data = {
            "title": "Test Task",
            "description": "Test Description",
            "priority": "high"
        }
        response = client.post("/tasks", json=task_data)
        assert response.status_code == 201
        
        data = response.json()
        assert data["title"] == task_data["title"]
        assert data["description"] == task_data["description"]
        assert data["priority"] == task_data["priority"]
        assert data["completed"] is False
        assert "id" in data
        assert "created_at" in data
        assert "updated_at" in data
    
    def test_create_task_minimal(self, client):
        """Test creating task with minimal required fields."""
        task_data = {"title": "Minimal Task"}
        response = client.post("/tasks", json=task_data)
        assert response.status_code == 201
        
        data = response.json()
        assert data["title"] == "Minimal Task"
        assert data["description"] is None
        assert data["priority"] == "medium"  # Default priority
        assert data["completed"] is False
    
    def test_create_task_invalid_priority(self, client):
        """Test creating task with invalid priority."""
        task_data = {
            "title": "Test Task",
            "priority": "invalid"
        }
        response = client.post("/tasks", json=task_data)
        assert response.status_code == 422
    
    def test_create_task_empty_title(self, client):
        """Test creating task with empty title."""
        task_data = {"title": ""}
        response = client.post("/tasks", json=task_data)
        assert response.status_code == 422
    
    def test_create_task_long_title(self, client):
        """Test creating task with title too long."""
        task_data = {"title": "x" * 101}  # Exceeds 100 char limit
        response = client.post("/tasks", json=task_data)
        assert response.status_code == 422
    
    def test_create_task_long_description(self, client):
        """Test creating task with description too long."""
        task_data = {
            "title": "Test Task",
            "description": "x" * 501  # Exceeds 500 char limit
        }
        response = client.post("/tasks", json=task_data)
        assert response.status_code == 422


class TestTaskRetrieval:
    """Test task retrieval functionality."""
    
    def test_get_empty_tasks(self, client):
        """Test getting tasks when none exist."""
        response = client.get("/tasks")
        assert response.status_code == 200
        assert response.json() == []
    
    def test_get_all_tasks(self, client):
        """Test getting all tasks."""
        # Create test tasks
        task1 = {"title": "Task 1", "priority": "high"}
        task2 = {"title": "Task 2", "priority": "low"}
        
        client.post("/tasks", json=task1)
        client.post("/tasks", json=task2)
        
        response = client.get("/tasks")
        assert response.status_code == 200
        tasks = response.json()
        assert len(tasks) == 2
        # Should be sorted by creation date (newest first)
        assert tasks[0]["title"] == "Task 2"
        assert tasks[1]["title"] == "Task 1"
    
    def test_get_tasks_filter_by_completed(self, client):
        """Test filtering tasks by completion status."""
        # Create and complete one task
        task1_response = client.post("/tasks", json={"title": "Task 1"})
        task1_id = task1_response.json()["id"]
        client.put(f"/tasks/{task1_id}", json={"completed": True})
        
        # Create another task (not completed)
        client.post("/tasks", json={"title": "Task 2"})
        
        # Filter by completed tasks
        response = client.get("/tasks?completed=true")
        assert response.status_code == 200
        tasks = response.json()
        assert len(tasks) == 1
        assert tasks[0]["title"] == "Task 1"
        assert tasks[0]["completed"] is True
        
        # Filter by pending tasks
        response = client.get("/tasks?completed=false")
        assert response.status_code == 200
        tasks = response.json()
        assert len(tasks) == 1
        assert tasks[0]["title"] == "Task 2"
        assert tasks[0]["completed"] is False
    
    def test_get_tasks_filter_by_priority(self, client):
        """Test filtering tasks by priority."""
        client.post("/tasks", json={"title": "High Task", "priority": "high"})
        client.post("/tasks", json={"title": "Low Task", "priority": "low"})
        client.post("/tasks", json={"title": "Medium Task", "priority": "medium"})
        
        response = client.get("/tasks?priority=high")
        assert response.status_code == 200
        tasks = response.json()
        assert len(tasks) == 1
        assert tasks[0]["title"] == "High Task"
    
    def test_get_task_by_id(self, client):
        """Test getting a specific task by ID."""
        task_response = client.post("/tasks", json={"title": "Test Task"})
        task_id = task_response.json()["id"]
        
        response = client.get(f"/tasks/{task_id}")
        assert response.status_code == 200
        task = response.json()
        assert task["id"] == task_id
        assert task["title"] == "Test Task"
    
    def test_get_nonexistent_task(self, client):
        """Test getting a task that doesn't exist."""
        response = client.get("/tasks/nonexistent-id")
        assert response.status_code == 404
        assert "not found" in response.json()["detail"]


class TestTaskUpdate:
    """Test task update functionality."""
    
    def test_update_task_success(self, client):
        """Test successful task update."""
        # Create a task
        task_response = client.post("/tasks", json={"title": "Original Title"})
        task_id = task_response.json()["id"]
        original_updated_at = task_response.json()["updated_at"]
        
        # Update the task
        update_data = {
            "title": "Updated Title",
            "description": "Updated Description",
            "priority": "high",
            "completed": True
        }
        
        with patch('src.main.datetime') as mock_datetime:
            mock_datetime.now.return_value = datetime(2024, 1, 15, 12, 0, 0)
            mock_datetime.side_effect = lambda *args, **kw: datetime(*args, **kw)
            
            response = client.put(f"/tasks/{task_id}", json=update_data)
        
        assert response.status_code == 200
        updated_task = response.json()
        assert updated_task["title"] == "Updated Title"
        assert updated_task["description"] == "Updated Description"
        assert updated_task["priority"] == "high"
        assert updated_task["completed"] is True
        assert updated_task["updated_at"] != original_updated_at
    
    def test_update_task_partial(self, client):
        """Test partial task update."""
        # Create a task
        task_response = client.post("/tasks", json={
            "title": "Original Title",
            "description": "Original Description",
            "priority": "low"
        })
        task_id = task_response.json()["id"]
        
        # Update only the title
        response = client.put(f"/tasks/{task_id}", json={"title": "New Title"})
        assert response.status_code == 200
        
        updated_task = response.json()
        assert updated_task["title"] == "New Title"
        assert updated_task["description"] == "Original Description"  # Unchanged
        assert updated_task["priority"] == "low"  # Unchanged
    
    def test_update_nonexistent_task(self, client):
        """Test updating a task that doesn't exist."""
        response = client.put("/tasks/nonexistent-id", json={"title": "New Title"})
        assert response.status_code == 404
        assert "not found" in response.json()["detail"]
    
    def test_update_task_invalid_data(self, client):
        """Test updating task with invalid data."""
        # Create a task
        task_response = client.post("/tasks", json={"title": "Test Task"})
        task_id = task_response.json()["id"]
        
        # Try to update with invalid priority
        response = client.put(f"/tasks/{task_id}", json={"priority": "invalid"})
        assert response.status_code == 422


class TestTaskDeletion:
    """Test task deletion functionality."""
    
    def test_delete_task_success(self, client):
        """Test successful task deletion."""
        # Create a task
        task_response = client.post("/tasks", json={"title": "To Delete"})
        task_id = task_response.json()["id"]
        
        # Delete the task
        response = client.delete(f"/tasks/{task_id}")
        assert response.status_code == 204
        
        # Verify task is deleted
        response = client.get(f"/tasks/{task_id}")
        assert response.status_code == 404
    
    def test_delete_nonexistent_task(self, client):
        """Test deleting a task that doesn't exist."""
        response = client.delete("/tasks/nonexistent-id")
        assert response.status_code == 404
        assert "not found" in response.json()["detail"]


class TestTaskStats:
    """Test task statistics functionality."""
    
    def test_stats_empty(self, client):
        """Test stats when no tasks exist."""
        response = client.get("/tasks/stats/summary")
        assert response.status_code == 200
        stats = response.json()
        assert stats == {
            "total_tasks": 0,
            "completed_tasks": 0,
            "pending_tasks": 0,
            "high_priority": 0,
            "medium_priority": 0,
            "low_priority": 0
        }
    
    def test_stats_with_tasks(self, client):
        """Test stats with various tasks."""
        # Create tasks with different priorities and completion status
        tasks = [
            {"title": "High Task 1", "priority": "high"},
            {"title": "High Task 2", "priority": "high"},
            {"title": "Medium Task", "priority": "medium"},
            {"title": "Low Task", "priority": "low"}
        ]
        
        task_ids = []
        for task in tasks:
            response = client.post("/tasks", json=task)
            task_ids.append(response.json()["id"])
        
        # Complete some tasks
        client.put(f"/tasks/{task_ids[0]}", json={"completed": True})
        client.put(f"/tasks/{task_ids[2]}", json={"completed": True})
        
        response = client.get("/tasks/stats/summary")
        assert response.status_code == 200
        stats = response.json()
        
        assert stats["total_tasks"] == 4
        assert stats["completed_tasks"] == 2
        assert stats["pending_tasks"] == 2
        assert stats["high_priority"] == 2
        assert stats["medium_priority"] == 1
        assert stats["low_priority"] == 1


class TestEdgeCases:
    """Test edge cases and error conditions."""
    
    def test_invalid_json(self, client):
        """Test sending invalid JSON."""
        response = client.post(
            "/tasks",
            data="invalid json",
            headers={"Content-Type": "application/json"}
        )
        assert response.status_code == 422
    
    def test_missing_required_field(self, client):
        """Test creating task without required title field."""
        response = client.post("/tasks", json={"description": "No title"})
        assert response.status_code == 422
    
    def test_unicode_handling(self, client):
        """Test handling of unicode characters."""
        task_data = {
            "title": "Unicode Task 🚀",
            "description": "Description with émojis and spëcial chars"
        }
        response = client.post("/tasks", json=task_data)
        assert response.status_code == 201
        
        data = response.json()
        assert data["title"] == "Unicode Task 🚀"
        assert data["description"] == "Description with émojis and spëcial chars"


class TestConcurrency:
    """Test concurrent operations (basic simulation)."""
    
    def test_multiple_task_creation(self, client):
        """Test creating multiple tasks rapidly."""
        tasks = [{"title": f"Task {i}"} for i in range(10)]
        
        responses = []
        for task in tasks:
            response = client.post("/tasks", json=task)
            responses.append(response)
        
        # All should succeed
        for response in responses:
            assert response.status_code == 201
        
        # Verify all tasks exist
        response = client.get("/tasks")
        assert len(response.json()) == 10
        
        # Verify all have unique IDs
        task_ids = [task["id"] for task in response.json()]
        assert len(set(task_ids)) == 10  # All unique
