import re
from fastapi import APIRouter, HTTPException

from app.api.user import _hash_password
from app.schemas.teacher import TeaCreate,TeaUpdate
from app.DB import DBmysql
from app.DB import logging

router = APIRouter(
    prefix="/teacher",
    tags=["老师管理"]
)
db=DBmysql()

#这里要改，要分页
@router.get("/list", summary="老师列表")
def teacher_list():
    try:
        logging.info("查询全部老师列表")
        select_sql = """
                     select a.* from teachers a
                     """
        res = db.execute_query(select_sql)
        if not res:
            logging.info(f"全部老师查询结果：0条")
            return {"code": 200, "msg": "查询成功", "data": []}
        logging.info(f"全部老师查询结果：{len(res)}条")
        return {"code": 200, "msg": "查询成功", "data": res, "total": len(res)}
    except Exception as e:
        logging.error(f"查询老师信息异常，异常信息：{e}")
        raise HTTPException(status_code=500, detail=f"查询失败: {str(e)}")


@router.post("/add", summary="新增老师")
def teacher_add(user: TeaCreate):
    try:##name,gender,age,subject,phone
        select_sql = "select * from `teachers` where name = %s"
        res = db.execute_query(select_sql, (user.name,))
        if res:
            raise HTTPException(status_code=400, detail="老师已存在")
        insert_sql = "INSERT INTO `teachers` (name,gender,age,subject,phone) VALUES (%s,%s,%s,%s,%s);"
        teacher_id = db.execute_dml_return_id(insert_sql, (user.name, user.gender, user.age, user.subject, user.phone))
        logging.info(f"新增老师，插入{teacher_id}条")
        if not teacher_id:
            raise HTTPException(status_code=500, detail="老师信息录入失败")
        return {"code": 200, "msg": "添加成功", "teacher_id": teacher_id}
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"插入老师信息异常，异常信息：{e}")
        raise HTTPException(status_code=500, detail=f"新增失败: {str(e)}")

@router.put("/update/{sid}", summary="修改老师")
def teacher_update(sid: int, tea: TeaUpdate, role: str = "管理员"):
    try:
        if role != "管理员":
            raise HTTPException(status_code=403, detail="仅管理员可修改老师")
        select_sql = "select * from `teachers` where id = %s"
        res = db.execute_query(select_sql, (sid,))
        if not res:
            raise HTTPException(status_code=400, detail="老师不存在")

        # 构建动态部分更新 SQL：只更新传入的非 None 字段
        existing = res[0]
        set_clauses = []
        params = []

        for field in ("name", "gender", "age", "subject", "phone"):
            val = getattr(tea, field, None)
            if val is not None:
                set_clauses.append(f"`{field}` = %s")
                params.append(val)
            else:
                # 保留原值
                set_clauses.append(f"`{field}` = %s")
                params.append(existing.get(field))

        params.append(sid)
        update_sql = f"UPDATE `teachers` SET {', '.join(set_clauses)} WHERE `id` = %s"
        affected = db.execute_dml(update_sql, tuple(params))
        logging.info(f"修改老师 sid={sid}，影响{affected}条")
        return {"code": 200, "msg": "修改成功", "data": affected}
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"修改老师信息异常，异常信息：{e}")
        raise HTTPException(status_code=500, detail=f"修改失败: {str(e)}")

@router.delete("/del/{sid}", summary="删除老师")
def teacher_del(sid: int, role: str = "管理员"):
    try:
        if role != "管理员":
            raise HTTPException(status_code=403, detail="仅管理员可删除老师")
        select_sql = "select * from `teachers` where id = %s"
        res = db.execute_query(select_sql, (sid,))
        if not res:
            raise HTTPException(status_code=400, detail="老师不存在")
        del_sql = "delete from `teachers` where `id` = %s"
        res = db.execute_dml(del_sql, (sid,))
        logging.info(f"删除老师 sid={sid}，影响{res}条")

        return {"code": 200, "msg": "删除成功", "data": res}
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"删除老师信息异常，异常信息：{e}")
        raise HTTPException(status_code=500, detail=f"删除失败: {str(e)}")

def select_page_sql(page=1, page_size=10):
    """分页查询用户列表"""
    try:
        # 查总数
        count_sql = "SELECT COUNT(1) AS total FROM `teachers`"
        count_res = db.execute_query(count_sql)
        total = count_res[0]['total'] if count_res else 0
        # 查分页数据
        offset = (page - 1) * page_size
        page_sql = """
                     select a.* 
                            from teachers a
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

@router.get("/get_page", summary="老师列表分页查询")
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


@router.get("/search", summary="多条件查询老师")
def search_tea(teacher_id: str = "", name: str = "", phone: str = ""):
    """按 ID / 姓名 / 手机号单独查询，支持任意组合"""
    try:
        where_parts = []
        params = []

        if teacher_id.strip():
            where_parts.append("a.id LIKE %s")
            params.append(f"%{teacher_id.strip()}%")

        if name.strip():
            if len(name.strip()) < 2:
                raise HTTPException(status_code=400, detail="姓名至少输入 2 个字符")
            where_parts.append("a.name LIKE %s")
            params.append(f"%{name.strip()}%")

        if phone.strip():
            digits = re.sub(r'\D', '', phone.strip())
            if len(digits) < 11:
                raise HTTPException(status_code=400, detail="手机号至少输入 11 位数字")
            where_parts.append("a.phone LIKE %s")
            params.append(f"%{phone.strip()}%")

        if not where_parts:
            raise HTTPException(status_code=400, detail="请至少输入一个查询条件")

        where_clause = " AND ".join(where_parts)
        select_sql = f"""select a.*
                            from teachers a
                             WHERE {where_clause} ORDER BY a.id"""
        res = db.execute_query(select_sql, tuple(params))
        logging.info(f"多条件查询到{len(res)}条")
        return {"code": 200, "msg": "查询成功", "data": res, "total": len(res)}
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"搜索异常：{e}")
        raise HTTPException(status_code=500, detail=f"搜索失败: {str(e)}")


