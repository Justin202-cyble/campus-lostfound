/**
 * 顶部导航栏组件
 */

import { isLoggedIn, isAdmin, getCurrentUser } from '../app.js';
import api from '../api.js';
import { getInitial } from '../utils.js';

let unreadNotifCount = 0;
let unreadMsgCount = 0;

/**
 * 渲染导航栏
 */
export function renderNavbar() {
    const nav = document.getElementById('navbar');
    if (!nav) return;

    const user = getCurrentUser();
    const loggedIn = isLoggedIn();

    nav.innerHTML = `
        <div class="navbar">
            <div class="navbar-inner">
                <!-- Logo -->
                <div class="navbar-brand" onclick="window.location.hash='#/'">
                    <span class="brand-icon">🏫</span>
                    <span>校园失物招领</span>
                </div>

                <!-- 移动端菜单按钮 -->
                <button class="navbar-toggle" id="navbarToggle" aria-label="菜单">
                    ☰
                </button>

                <!-- 导航链接 -->
                <div class="navbar-links" id="navbarLinks">
                    <a href="#/" data-route="/">首页</a>
                    <a href="#/found" data-route="/found">拾物招领</a>
                    <a href="#/lost" data-route="/lost">寻物启事</a>
                    <a href="#/exchange" data-route="/exchange">物品交换</a>

                    ${loggedIn ? `
                        <a href="#/post" data-route="/post" style="color:var(--success);font-weight:600">
                            ✏️ 发布信息
                        </a>
                        <a href="#/messages" data-route="/messages" class="nav-msg-link">
                            💬 消息
                            ${unreadMsgCount > 0 ? `<span class="nav-badge">${unreadMsgCount > 99 ? '99+' : unreadMsgCount}</span>` : ''}
                        </a>
                        <a href="#/notifications" data-route="/notifications" class="nav-notif-link">
                            🔔 通知
                            ${unreadNotifCount > 0 ? `<span class="nav-badge">${unreadNotifCount > 99 ? '99+' : unreadNotifCount}</span>` : ''}
                        </a>
                        ${isAdmin() ? `<a href="#/admin" data-route="/admin">📊 管理后台</a>` : ''}
                        <div class="navbar-user" onclick="window.location.hash='#/profile'">
                            <div class="navbar-avatar">${getInitial(user?.username || '?')}</div>
                            <span class="navbar-username">${user?.username || ''}</span>
                        </div>
                        <button class="nav-btn" id="logoutBtn" style="color:var(--text-muted)">退出</button>
                    ` : `
                        <a href="#/login" data-route="/login" class="btn btn-primary btn-sm">登录</a>
                    `}
                </div>
            </div>
        </div>
    `;

    // 绑定事件
    bindEvents();
}

/**
 * 绑定导航栏事件
 */
function bindEvents() {
    // 移动端菜单切换
    const toggle = document.getElementById('navbarToggle');
    const links = document.getElementById('navbarLinks');
    if (toggle && links) {
        toggle.addEventListener('click', () => {
            links.classList.toggle('open');
        });

        // 点击链接后关闭菜单
        links.querySelectorAll('a').forEach(link => {
            link.addEventListener('click', () => {
                links.classList.remove('open');
            });
        });
    }

    // 退出登录
    const logoutBtn = document.getElementById('logoutBtn');
    if (logoutBtn) {
        logoutBtn.addEventListener('click', async () => {
            try {
                await api.post('/api/auth/logout');
                window.location.reload();
            } catch (e) {
                console.error('退出失败', e);
            }
        });
    }
}

/**
 * 更新导航栏高亮状态
 */
export function updateNavbarState(currentPath) {
    const links = document.querySelectorAll('.navbar-links [data-route]');
    links.forEach(link => {
        const route = link.getAttribute('data-route');
        link.classList.remove('active');
        if (route === currentPath || (route !== '/' && currentPath.startsWith(route))) {
            link.classList.add('active');
        }
    });
}

/**
 * 更新未读消息和通知徽章
 */
export async function updateUnreadBadge() {
    if (!isLoggedIn()) return;

    try {
        const [notifData, msgData] = await Promise.all([
            api.get('/api/notifications/unread-count').catch(() => ({ count: 0 })),
            api.get('/api/messages/unread-count').catch(() => ({ count: 0 })),
        ]);
        unreadNotifCount = notifData.count || 0;
        unreadMsgCount = msgData.count || 0;
    } catch {
        unreadNotifCount = 0;
        unreadMsgCount = 0;
    }

    // 更新DOM
    const notifLink = document.querySelector('.nav-notif-link');
    const msgLink = document.querySelector('.nav-msg-link');

    if (notifLink) {
        const badge = notifLink.querySelector('.nav-badge');
        if (unreadNotifCount > 0) {
            if (badge) {
                badge.textContent = unreadNotifCount > 99 ? '99+' : unreadNotifCount;
            } else {
                const span = document.createElement('span');
                span.className = 'nav-badge';
                span.textContent = unreadNotifCount > 99 ? '99+' : unreadNotifCount;
                notifLink.appendChild(span);
            }
        } else if (badge) {
            badge.remove();
        }
    }

    if (msgLink) {
        const badge = msgLink.querySelector('.nav-badge');
        if (unreadMsgCount > 0) {
            if (badge) {
                badge.textContent = unreadMsgCount > 99 ? '99+' : unreadMsgCount;
            } else {
                const span = document.createElement('span');
                span.className = 'nav-badge';
                span.textContent = unreadMsgCount > 99 ? '99+' : unreadMsgCount;
                msgLink.appendChild(span);
            }
        } else if (badge) {
            badge.remove();
        }
    }
}
