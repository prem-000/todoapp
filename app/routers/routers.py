from fastapi import APIRouter, Body, HTTPException
from app.schemas import Todo
from typing import List
from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler

scheduler = BackgroundScheduler()
if not scheduler.running:
    scheduler.start()

router = APIRouter(prefix="/todos")
todo_list: List[dict] = []


# ------------------ Alarm Function ------------------
def send_alarm(todo_data):
    print(f"⏰ Alarm Triggered for: {todo_data['task_name']}")


# ------------------ CREATE ------------------
@router.post("/")
def create_todo(todo: Todo):
    # --- Check for overlapping times ---
    for existing_todo in todo_list:
        if (
            existing_todo["stratTime"] == todo.stratTime
            and existing_todo["OutTime"] == todo.OutTime
            and existing_todo["stratTime"] < existing_todo["OutTime"]
        ):
            raise HTTPException(status_code=400, detail="❌ Choose a different timing")

    # --- Validate alarm_time format ---
    try:
        alarm_dt = datetime.strptime(todo.alarm_time, "%Y-%m-%d %H:%M")
    except ValueError:
        raise HTTPException(
            status_code=422,
            detail="⚠️ Invalid datetime format. Use 'YYYY-MM-DD HH:MM' (e.g., 2025-10-26 23:55).",
        )

    # --- Check if alarm time is in the future ---
    if alarm_dt < datetime.now():
        raise HTTPException(status_code=400, detail="⚠️ Alarm time must be in the future")

    # --- Schedule the alarm ---
    scheduler.add_job(send_alarm, "date", run_date=alarm_dt, args=[todo.model_dump()])

    # --- Calculate duration & give feedback ---
    try:
        start = datetime.strptime(todo.stratTime, "%H:%M")
        end = datetime.strptime(todo.OutTime, "%H:%M")
        duration = (end - start).total_seconds() / 60  # in minutes

        if duration <= 0:
            raise HTTPException(status_code=400, detail="⚠️ OutTime must be later than StartTime")

        if 25 <= duration <= 60:
            feedback = "✅ Great! This is an effective learning session length."
        else:
            feedback = "💡 Try focusing for 25–60 minutes to improve concentration."

    except Exception:
        feedback = "⚠️ Invalid time format for start or end. Use HH:MM (e.g., 09:30)."

    # --- Save Todo ---
    todo_dict = todo.model_dump()
    todo_dict["feedback"] = feedback
    todo_list.append(todo_dict)

    return {"message": "✅ Todo created successfully", "data": todo_dict}


# ------------------ READ ------------------
@router.get("/")
def read_todos(task_name: str = None):
    if task_name:
        result = [todo for todo in todo_list if todo["task_name"] == task_name]
        if not result:
            raise HTTPException(status_code=404, detail="Todo not found")
        return result
    return todo_list


# ------------------ DELETE ------------------
@router.delete("/")
def delete_todo(task_name: str = Body(..., embed=True)):
    try:
        found = False
        for todo in todo_list:
            if todo["task_name"] == task_name:
                todo_list.remove(todo)
                found = True
                break

        if not found:
            raise ValueError("Todo not found")

        return {
            "message": f"Todo '{task_name}' deleted successfully",
            "data": todo_list,
        }

    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")
