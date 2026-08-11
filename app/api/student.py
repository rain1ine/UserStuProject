import re
from fastapi import APIRouter, HTTPException

from app.api.user import _hash_password
from app.schemas.student import StuCreate,StuUpdate,CustomSQL,StuUpdate2
from app.DB import DBmysql
from app.DB import logging

router = APIRouter(
    prefix="/student",
    tags=["学生管理"]
)
db=DBmysql()

#这里要改，要分页
@router.get("/list", summary="学生列表")
def student_list():
    try:
        logging.info("查询全部学生列表")
        select_sql = """
                     select b.`name` as tea_name,c.`name` as cls_name,a.* from student a
                            left join teachers b
                            on a.teacher_id=b.id
                            left join classes c
                            on a.class_id=c.id
                     """
        res = db.execute_query(select_sql)
        if not res:
            logging.info(f"全部学生查询结果：0条")
            return {"code": 200, "msg": "查询成功", "data": []}
        logging.info(f"全部学生查询结果：{len(res)}条")
        return {"code": 200, "msg": "查询成功", "data": res, "total": len(res)}
    except Exception as e:
        logging.error(f"查询学生信息异常，异常信息：{e}")
        raise HTTPException(status_code=500, detail=f"查询失败: {str(e)}")
        
@router.post("/add", summary="新增学生")
def student_add(user: StuCreate):
    try:
        select_sql = "select * from `student` where name = %s"
        res = db.execute_query(select_sql, (user.name,))
        if res:
            raise HTTPException(status_code=400, detail="学生已存在")
        insert_sql = "INSERT INTO `student` (`name`, `gender`, `age`, `phone_number`, `birthday`) VALUES (%s,%s,%s,%s,%s);"
        student_id = db.execute_dml_return_id(insert_sql, (user.name, user.gender, user.age, user.phone_number, user.birthday))
        logging.info(f"新增学生，插入{student_id}条")
        if not student_id:
            raise HTTPException(status_code=500, detail="学生信息录入失败")

        hashed_pwd = _hash_password('123456')
        insert_sql2 = "INSERT INTO `t_user` (`username`, `password`, `nickname`, `role`, `student_id`) VALUES (%s,%s,%s,%s,%s);"
        db.execute_dml(insert_sql2, (user.name, hashed_pwd, user.name, '学生', student_id))
        logging.info(f"注册成功 user={user.name} role='学生' student_id={student_id}")
        return {"code": 200, "msg": "注册成功", "student_id": student_id}
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"插入学生信息异常，异常信息：{e}")
        raise HTTPException(status_code=500, detail=f"新增失败: {str(e)}")

@router.put("/update/{sid}", summary="修改学生")
def student_update(sid: int, stu: StuUpdate, role: str = "管理员"):
    try:
        if role != "管理员":
            raise HTTPException(status_code=403, detail="仅管理员可修改学生")
        select_sql = "select * from `student` where id = %s"
        res = db.execute_query(select_sql, (sid,))
        if not res:
            raise HTTPException(status_code=400, detail="学生不存在")

        # 构建动态部分更新 SQL：只更新传入的非 None 字段
        existing = res[0]
        set_clauses = []
        params = []

        for field in ("name", "gender", "age", "phone_number", "birthday"):
            val = getattr(stu, field, None)
            if val is not None:
                set_clauses.append(f"`{field}` = %s")
                params.append(val)
            else:
                # 保留原值
                set_clauses.append(f"`{field}` = %s")
                params.append(existing.get(field))

        params.append(sid)
        update_sql = f"UPDATE `student` SET {', '.join(set_clauses)} WHERE `id` = %s"
        affected = db.execute_dml(update_sql, tuple(params))
        logging.info(f"修改学生 sid={sid}，影响{affected}条")
        return {"code": 200, "msg": "修改成功", "data": affected}
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"修改学生信息异常，异常信息：{e}")
        raise HTTPException(status_code=500, detail=f"修改失败: {str(e)}")

@router.delete("/del/{sid}", summary="删除学生")
def student_del(sid: int, role: str = "管理员"):
    try:
        if role != "管理员":
            raise HTTPException(status_code=403, detail="仅管理员可删除学生")
        select_sql = "select * from `student` where id = %s"
        res = db.execute_query(select_sql, (sid,))
        if not res:
            raise HTTPException(status_code=400, detail="学生不存在")
        del_sql = "delete from `student` where `id` = %s"
        res = db.execute_dml(del_sql, (sid,))
        logging.info(f"删除学生 sid={sid}，影响{res}条")

        del_sql2 = "delete from `t_user` where `student_id` = %s"
        res2 = db.execute_dml(del_sql2, (sid,))
        logging.info(f"删除学生账号 sid={sid}，影响{res2}条")
        return {"code": 200, "msg": "删除成功", "data": res}
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"删除学生信息异常，异常信息：{e}")
        raise HTTPException(status_code=500, detail=f"删除失败: {str(e)}")


