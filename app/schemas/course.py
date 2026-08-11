from typing import Optional

from pydantic import BaseModel

class courCreate(BaseModel):
    name: str
    credit: int

class courUpdate(BaseModel):
    name: Optional[str] = None
    credit: Optional[int] = None
    teacher_id: Optional[int] = None
