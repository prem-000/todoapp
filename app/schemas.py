from pydantic import BaseModel

class Todo(BaseModel):
    task_name: str
    stratTime: str  # "HH:MM" format
    OutTime: str    # "HH:MM" format
    alarm_time: str # "YYYY-MM-DD HH:MM"
    timer: int
