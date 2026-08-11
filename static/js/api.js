/* ============================================================
   学校管理系统 - API 请求封装
   ============================================================ */

// 自动检测 API 基础地址：同源优先，否则用 8000 端口（开发模式）
var API_BASE = (function () {
  if (window.location.port === '8000') {
    return ''; // 同源，直接用相对路径
  }
  return window.location.protocol + '//' + window.location.hostname + ':8000';
})();

/**
 * 通用请求函数
 * @param {string} method - HTTP 方法
 * @param {string} path - API 路径 (如 /user/login)
 * @param {object|null} body - 请求体（GET/HEAD 自动忽略）
 * @param {number} timeout - 超时时间（毫秒），默认 15 秒
 * @returns {Promise<object>} 解析后的响应 JSON
 */
function request(method, path, body, timeout) {
  var url = API_BASE + path;
  timeout = timeout || 15000;

  var opts = {
    method: method,
    headers: { 'Content-Type': 'application/json' },
  };
  if (body && method !== 'GET' && method !== 'HEAD') {
    opts.body = JSON.stringify(body);
  }

  var controller = new AbortController();
  opts.signal = controller.signal;
  var timeoutId = setTimeout(function () { controller.abort(); }, timeout);

  var res;
  return fetch(url, opts)
    .then(function (r) {
      clearTimeout(timeoutId);
      res = r;
      return r.json().catch(function () { return null; });
    })
    .then(function (data) {
      if (!res.ok) {
        var detail = (data && data.detail) ? data.detail : ('请求失败 HTTP ' + res.status);
        throw new Error(typeof detail === 'string' ? detail : JSON.stringify(detail));
      }
      // 应用层错误：code 非 200 视为失败
      if (data && data.code !== undefined && String(data.code) !== '200') {
        throw new Error(data.msg || data.detail || ('请求失败 code=' + data.code));
      }
      return data;
    })
    .catch(function (e) {
      clearTimeout(timeoutId);
      if (e.name === 'AbortError') {
        throw new Error('请求超时，请检查网络连接');
      }
      throw e;
    });
}

/** 拼接查询参数（自动忽略空值） */
function qs(params) {
  var parts = [];
  for (var k in params) {
    var v = params[k];
    if (v === null || v === undefined || v === '') continue;
    parts.push(encodeURIComponent(k) + '=' + encodeURIComponent(v));
  }
  return parts.length ? ('?' + parts.join('&')) : '';
}

// ===================== 用户 API =====================

/** 用户注册：data = {username, password, nickname, role, name?, gender?, age?, phone_number?, birthday?} */
function apiRegister(data) {
  return request('POST', '/user/register', data);
}

/** 用户登录：role = '管理员' | '学生' */
function apiLogin(username, password, role) {
  return request('POST', '/user/login', { username: username, password: password, role: role });
}

/** 获取用户信息 */
function apiGetUserInfo(uid) {
  return request('GET', '/user/info' + qs({ uid: uid }));
}

// ===================== 学生 API =====================

/** 分页获取学生列表 */
function apiGetStudentPage(page, pageSize) {
  return request('GET', '/student/get_page' + qs({ page: page, page_size: pageSize }));
}

/** 获取全部学生列表（不分页，含班级/老师名） */
function apiGetAllStudents() {
  return request('GET', '/student/list');
}

/** 新增学生：{name, gender, age, phone_number, birthday} */
function apiAddStudent(data) {
  return request('POST', '/student/add', data);
}

/** 修改学生：只传需更新的字段 */
function apiUpdateStudent(id, data) {
  return request('PUT', '/student/update/' + encodeURIComponent(id), data);
}

/** 删除学生 */
function apiDeleteStudent(id) {
  return request('DELETE', '/student/del/' + encodeURIComponent(id));
}

/** 多条件搜索学生：student_id / name / phone 任意组合 */
function apiSearchStudent(params) {
  return request('GET', '/student/search' + qs(params));
}

/** 学生分班：class_id 必传 */
function apiAssignClass(studentId, classId) {
  return request('PUT', '/student/assign_class/' + encodeURIComponent(studentId) + qs({ class_id: classId }));
}

