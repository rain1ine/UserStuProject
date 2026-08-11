from fastapi import APIRouter, HTTPException
from app.DB import DBmysql

router = APIRouter(
    prefix="/model",
    tags=["统计分析"]
)
db = DBmysql()


@router.get("/list", summary="数据模型统计")
def model_list():
    """返回饼图统计数据：年级分布 + 性别分布"""
    try:
        gender_data = db.execute_query(
            "SELECT gender as name, COUNT(*) as value FROM student GROUP BY gender")
        grade_data = db.execute_query(
            "SELECT grade as name, COUNT(*) as value FROM student GROUP BY grade")
        return {
            "code": 200,
            "data": {
                "gender": [{"name": r['name'] or '未知', "value": r['value']} for r in gender_data],
                "class": [{"name": r['name'] or '未知', "value": r['value']} for r in grade_data]
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
