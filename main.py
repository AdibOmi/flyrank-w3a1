from typing import Optional

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse, Response
from pydantic import BaseModel

from db import init_db, get_connection

app = FastAPI(
    title="Task API",
    description="A small in-memory to-do list API built for the FlyRank Week 2 CRUD assignment.",
    version="1.0",
)

init_db()


class TaskCreate(BaseModel):
    title: str = ""


class TaskUpdate(BaseModel):
    title: Optional[str] = None
    done: Optional[bool] = None


@app.exception_handler(HTTPException)
def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(status_code=exc.status_code, content={"error": exc.detail})

def row_to_dict(row):
    return {"id": row["id"], 
            "title": row["title"],
            "done": bool(row["done"])}

tasks = [
    {"id": 1, "title": "Attend lecture", "done": False},
    {"id": 2, "title": "Journal", "done": False},
    {"id": 3, "title": "Prepare notes", "done": True},
]


@app.get("/", summary="API info")
def root():
    return {"name": "Task API", "version": "1.0", "endpoints": ["/tasks"]}


@app.get("/health", summary="Health check")
def health():
    return {"status": "ok"}


@app.get("/tasks", summary="List all tasks")
def list_tasks():
    conn = get_connection()
    rows = conn.execute("SELECT * FROM tasks").fetchall()
    conn.close()
    return [row_to_dict(row) for row in rows]



@app.get("/tasks/{task_id}", summary="Get one task by id")
def get_task(task_id: int):
    conn = get_connection()
    row = conn.execute("SELECT * FROM tasks WHERE id = ?", (task_id,)).fetchone()
    conn.close()
    if row is None:
        raise HTTPException(status_code=404, detail=f"Task {task_id} not found")
    return row_to_dict(row)


@app.post("/tasks", status_code=201, summary="Create a new task")
def create_task(body: TaskCreate):
    if not body.title.strip():
        raise HTTPException(status_code=400, detail="title is required")
    conn = get_connection()
    cursor = conn.execute(
        "INSERT INTO tasks (title, done) VALUES (?, ?)", (body.title, 0)
    )
    conn.commit()
    new_id = cursor.lastrowid
    conn.close()
    return {"id": new_id, "title": body.title, "done": False}



@app.put("/tasks/{task_id}", summary="Update a task's title and/or done status")
def update_task(task_id: int, body: TaskUpdate):
    task = next((t for t in tasks if t["id"] == task_id), None)
    if task is None:
        raise HTTPException(status_code=404, detail=f"Task {task_id} not found")
    if body.title is None and body.done is None:
        raise HTTPException(status_code=400, detail="title and/or done is required")
    if body.title is not None:
        if not body.title.strip():
            raise HTTPException(status_code=400, detail="title cannot be empty")
        task["title"] = body.title
    if body.done is not None:
        task["done"] = body.done
    return task


@app.delete("/tasks/{task_id}", status_code=204, summary="Delete a task")
def delete_task(task_id: int):
    task = next((t for t in tasks if t["id"] == task_id), None)
    if task is None:
        raise HTTPException(status_code=404, detail=f"Task {task_id} not found")
    tasks.remove(task)
    return Response(status_code=204)
