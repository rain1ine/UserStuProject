from pydantic import BaseModel

# 注册
class UserRegister(BaseModel):
    username: str
    password: str
    nickname: str | None = None
    role: str         # 管理员 / 学生
    # 学生信息（role=学生时必填）
    name: str | None = None
    gender: str | None = None
    age: int | None = None
    phone_number: str | None = None
    birthday: str | None = None

# 登录
class UserLogin(BaseModel):
    username: str
    password: str
    role: str         # 前端选中角色

# 返回信息
class UserInfo(BaseModel):
    id: int
    username: str
    nickname: str | None = None
    role: str | None = None

    model_config = {"from_attributes": True}