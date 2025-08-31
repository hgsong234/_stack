# todo_api.py: A basic To-Do List API using FastAPI.

from fastapi import FastAPI, HTTPException, Path, Query
from pydantic import BaseModel, Field
from typing import List, Dict, Optional
import uuid

# FastAPI 인스턴스 생성
app = FastAPI(
    title="Simple To-Do API",
    description="A basic API for managing to-do items.",
    version="1.0.0"
)

# In-memory 데이터베이스 to store tasks
tasks_db: Dict[uuid.UUID, dict] = {}

# Pydantic model for task creation
class TaskCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=300)
    completed: bool = False

# Pydantic model for task updates
class TaskUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=300)
    completed: Optional[bool] = None

# Pydantic model for tasks stored in the DB
class TaskInDB(TaskCreate):
    id: uuid.UUID

# 1. Retrieve all tasks
@app.get(
    "/tasks/",
    response_model=List[TaskInDB],
    summary="Get all tasks",
)
async def get_all_tasks(
    skip: int = Query(0, description="Number of items to skip."),
    limit: int = Query(10, description="Maximum number of items to return.")
):
    """Retrieve a list of all to-do items."""
    tasks = list(tasks_db.values())
    return [TaskInDB(**task) for task in tasks[skip : skip + limit]]

# 2. Retrieve a specific task by ID
@app.get(
    "/tasks/{task_id}",
    response_model=TaskInDB,
    summary="Get a single task by ID",
)
async def get_task(
    task_id: uuid.UUID = Path(..., description="The ID of the task to retrieve.")
):
    """Retrieve a single to-do item by its unique ID."""
    if task_id not in tasks_db:
        raise HTTPException(
            status_code=404,
            detail=f"Task with ID {task_id} not found."
        )
    return TaskInDB(**tasks_db[task_id])

# 3. Create a new task
@app.post(
    "/tasks/",
    response_model=TaskInDB,
    status_code=201,
    summary="Create a new task",
)
async def create_task(task: TaskCreate):
    """Create a new to-do item with a unique ID."""
    task_id = uuid.uuid4()
    new_task = task.dict()
    new_task["id"] = task_id
    tasks_db[task_id] = new_task
    return TaskInDB(**new_task)

# 4. Update an existing task
@app.put(
    "/tasks/{task_id}",
    response_model=TaskInDB,
    summary="Update an existing task",
)
async def update_task(
    task_id: uuid.UUID = Path(..., description="The ID of the task to update."),
    task: TaskUpdate = ...
):
    """Update the details of an existing to-do item."""
    if task_id not in tasks_db:
        raise HTTPException(
            status_code=404,
            detail=f"Task with ID {task_id} not found."
        )
    
    current_task = tasks_db[task_id]
    update_data = task.dict(exclude_unset=True)
    
    for key, value in update_data.items():
        current_task[key] = value

    tasks_db[task_id] = current_task
    return TaskInDB(**current_task)

# 5. Delete a task
@app.delete(
    "/tasks/{task_id}",
    status_code=204,
    summary="Delete a task",
)
async def delete_task(
    task_id: uuid.UUID = Path(..., description="The ID of the task to delete.")
):
    """Delete a to-do item from the database."""
    if task_id not in tasks_db:
        raise HTTPException(
            status_code=404,
            detail=f"Task with ID {task_id} not found."
        )
    
    del tasks_db[task_id]

# 6. Search for tasks
@app.get(
    "/tasks/search/",
    response_model=List[TaskInDB],
    summary="Search for tasks",
)
async def search_tasks(
    q: Optional[str] = Query(None, description="Search term for title or description."),
    completed: Optional[bool] = Query(None, description="Filter by completion status.")
):
    """Search for tasks by title, description, or completion status."""
    filtered_tasks = []
    
    for task_data in tasks_db.values():
        match = True
        
        if q:
            if q.lower() not in task_data["title"].lower() and \
               q.lower() not in task_data["description"].lower():
                match = False
        
        if completed is not None:
            if task_data["completed"] != completed:
                match = False
        
        if match:
            filtered_tasks.append(TaskInDB(**task_data))
            
    return filtered_tasks

# To run the server, execute 'uvicorn todo_api:app --reload' in the terminal.
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("todo_api:app", host="0.0.0.0", port=8000, reload=True)