def select_page_sql(page=1, page_size=10):
    """分页查询用户列表"""
    try:
        # 查总数
        count_sql = "SELECT COUNT(1) AS total FROM `student`"
        count_res = db.execute_query(count_sql)
        total = count_res[0]['total'] if count_res else 0
        # 查分页数据
        offset = (page - 1) * page_size
        page_sql = """
                     select b.`name` as tea_name,c.`name` as cls_name,a.* 
                            from student a
                            left join teachers b
                            on a.teacher_id=b.id
                            left join classes c
                            on a.class_id=c.id
                            ORDER BY a.id LIMIT %s OFFSET %s 
                    """
        rows = db.execute_query(page_sql, (page_size, offset))

        total_pages = max(1, (total + page_size - 1) // page_size)
        logging.info(f"分页查询：第{page}/{total_pages}页，{len(rows)}条，共{total}条")
        return {
            "rows": rows,
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": total_pages
        }
    except Exception as e:
        logging.error(f"分页查询异常：{e}")
        raise

@router.get("/get_page", summary="学生列表分页查询")
def list_Stu_page(page: int = 1, page_size: int = 10):
    """分页查询用户列表"""
    try:
        logging.info(f"分页查询用户，第{page}页，每页{page_size}条")
        result = select_page_sql(page, page_size)
        if result is None:
            raise HTTPException(status_code=500, detail="数据库查询失败")
        return result
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"分页查询异常：{e}")
        raise HTTPException(status_code=500, detail=f"分页查询失败: {str(e)}")
@router.get("/search", summary="多条件查询学生")
def search_stu(student_id: str = "", name: str = "", phone: str = ""):
    """按 ID / 姓名 / 手机号单独查询，支持任意组合"""
    try:
        where_parts = []
        params = []

        if student_id.strip():
            where_parts.append("a.id LIKE %s")
            params.append(f"%{student_id.strip()}%")

        if name.strip():
            if len(name.strip()) < 2:
                raise HTTPException(status_code=400, detail="姓名至少输入 2 个字符")
            where_parts.append("a.name LIKE %s")
            params.append(f"%{name.strip()}%")

        if phone.strip():
            digits = re.sub(r'\D', '', phone.strip())
            if len(digits) < 11:
                raise HTTPException(status_code=400, detail="手机号至少输入 11 位数字")
            where_parts.append("a.phone_number LIKE %s")
            params.append(f"%{phone.strip()}%")

        if not where_parts:
            raise HTTPException(status_code=400, detail="请至少输入一个查询条件")

        where_clause = " AND ".join(where_parts)
        select_sql = f"""select b.`name` as tea_name,c.`name` as cls_name,a.*
                            from student a
                            left join teachers b
                            on a.teacher_id=b.id
                            left join classes c
                            on a.class_id=c.id WHERE {where_clause} ORDER BY a.id"""
        res = db.execute_query(select_sql, tuple(params))
        logging.info(f"多条件查询到{len(res)}条")
        return {"code": 200, "msg": "查询成功", "data": res, "total": len(res)}
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"搜索异常：{e}")
        raise HTTPException(status_code=500, detail=f"搜索失败: {str(e)}")


@router.put("/assign_class/{sid}", summary="学生分班")
def student_assign_class(sid: int, class_id: int = None):
    """将学生分配到指定班级"""
    try:
        if class_id is None:
            raise HTTPException(status_code=400, detail="请提供班级ID")
        upd_sql = "UPDATE `student` SET class_id = %s WHERE id = %s"
        db.execute_dml(upd_sql, (class_id, sid))
        logging.info(f"学生 sid={sid} 分配到班级 class_id={class_id}")
        return {"code": 200, "msg": "分班成功"}
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"分班异常：{e}")
        raise HTTPException(status_code=500, detail=f"分班失败: {str(e)}")

@router.put("/assign_teachers/{sid}", summary="选老师")
def student_assign_teachers(sid: int, teacher_id: int = None):
    """将学生分配到指定班级"""
    try:
        if teacher_id is None:
            raise HTTPException(status_code=400, detail="请提供老师ID")
        upd_sql = "UPDATE `student` SET teacher_id = %s WHERE id = %s"
        db.execute_dml(upd_sql, (teacher_id, sid))
        logging.info(f"学生 sid={sid} 选老师 class_id={teacher_id}")
        return {"code": 200, "msg": "选老师成功"}
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"分班异常：{e}")
        raise HTTPException(status_code=500, detail=f"选老师失败: {str(e)}")



def custom_execute_sql(sql):
    """自定义 SQL 执行：仅允许 SELECT/SHOW/DESC 查询，禁止 DML/DDL"""
    try:
        sql_upper = sql.strip().upper()
        allowed_prefixes = ('SELECT', 'SHOW', 'DESC', 'DESCRIBE', 'EXPLAIN')
        if not any(sql_upper.startswith(p) for p in allowed_prefixes):
            raise HTTPException(
                status_code=403,
                detail="仅允许执行 SELECT / SHOW / DESC 等查询语句，禁止 INSERT/UPDATE/DELETE/DROP 等修改操作"
            )
        res = db.execute_query(sql)
        logging.info(f"自定义查询返回{len(res)}条")
        return {"type": "query", "rows": res, "count": len(res)}
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"自定义SQL执行异常: {e}")
        raise e

@router.post("/custom_query", summary="自定义查询学生")
def custom_query(query: CustomSQL):
    """自定义 SQL 执行：用户粘贴 SQL 语句直接执行"""
    try:
        if not query.sql or not query.sql.strip():
            raise HTTPException(status_code=400, detail="SQL 语句不能为空")
        logging.info(f"执行自定义SQL: {query.sql[:100]}...")
        return custom_execute_sql(query.sql.strip())
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"自定义SQL执行异常：{e}")
        raise HTTPException(status_code=500, detail=f"SQL 执行失败：{str(e)}")


