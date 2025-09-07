"""
Simple Task Management API
A basic FastAPI application for managing tasks with full DevSecOps testing coverage.
"""

from typing import List, Optional
from datetime import datetime
import uuid

from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, Field


# Pydantic models for request/response validation
class TaskCreate(BaseModel):
    """Model for creating a new task."""
    title: str = Field(..., min_length=1, max_length=100, description="Task title")
    description: Optional[str] = Field(None, max_length=500, description="Task description")
    priority: str = Field("medium", pattern="^(low|medium|high)$", description="Task priority")


class TaskUpdate(BaseModel):
    """Model for updating an existing task."""
    title: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    priority: Optional[str] = Field(None, pattern="^(low|medium|high)$")
    completed: Optional[bool] = None


class Task(BaseModel):
    """Model representing a task."""
    id: str = Field(..., description="Unique task identifier")
    title: str = Field(..., description="Task title")
    description: Optional[str] = Field(None, description="Task description")
    priority: str = Field(..., description="Task priority")
    completed: bool = Field(False, description="Task completion status")
    created_at: datetime = Field(..., description="Task creation timestamp")
    updated_at: datetime = Field(..., description="Task last update timestamp")


# FastAPI application
app = FastAPI(
    title="Task Management API",
    description="A simple API for managing tasks with DevSecOps best practices",
    version="1.0.0",
)

# In-memory storage (for simplicity)
tasks_db: dict[str, Task] = {}


@app.get("/")
async def root() -> dict[str, str]:
    """Root endpoint returning API information."""
    return {
        "message": "Task Management API",
        "version": "1.0.0",
        "status": "healthy"
    }


@app.get("/health")
async def health_check() -> dict[str, str]:
    """Health check endpoint."""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}


@app.post("/tasks", response_model=Task, status_code=status.HTTP_201_CREATED)
async def create_task(task_data: TaskCreate) -> Task:
    """Create a new task."""
    task_id = str(uuid.uuid4())
    now = datetime.now()
    
    task = Task(
        id=task_id,
        title=task_data.title,
        description=task_data.description,
        priority=task_data.priority,
        completed=False,
        created_at=now,
        updated_at=now
    )
    
    tasks_db[task_id] = task
    return task


@app.get("/tasks", response_model=List[Task])
async def get_tasks(
    completed: Optional[bool] = None,
    priority: Optional[str] = None
) -> List[Task]:
    """Get all tasks with optional filtering."""
    tasks = list(tasks_db.values())
    
    if completed is not None:
        tasks = [task for task in tasks if task.completed == completed]
    
    if priority is not None:
        tasks = [task for task in tasks if task.priority == priority]
    
    # Sort by creation date (newest first)
    tasks.sort(key=lambda x: x.created_at, reverse=True)
    return tasks


@app.get("/tasks/{task_id}", response_model=Task)
async def get_task(task_id: str) -> Task:
    """Get a specific task by ID."""
    if task_id not in tasks_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task with id {task_id} not found"
        )
    return tasks_db[task_id]


@app.put("/tasks/{task_id}", response_model=Task)
async def update_task(task_id: str, task_update: TaskUpdate) -> Task:
    """Update an existing task."""
    if task_id not in tasks_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task with id {task_id} not found"
        )
    
    task = tasks_db[task_id]
    update_data = task_update.model_dump(exclude_unset=True)
    
    for field, value in update_data.items():
        setattr(task, field, value)
    
    task.updated_at = datetime.now()
    tasks_db[task_id] = task
    return task


@app.delete("/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(task_id: str) -> None:
    """Delete a task."""
    if task_id not in tasks_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task with id {task_id} not found"
        )
    
    del tasks_db[task_id]


@app.get("/tasks/stats/summary")
async def get_task_stats() -> dict[str, int]:
    """Get task statistics."""
    total_tasks = len(tasks_db)
    completed_tasks = sum(1 for task in tasks_db.values() if task.completed)
    pending_tasks = total_tasks - completed_tasks
    
    priority_counts = {"low": 0, "medium": 0, "high": 0}
    for task in tasks_db.values():
        priority_counts[task.priority] += 1
    
    return {
        "total_tasks": total_tasks,
        "completed_tasks": completed_tasks,
        "pending_tasks": pending_tasks,
        "high_priority": priority_counts["high"],
        "medium_priority": priority_counts["medium"],
        "low_priority": priority_counts["low"]
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
