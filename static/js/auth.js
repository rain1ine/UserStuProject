/* ============================================================
   学校管理系统 - 认证守卫 & 会话管理
   ============================================================ */

const AUTH_KEY = 'school_user';

/**
 * 保存登录用户信息到 localStorage
 * @param {object} user - { uid, username, nickname }
 */
function saveUser(user) {
  localStorage.setItem(AUTH_KEY, JSON.stringify(user));
}

/**
 * 获取当前登录用户
 * @returns {object|null}
 */
function getUser() {
  const raw = localStorage.getItem(AUTH_KEY);
  if (!raw) return null;
  try {
    return JSON.parse(raw);
  } catch (e) {
    return null;
  }
}

/**
 * 检查登录状态：未登录则跳转登录页
 * @returns {object} 当前用户信息
 */
function checkAuth() {
  const user = getUser();
  if (!user) {
    window.location.href = 'login.html';
    throw new Error('未登录');
  }
  return user;
}

/**
 * 退出登录
 */
function logout() {
  localStorage.removeItem(AUTH_KEY);
  window.location.href = 'login.html';
}

/**
 * 显示 Toast 消息
 * @param {string} msg - 消息文本
 * @param {'success'|'error'|'warning'} type - 消息类型
 * @param {number} duration - 显示时长（毫秒）
 */
function showToast(msg, type, duration) {
  type = type || 'success';
  duration = duration || 2000;

  // 确保容器存在
  var container = document.querySelector('.toast-container');
  if (!container) {
    container = document.createElement('div');
    container.className = 'toast-container';
    document.body.appendChild(container);
  }

  var toast = document.createElement('div');
  toast.className = 'toast ' + type;
  toast.textContent = msg;
  container.appendChild(toast);

  setTimeout(function() {
    toast.style.transition = 'opacity 0.3s';
    toast.style.opacity = '0';
    setTimeout(function() {
      if (toast.parentNode) toast.parentNode.removeChild(toast);
    }, 300);
  }, duration);
}

/**
 * 显示/隐藏全屏 loading
 * @param {boolean} visible
 * @param {string} text
 */
function toggleLoading(visible, text) {
  var el = document.getElementById('loading-overlay');
  if (!el) {
    el = document.createElement('div');
    el.id = 'loading-overlay';
    el.className = 'loading';
    el.innerHTML = '<div class="spinner"></div><div class="text"></div>';
    document.body.appendChild(el);
  }
  if (visible) {
    el.className = 'loading show';
    el.querySelector('.text').textContent = text || '加载中...';
  } else {
    el.className = 'loading';
  }
}

/**
 * 显示确认弹窗
 * @param {string} title
 * @param {string} message
 * @returns {Promise<boolean>}
 */
function showConfirm(title, message) {
  return new Promise(function(resolve) {
    var overlay = document.createElement('div');
    overlay.className = 'modal-overlay show';
    overlay.innerHTML =
      '<div class="modal">' +
        '<div class="modal-title">' + title + '</div>' +
        '<div class="modal-body">' + message + '</div>' +
        '<div class="modal-footer">' +
          '<button class="btn btn-outline btn-sm" id="modal-cancel">取消</button>' +
          '<button class="btn btn-danger btn-sm" id="modal-confirm">确认</button>' +
        '</div>' +
      '</div>';
    document.body.appendChild(overlay);

    function cleanup() {
      overlay.className = 'modal-overlay';
      setTimeout(function() {
        if (overlay.parentNode) overlay.parentNode.removeChild(overlay);
      }, 200);
    }

    overlay.querySelector('#modal-cancel').onclick = function() { cleanup(); resolve(false); };
    overlay.querySelector('#modal-confirm').onclick = function() { cleanup(); resolve(true); };
    overlay.onclick = function(e) { if (e.target === overlay) { cleanup(); resolve(false); } };
  });
}
