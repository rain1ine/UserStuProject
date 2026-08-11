from pydantic import BaseModel



class AddClass(BaseModel):
    name: str
    grade: str
    head_teacher_id: int
