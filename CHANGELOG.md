# 项目变更记录 (CHANGELOG)

## 2026-08-08 (第二次) — 全面审计修复

### 后端修复

| 文件 | 修复内容 |
|------|---------|
| `Dockerfile` | 修复 COPY 路径（`app.api.student.py` → `COPY app/ app/`），保留目录结构 |
| `app/api/user.py` | ① 登录验证密码（SHA256 哈希比对）② 修复 `res.id` → `res[0]['id']` ③ 修复 get_user_info SQL `username` → `id` ④ 密码哈希存储 ⑤ 修复 HTTPException 被外层 try 吞掉 |
| `app/api/student.py` | ① 修复 update/delete 路径参数 `id` → `sid` ② 搜索接口 `DELETE` → `GET`，`execute_dml` → `execute_query` ③ 列表返回完整数据而非 count ④ 限制自定义 SQL 仅允许 SELECT ⑤ 修复所有端点 HTTPException 吞没问题 ⑥ update 支持部分字段更新 |
| `app/DB.py` | ① 数据库连接改为读取环境变量（`DB_HOST`/`DB_USER`/`DB_PASS`/`DB_NAME`）② 日志文件 `playgamelog.log` → `school.log` |
| `app/main.py` | ① `goods_router` → `student_router` ② CORS `allow_credentials=False` ③ `uvicorn.run("app.main:app")` |
| `app/schemas/student.py` | StuUpdate 字段改为全部 Optional（支持部分更新） |
| `app/schemas/user.py` | `orm_mode = True` → `model_config = {"from_attributes": True}` (Pydantic v2) |
| `init.sql` | 普通 `INSERT` → `INSERT IGNORE`，避免重启时重复键报错 |

### 前端修复

| 文件 | 修复内容 |
|------|---------|
| `static/js/api.js` | ① 增加 `code` 字段检查（应用层错误码处理）② 增加 15s 超时 `AbortController` ③ `API_BASE` 同源自动用相对路径 ④ `encodeURIComponent` 转义 URL 参数 ⑤ 新增 `apiSearchStudent` |
| `static/student_list.html` | ① 搜索改为全量拉取+客户端分页（跨页搜索）② 按钮改用 DOM API + 事件监听（防引号/XSS）③ 删除/编辑按钮不再使用 inline onclick 拼接字符串 ④ 编辑时将数据写入 sessionStorage |
| `static/student_form.html` | ① 编辑模式优先从 sessionStorage 读取数据 ② 修复 `editId` 为 0 的边界情况 ③ 回退方案 page_size 扩大至 500 |
| `static/custom_sql.html` | ① SQL 结果渲染改用 `textContent`/DOM API（防 XSS）② 结果最多显示 200 行 ③ 错误消息改用 `textContent` |
| `static/login.html` | 修复 `uid` 为 0 的 falsy 检查问题 |
| `static/index.html` | 合并两次 API 调用为一次（同时获取 total + 性别分布） |
| 所有 HTML | `user-scalable=no` 移除，`maximum-scale=5.0`（可访问性） |

---

## 2026-08-08 (第一次) — 新增前端 H5 静态页面

### 新增文件

**`static/` 目录** — 学校管理系统前端 H5 静态页面（移动端优先响应式设计）

| 文件 | 说明 |
|------|------|
| `static/css/style.css` | 全局样式表，蓝色学校主题，移动端/平板/桌面三档响应式 |
| `static/js/api.js` | API 请求封装（fetch），包含所有后端接口调用 |
| `static/js/auth.js` | 认证守卫：登录状态管理、登出、Toast 通知、Loading 遮罩、确认弹窗 |
| `static/login.html` | 登录页 |
| `static/register.html` | 注册页（含两次密码校验） |
| `static/index.html` | 主控制台（统计卡片 + 功能导航卡片） |
| `static/student_list.html` | 学生列表页（分页 + 搜索 + 表格/卡片双视图 + 删除确认） |
| `static/student_form.html` | 新增/编辑学生表单（通过 URL 参数区分模式） |
| `static/custom_sql.html` | 自定义 SQL 查询页（快捷查询模板 + 结果展示表格） |

### 修改文件

**`app/main.py`** — 新增 CORS 中间件 + 挂载静态文件目录

已完成。最终修复了 3 个静默吞异常点：

###点击显示全部学生,一直在加载,无法显示出来
文件	行	修复
app/DB.py	execute_query()	已有 raise ✅
app/DB.py	execute_dml()	新增 raise（之前静默返回 None）
app/api/student.py	select_page_sql()	改为 raise（之前静默返回 None）
app/api/student.py	/get_page 端点	新增 None 检测 + HTTPException
现在所有数据库异常都会正确传播到前端，不会出现"卡在加载中"的情况。点击 📋 显示全部学生：

数据库可连接 → 显示数据或"无数据"提示
数据库不可连接 → 显示红色错误 Toast + 停止加载动画