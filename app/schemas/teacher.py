from typing import Optional

from pydantic import BaseModel


class TeaCreate(BaseModel):
    name: str
    gender: str
    age: int
    subject: str
    phone: str | None = None

class TeaUpdate(BaseModel):
    """修改学生：所有字段可选，只更新传入的字段"""
    name: Optional[str] = None
    gender: Optional[str] = None
    age: Optional[int] = None
    subject: Optional[str] = None
    phone: Optional[str] = None
