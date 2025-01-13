from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

app = FastAPI()

tasks = []
pomodoro_sessions = []

current_task_id = 1


class Task(BaseModel):
    id: int
    title: str = Field(..., min_length=3, max_length=100)
    description: Optional[str] = Field(None, max_length=100)
    status: str = Field(default = "TODO", pattern= "^(TODO|in_progress|done)$")

class PomodoroSessions(BaseModel):
    task_id: int
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    completed: bool = False


@app.post("/tasks", response_model=Task)
def create_task(task: Task):
    global current_task_id
    if any(t["title"] ==task.title for t in tasks):
        raise HTTPException(status_code=400, detail="Tytul zadania musi byc unikalny!:(")

    task.id = current_task_id
    current_task_id +=1
    tasks.append(task.dict())
    return task

@app.get("/tasks", response_model=List[Task])
def get_tasks(status: Optional[str] = None):
    if status:
        return [task for task in tasks if task["status"] == status] # craaaaaazy 
    return tasks


@app.get("/tasks/{task_id}", response_model= Task)
def get_task(task_id: int):
    task = next((task for task in tasks if task["id"] == task_id), None)
    if not task:
        raise HTTPException(status_code=404, detail="Zadanie nie istnieje :(")
    return task

@app.put("/tasks/{task_id}", response_model=Task)
def update_task(task_id: int, updated_task: Task):
    task = next((task for task in tasks if task["id"]==task_id), None)
    if not task:
        raise HTTPException(status_code=404, detail="Zadanie nie istnieje :(")
    
    if any(t["title"]==updated_task.title and t["id"] != task_id for t in tasks):
        raise HTTPException(status_code=400, detail="Tytul zadania musi byc unikalny! :(")
    task.update(updated_task.dict(exclude_unset= True))
    return task


@app.delete("/tasks/{task_id}")
def delete_task(task_id: int):
    global tasks
    tasks = [task for task in tasks if task["id"] != task_id]
    return {"detail": "Zadanie usuniete"}

