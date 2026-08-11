import re
from fastapi import APIRouter, HTTPException

from app.api.user import _hash_password
from app.schemas.course import courCreate,courUpdate
from app.DB import DBmysql
from app.DB import logging

router = APIRouter(
    prefix="/course",
    tags=["课程管理"]
)
db=DBmysql()

#这里要改，要分页
@router.get("/list", summary="课程列表")
def course_list():
    try:
        logging.info("查询全部课程列表")
        select_sql = """
                     select a.*, b.name as teacher_name from courses a
                         left join teachers b
                         on a.teacher_id=b.id
                     """
        res = db.execute_query(select_sql)
        if not res:
            logging.info(f"全部课程查询结果：0条")
            return {"code": 200, "msg": "查询成功", "data": []}
        logging.info(f"全部课程查询结果：{len(res)}条")
        return {"code": 200, "msg": "查询成功", "data": res, "total": len(res)}
    except Exception as e:
        logging.error(f"查询课程信息异常，异常信息：{e}")
        raise HTTPException(status_code=500, detail=f"查询失败: {str(e)}")



@router.post("/add", summary="新增课程")
def course_add(user: courCreate,teacher_id:int):
    try:##name,gender,age,subject,phone
        select_sql = "select * from `courses` where name = %s"
        res = db.execute_query(select_sql, (user.name,))
        if res:
            raise HTTPException(status_code=400, detail="课程已存在")
        insert_sql = "INSERT INTO `courses` (name,credit,teacher_id) VALUES (%s,%s,%s);"
        course_id = db.execute_dml_return_id(insert_sql, (user.name, user.credit, teacher_id))
        logging.info(f"新增课程，插入{course_id}条")
        if not course_id:
            raise HTTPException(status_code=500, detail="课程信息录入失败")
        return {"code": 200, "msg": "添加成功", "course_id": course_id}
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"插入课程信息异常，异常信息：{e}")
        raise HTTPException(status_code=500, detail=f"新增失败: {str(e)}")

@router.put("/update/{sid}", summary="修改课程")
def course_update(sid: int, tea: courUpdate, role: str = "管理员"):
    try:
        if role != "管理员":
            raise HTTPException(status_code=403, detail="仅管理员可修改课程")
        select_sql = "select * from `courses` where id = %s"
        res = db.execute_query(select_sql, (sid,))
        if not res:
            raise HTTPException(status_code=400, detail="课程不存在")

        # 构建动态部分更新 SQL：只更新传入的非 None 字段
        existing = res[0]
        set_clauses = []
        params = []

        for field in ("name", "credit", "teacher_id"):
            val = getattr(tea, field, None)
            if val is not None:
                set_clauses.append(f"`{field}` = %s")
                params.append(val)
            else:
                # 保留原值
                set_clauses.append(f"`{field}` = %s")
                params.append(existing.get(field))

        params.append(sid)
        update_sql = f"UPDATE `courses` SET {', '.join(set_clauses)} WHERE `id` = %s"
        affected = db.execute_dml(update_sql, tuple(params))
        logging.info(f"修改课程 sid={sid}，影响{affected}条")
        return {"code": 200, "msg": "修改成功", "data": affected}
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"修改课程信息异常，异常信息：{e}")
        raise HTTPException(status_code=500, detail=f"修改失败: {str(e)}")

@router.delete("/del/{sid}", summary="删除课程")
def course_del(sid: int, role: str = "管理员"):
    try:
        if role != "管理员":
            raise HTTPException(status_code=403, detail="仅管理员可删除课程")
        select_sql = "select * from `courses` where id = %s"
        res = db.execute_query(select_sql, (sid,))
        if not res:
            raise HTTPException(status_code=400, detail="课程不存在")
        del_sql = "delete from `courses` where `id` = %s"
        res = db.execute_dml(del_sql, (sid,))
        logging.info(f"删除课程 sid={sid}，影响{res}条")

        return {"code": 200, "msg": "删除成功", "data": res}
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"删除课程信息异常，异常信息：{e}")
        raise HTTPException(status_code=500, detail=f"删除失败: {str(e)}")

def select_page_sql(page=1, page_size=10):
    """分页查询用户列表"""
    try:
        # 查总数
        count_sql = "SELECT COUNT(1) AS total FROM `courses`"
        count_res = db.execute_query(count_sql)
        total = count_res[0]['total'] if count_res else 0
        # 查分页数据
        offset = (page - 1) * page_size
        page_sql = """
                     SELECT a.*, t.name AS teacher_name
                     FROM courses a
                     LEFT JOIN teachers t ON a.teacher_id = t.id
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

@router.get("/get_page", summary="课程列表分页查询")
def list_tea_page(page: int = 1, page_size: int = 10):
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


@router.get("/search", summary="多条件查询课程")
def search_tea(course_id: str = "", name: str = ""):
    """按 ID / 姓名 / 手机号单独查询，支持任意组合"""
    try:
        where_parts = []
        params = []

        if course_id.strip():
            where_parts.append("a.id LIKE %s")
            params.append(f"%{course_id.strip()}%")

        if name.strip():
            if len(name.strip()) < 2:
                raise HTTPException(status_code=400, detail="姓名至少输入 2 个字符")
            where_parts.append("a.name LIKE %s")
            params.append(f"%{name.strip()}%")

        if not where_parts:
            raise HTTPException(status_code=400, detail="请至少输入一个查询条件")

        where_clause = " AND ".join(where_parts)
        select_sql = f"""select a.*
                            from courses a
                             WHERE {where_clause} ORDER BY a.id"""
        res = db.execute_query(select_sql, tuple(params))
        logging.info(f"多条件查询到{len(res)}条")
        return {"code": 200, "msg": "查询成功", "data": res, "total": len(res)}
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"搜索异常：{e}")
        raise HTTPException(status_code=500, detail=f"搜索失败: {str(e)}")

@router.put("/assign_teacher/{sid}", summary="课程选老师")
def course_assign_teacher(sid: int, teacher_id: int = None):
    """为课程分配授课老师"""
    try:
        if teacher_id is None:
            raise HTTPException(status_code=400, detail="请提供老师ID")
        upd_sql = "UPDATE `courses` SET teacher_id = %s WHERE id = %s"
        db.execute_dml(upd_sql, (teacher_id, sid))
        logging.info(f"课程 sid={sid} 选老师 teacher_id={teacher_id}")
        return {"code": 200, "msg": "选老师成功"}
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"课程选老师异常：{e}")
        raise HTTPException(status_code=500, detail=f"选老师失败: {str(e)}")
