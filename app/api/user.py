from fastapi import APIRouter, HTTPException
from app.schemas.user import UserRegister, UserLogin, UserInfo
from app.DB import DBmysql
from app.DB import logging
import hashlib

# 路由前缀 /user  文档标签：用户管理
router = APIRouter(
    prefix="/user",
    tags=["用户管理模块"]
)
db = DBmysql()


def _hash_password(password: str) -> str:
    """对密码进行 SHA256 哈希"""
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


@router.post("/register", summary="用户注册")
def register(user: UserRegister):
    try:
        select_sql = "select * from `t_user` where username = %s"
        res = db.execute_query(select_sql, (user.username,))
        if res:
            raise HTTPException(status_code=400, detail="账号已被注册")
        hashed_pwd = _hash_password(user.password)

        student_id = None
        # 学生角色：先插入 student 表，拿到 student_id
        if user.role == "学生":
            stu_sql = """INSERT INTO `student` (`name`, `gender`, `age`, `phone_number`, `birthday`)
                         VALUES (%s,%s,%s,%s,%s);"""
            student_id = db.execute_dml_return_id(stu_sql,
                (user.name or user.nickname, user.gender, user.age, user.phone_number, user.birthday))
            if not student_id:
                raise HTTPException(status_code=500, detail="学生信息录入失败")

        # 插入 t_user，关联 student_id
        insert_sql = "INSERT INTO `t_user` (`username`, `password`, `nickname`, `role`, `student_id`) VALUES (%s,%s,%s,%s,%s);"
        db.execute_dml(insert_sql, (user.username, hashed_pwd, user.nickname, user.role, student_id))
        logging.info(f"注册成功 user={user.username} role={user.role} student_id={student_id}")
        return {"code": 200, "msg": "注册成功", "student_id": student_id}
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"注册异常: {e}")
        raise HTTPException(status_code=500, detail=f"注册失败: {str(e)}")


@router.post("/login", summary="用户登录")
def login(user: UserLogin):
    try:
        hashed_pwd = _hash_password(user.password)

        # 1) 验证用户名+密码+角色
        select_sql = "select * from `t_user` where username = %s and password = %s and role = %s"
        res = db.execute_query(select_sql, (user.username, hashed_pwd, user.role))

        # 2) 哈希不匹配则尝试明文密码（兼容旧数据），匹配则自动升级为哈希
        if not res:
            plain_sql = "select * from `t_user` where username = %s and password = %s and role = %s"
            res = db.execute_query(plain_sql, (user.username, user.password, user.role))
            if res:
                # 自动迁移：将明文密码更新为哈希值
                upgrade_sql = "update `t_user` set password = %s where id = %s"
                db.execute_dml(upgrade_sql, (hashed_pwd, res[0]["id"]))
                logging.info(f"用户 {user.username} 密码已从明文升级为哈希")

        if not res:
            raise HTTPException(status_code=401, detail="账号或密码错误")
        row = res[0]
        return {
            "code": 200,
            "msg": "登录成功",
            "data": {"uid": row["id"], "username": row["username"], "nickname": row.get("nickname"), "role": row.get("role")}
        }
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"登录异常: {e}")
        raise HTTPException(status_code=500, detail=f"登录失败: {str(e)}")


@router.get("/info", summary="获取当前用户信息")
def get_user_info(uid: int):
    select_sql = "select * from `t_user` where id = %s"
    res = db.execute_query(select_sql, (uid,))
    if not res:
        raise HTTPException(status_code=404, detail="用户不存在")
    row = res[0]
    return {"id": row["id"], "username": row["username"], "nickname": row.get("nickname")}