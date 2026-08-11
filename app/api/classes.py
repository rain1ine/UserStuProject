import logging

from fastapi import APIRouter, HTTPException
from app.DB import DBmysql
from app.schemas.classes import AddClass

router = APIRouter(
    prefix="/classes",
    tags=["班级管理"]
)

db = DBmysql()


def _class_exists(class_id: int) -> bool:
    """判断班级是否存在"""
    res = db.execute_query("SELECT id FROM classes WHERE id = %s", (class_id,))
    return bool(res)


# 查询全部班级信息
@router.get('/all', summary='查询全部班级')
def classes_list():
    try:
        logging.info('查询全部班级信息')
        sql_query = """
            SELECT c.*, t.name AS head_teacher_name,
                   (SELECT COUNT(*) FROM student s WHERE s.class_id = c.id) AS student_count
            FROM classes c
            LEFT JOIN teachers t ON c.head_teacher_id = t.id
        """
        res = db.execute_query(sql_query)
        if not res:
            logging.info('查询全部班级信息为0条')
            return {"code": 200, "msg": "查询成功", "data": []}
        logging.info(f"全部班级查询结果：{len(res)}条")
        return {"code": 200, "msg": "查询成功", "data": res, "total": len(res)}
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f'查询信息异常：{e}')
        raise HTTPException(status_code=500, detail=f"查询失败: {str(e)}")


# 查询单个班级信息
@router.get('/one/{class_id}', summary='按编号查询班级')
def get_by_id(class_id: int):
    try:
        logging.info(f'查询编号为{class_id}的班级信息')
        sql_query = """
            SELECT c.*, t.name AS head_teacher_name,
                   (SELECT COUNT(*) FROM student s WHERE s.class_id = c.id) AS student_count
            FROM classes c
            LEFT JOIN teachers t ON c.head_teacher_id = t.id
            WHERE c.id = %s
        """
        res = db.execute_query(sql_query, (class_id,))
        if not res:
            raise HTTPException(status_code=404, detail='该班级不存在')
        return {"code": 200, "msg": "查询成功", "data": res[0]}
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f'查询出错：{e}')
        raise HTTPException(status_code=500, detail=f"查询失败: {str(e)}")


# 添加新的班级
@router.post('/add', summary='添加新班级')
def add_class(cla: AddClass):
    try:
        sql = "INSERT INTO classes (name, grade, head_teacher_id) VALUES (%s, %s, %s)"
        res = db.execute_dml(sql, (cla.name, cla.grade, cla.head_teacher_id))
        return {"code": 200, "msg": "添加成功", "data": res}
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f'添加失败：{e}')
        raise HTTPException(status_code=500, detail=f"添加失败: {str(e)}")


# 修改班级信息
@router.put('/update/{class_id}', summary='修改班级信息')
def update_class(class_id: int, cla: AddClass):
    try:
        if not _class_exists(class_id):
            raise HTTPException(status_code=404, detail='该班级不存在')
        sql = "UPDATE classes SET name = %s, grade = %s, head_teacher_id = %s WHERE id = %s"
        res = db.execute_dml(sql, (cla.name, cla.grade, cla.head_teacher_id, class_id))
        return {"code": 200, "msg": "修改成功", "data": res}
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f'修改失败：{e}')
        raise HTTPException(status_code=500, detail=f"修改失败: {str(e)}")


# 删除班级
@router.delete('/delete/{class_id}', summary='删除班级')
def delete_class(class_id: int):
    try:
        if not _class_exists(class_id):
            raise HTTPException(status_code=404, detail='该班级不存在')
        sql = "DELETE FROM classes WHERE id = %s"
        res = db.execute_dml(sql, (class_id,))
        return {"code": 200, "msg": "删除成功", "data": res}
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f'删除失败：{e}')
        raise HTTPException(status_code=500, detail=f"删除失败: {str(e)}")


# 分页
def select_page_sql(page=1, page_size=10):
    """分页查询班级列表（含班主任姓名）"""
    try:
        count_sql = "SELECT COUNT(1) AS total FROM `classes`"
        count_res = db.execute_query(count_sql)
        total = count_res[0]['total'] if count_res else 0
        offset = (page - 1) * page_size
        page_sql = """
                   SELECT a.*, t.name AS head_teacher_name,
                          (SELECT COUNT(*) FROM student s WHERE s.class_id = a.id) AS student_count
                   FROM classes a
                   LEFT JOIN teachers t ON a.head_teacher_id = t.id
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


@router.get("/get_page", summary="班级列表分页查询")
def list_classes_page(page: int = 1, page_size: int = 10):
    """分页查询用户列表"""
    try:
        logging.info(f"分页查询班级，第{page}页，每页{page_size}条")
        result = select_page_sql(page, page_size)
        if result is None:
            raise HTTPException(status_code=500, detail="数据库查询失败")
        return result
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"分页查询异常：{e}")
        raise HTTPException(status_code=500, detail=f"分页查询失败: {str(e)}")


# 各班级学生数统计
@router.get("/student_count", summary="各班级学生数统计")
def class_student_count():
    """返回每个班级的学生人数及汇总（班级总数 / 学生总数 / 未分班人数）"""
    try:
        sql_query = """
            SELECT c.id, c.name, c.grade,
                   (SELECT COUNT(*) FROM student s WHERE s.class_id = c.id) AS student_count
            FROM classes c
            ORDER BY c.id
        """
        rows = db.execute_query(sql_query)

        # 未分班学生数
        unassigned_sql = "SELECT COUNT(*) AS c FROM student WHERE class_id IS NULL"
        unassigned = db.execute_query(unassigned_sql)
        unassigned_count = unassigned[0]['c'] if unassigned else 0

        total_classes = len(rows)
        total_students = sum(int(r.get('student_count') or 0) for r in rows) + unassigned_count

        logging.info(f"班级学生数统计：{total_classes}个班级，共{total_students}名学生（未分班{unassigned_count}）")
        return {
            "code": 200,
            "msg": "查询成功",
            "data": {
                "items": rows,
                "total_classes": total_classes,
                "total_students": total_students,
                "unassigned_count": unassigned_count
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f'统计异常：{e}')
        raise HTTPException(status_code=500, detail=f"统计失败: {str(e)}")


# 为班级变更班主任
@router.put("/assign_classes/{class_id}", summary="变更班主任")
def assign_head_teacher(class_id: int, teacher_id: int = None):
    try:
        if not _class_exists(class_id):
            raise HTTPException(status_code=404, detail='该班级不存在')
        if teacher_id is None:
            raise HTTPException(status_code=400, detail="请提供老师ID")
        upd_sql = "UPDATE `classes` SET head_teacher_id = %s WHERE id = %s"
        db.execute_dml(upd_sql, (teacher_id, class_id))
        logging.info(f"班级 sid={class_id} 选老师 head_teacher_id={teacher_id}")
        return {"code": 200, "msg": "选老师成功"}
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"分班异常：{e}")
        raise HTTPException(status_code=500, detail=f"选老师失败: {str(e)}")