/** 学生选老师：teacher_id 必传 */
function apiAssignTeacher(studentId, teacherId) {
  return request('PUT', '/student/assign_teachers/' + encodeURIComponent(studentId) + qs({ teacher_id: teacherId }));
}

/** 自定义 SQL（后端仅允许 SELECT/SHOW/DESC 等只读查询） */
function apiCustomQuery(sql) {
  return request('POST', '/student/custom_query', { sql: sql });
}

// ===================== 老师 API =====================

/** 分页获取老师列表 */
function apiGetTeacherPage(page, pageSize) {
  return request('GET', '/teacher/get_page' + qs({ page: page, page_size: pageSize }));
}

/** 获取全部老师列表（供下拉选择） */
function apiGetAllTeachers() {
  return request('GET', '/teacher/list');
}

/** 新增老师：{name, gender, age, subject, phone} */
function apiAddTeacher(data) {
  return request('POST', '/teacher/add', data);
}

/** 修改老师：只传需更新的字段 */
function apiUpdateTeacher(id, data) {
  return request('PUT', '/teacher/update/' + encodeURIComponent(id), data);
}

/** 删除老师 */
function apiDeleteTeacher(id) {
  return request('DELETE', '/teacher/del/' + encodeURIComponent(id));
}

/** 多条件搜索老师：teacher_id / name / phone */
function apiSearchTeacher(params) {
  return request('GET', '/teacher/search' + qs(params));
}

// ===================== 班级 API =====================

/** 分页获取班级列表（含班主任姓名） */
function apiGetClassPage(page, pageSize) {
  return request('GET', '/classes/get_page' + qs({ page: page, page_size: pageSize }));
}

/** 获取全部班级列表（供下拉选择） */
function apiGetAllClasses() {
  return request('GET', '/classes/all');
}

/** 新增班级：{name, grade, head_teacher_id} */
function apiAddClass(data) {
  return request('POST', '/classes/add', data);
}

/** 修改班级 */
function apiUpdateClass(id, data) {
  return request('PUT', '/classes/update/' + encodeURIComponent(id), data);
}

/** 删除班级 */
function apiDeleteClass(id) {
  return request('DELETE', '/classes/delete/' + encodeURIComponent(id));
}

/** 变更班主任：teacher_id 必传 */
function apiAssignHeadTeacher(classId, teacherId) {
  return request('PUT', '/classes/assign_classes/' + encodeURIComponent(classId) + qs({ teacher_id: teacherId }));
}

/** 各班级学生数统计：返回 { items: [{id,name,grade,student_count}], total_classes, total_students, unassigned_count } */
function apiClassStudentCount() {
  return request('GET', '/classes/student_count');
}

// ===================== 课程 API =====================

/** 分页获取课程列表（含任课老师姓名） */
function apiGetCoursePage(page, pageSize) {
  return request('GET', '/course/get_page' + qs({ page: page, page_size: pageSize }));
}

/** 获取全部课程列表 */
function apiGetAllCourses() {
  return request('GET', '/course/list');
}

/** 新增课程：{name, credit} + teacher_id（query 参数） */
function apiAddCourse(data, teacherId) {
  return request('POST', '/course/add' + qs({ teacher_id: teacherId }), data);
}

/** 修改课程：只传需更新的字段 */
function apiUpdateCourse(id, data) {
  return request('PUT', '/course/update/' + encodeURIComponent(id), data);
}

/** 删除课程 */
function apiDeleteCourse(id) {
  return request('DELETE', '/course/del/' + encodeURIComponent(id));
}

/** 多条件搜索课程：course_id / name */
function apiSearchCourse(params) {
  return request('GET', '/course/search' + qs(params));
}

/** 课程选老师：teacher_id 必传 */
function apiCourseAssignTeacher(courseId, teacherId) {
  return request('PUT', '/course/assign_teacher/' + encodeURIComponent(courseId) + qs({ teacher_id: teacherId }));
}

// ===================== 统计分析 API =====================

/** 数据模型统计：性别分布 + 年级分布 */
function apiModelStats() {
  return request('GET', '/model/list');
}
