/* ============================================================
   学校管理系统 - 桌面端左侧固定侧边栏（注入式布局）
   在 .navbar 之后注入 .sidebar，含全部功能模块链接并高亮当前页。
   登录/注册页无 .navbar，不会注入。
   ============================================================ */
(function () {
  var page = (window.location.pathname.split('/').pop()) || 'index.html';

  var items = [
    { href: 'index.html',        icon: '\u{1F3E0}', label: '仪表盘' },
    { href: 'student_list.html', icon: '\u{1F393}', label: '学生管理' },
    { href: 'student_form.html', icon: '➕',    label: '新增学生' },
    { href: 'teacher_list.html', icon: '\u{1F9D1}‍\u{1F3EB}', label: '老师管理' },
    { href: 'classes_list.html', icon: '\u{1F3EB}', label: '班级管理' },
    { href: 'course_list.html',  icon: '\u{1F4DA}', label: '课程管理' },
    { href: 'analytics.html',    icon: '\u{1F4CA}', label: '统计分析' },
    { href: 'custom_sql.html',   icon: '⌨️', label: 'SQL 控制台' }
  ];

  var nav = document.querySelector('.navbar');
  if (!nav) return;

  var aside = document.createElement('aside');
  aside.className = 'sidebar';

  var html = '<div class="side-caption">功能模块</div><nav class="side-nav">';
  for (var i = 0; i < items.length; i++) {
    var it = items[i];
    html += '<a class="' + (page === it.href ? 'active' : '') + '" href="' + it.href + '">' +
            '<span class="s-icon">' + it.icon + '</span><span>' + it.label + '</span></a>';
  }
  html += '</nav>';
  aside.innerHTML = html;

  nav.parentNode.insertBefore(aside, nav.nextSibling);
})();
