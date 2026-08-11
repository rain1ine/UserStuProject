from pydantic import BaseModel
from typing import Optional


class StuCreate(BaseModel):
    name: str
    gender: str
    age: int
    phone_number: str
    birthday: str | None = None




class StuUpdate(BaseModel):
    """修改学生：所有字段可选，只更新传入的字段"""
    name: Optional[str] = None
    gender: Optional[str] = None
    age: Optional[int] = None
    phone_number: Optional[str] = None
    birthday: Optional[str] = None

class StuUpdate2(BaseModel):
    """修改学生：所有字段可选，只更新传入的字段"""
    class_name: Optional[str] = None
    teachar_name: Optional[str] = None


class CustomSQL(BaseModel):
    sql: str
