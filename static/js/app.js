/**
 * SPA 路由 & 应用入口
 */

import api from './api.js';
import { showToast } from './utils.js';
import { renderNavbar, updateNavbarState, updateUnreadBadge } from './components/navbar.js';

// 页面渲染函数映射
const routes = {};

// 当前用户状态
let currentUser = null;

/**
 * 注册路由
 */
function route(pattern, renderFn) {
    routes[pattern] = { pattern, renderFn, paramNames: [] };

    // 解析路径参数 :param
    const parts = pattern.split('/');
    const paramNames = [];
    parts.forEach(part => {
        if (part.startsWith(':')) {
            paramNames.push(part.slice(1));
        }
    });
    routes[pattern].paramNames = paramNames;
    routes[pattern].regex = new RegExp(
        '^' + parts.map(p => p.startsWith(':') ? '([^/]+)' : p).join('/') + '$'
    );
}

/**
 * 导航到指定路径
 */
export function navigateTo(path) {
    window.location.hash = '#' + path;
}

/**
 * 渲染当前页面
 */
async function renderPage() {
    const hash = window.location.hash.slice(1) || '/';
    const [path, queryStr] = hash.split('?');
    const container = document.getElementById('app-container');

    if (!container) {
        // 页面还没加载完
        return;
    }

    // 更新导航栏高亮
    updateNavbarState(path);

    // 匹配路由
    let matched = null;
    let params = {};

    for (const [pattern, routeDef] of Object.entries(routes)) {
        if (routeDef.regex) {
            const match = path.match(routeDef.regex);
            if (match) {
                matched = routeDef;
                routeDef.paramNames.forEach((name, i) => {
                    params[name] = match[i + 1];
                });
                break;
            }
        }
    }

    // 简单路径匹配回退
    if (!matched) {
        for (const [pattern, routeDef] of Object.entries(routes)) {
            if (path === pattern || path.startsWith(pattern + '?')) {
                matched = routeDef;
                break;
            }
        }
    }

    // 解析查询参数
    if (queryStr) {
        const sp = new URLSearchParams(queryStr);
        for (const [key, value] of sp) {
            params[key] = value;
        }
    }

    try {
        if (matched) {
            container.innerHTML = '<div class="loading-spinner"><div class="spinner"></div><p>加载中...</p></div>';
            const html = await matched.renderFn(params);
            container.innerHTML = html;
        } else {
            container.innerHTML = `
                <div class="page-container text-center" style="padding-top:80px">
                    <div style="font-size:4rem;margin-bottom:16px">🔍</div>
                    <h2>页面未找到</h2>
                    <p class="text-muted mt">您访问的页面不存在</p>
                    <button class="btn btn-primary mt-md" onclick="window.location.hash='#/'">返回首页</button>
                </div>
            `;
        }
    } catch (error) {
        console.error('页面渲染错误:', error);
        container.innerHTML = `
            <div class="page-container text-center" style="padding-top:80px">
                <div style="font-size:4rem;margin-bottom:16px">😵</div>
                <h2>加载失败</h2>
                <p class="text-muted mt">${error.message}</p>
                <button class="btn btn-primary mt-md" onclick="window.location.reload()">重新加载</button>
            </div>
        `;
    }

    // 滚动到顶部
    window.scrollTo(0, 0);
}

/**
 * 检查登录状态
 */
export async function checkAuth() {
    try {
        const data = await api.get('/api/auth/me');
        currentUser = data.user;
        return currentUser;
    } catch {
        currentUser = null;
        return null;
    }
}

/**
 * 获取当前用户
 */
export function getCurrentUser() {
    return currentUser;
}

/**
 * 设置当前用户
 */
export function setCurrentUser(user) {
    currentUser = user;
    renderNavbar();
    updateUnreadBadge();
}

/**
 * 是否已登录
 */
export function isLoggedIn() {
    return currentUser !== null;
}

/**
 * 是否管理员
 */
export function isAdmin() {
    return currentUser && currentUser.role === 'admin';
}

/**
 * 初始化应用
 */
async function init() {
    // 渲染导航栏
    renderNavbar();

    // 检查登录状态
    await checkAuth();
    renderNavbar();

    // 加载页面模块
    await loadPages();

    // 监听 hash 变化
    window.addEventListener('hashchange', renderPage);

    // 监听未登录事件
    window.addEventListener('auth:required', () => {
        showToast('请先登录', 'warning');
        navigateTo('/login');
    });

    // 首次渲染
    await renderPage();

    // 更新未读消息/通知徽章
    updateUnreadBadge();

    console.log('🚀 智慧校园失物招领与物品交换平台已启动');
}

/**
 * 动态加载页面模块
 */
async function loadPages() {
    const pageModules = {
        '/': () => import('./pages/home.js'),
        '/login': () => import('./pages/auth.js'),
        '/register': () => import('./pages/auth.js'),
        '/found': () => import('./pages/found-items.js'),
        '/lost': () => import('./pages/lost-items.js'),
        '/exchange': () => import('./pages/exchange-items.js'),
        '/item/found/:id': () => import('./pages/item-detail.js'),
        '/item/lost/:id': () => import('./pages/item-detail.js'),
        '/item/exchange/:id': () => import('./pages/item-detail.js'),
        '/post': () => import('./pages/post-item.js'),
        '/messages': () => import('./pages/messages.js'),
        '/notifications': () => import('./pages/notifications.js'),
        '/profile': () => import('./pages/profile.js'),
        '/admin': () => import('./pages/admin.js'),
    };

    for (const [pattern, loader] of Object.entries(pageModules)) {
        try {
            const module = await loader();
            const renderFn = module.default || module.render;
            if (typeof renderFn === 'function') {
                route(pattern, renderFn);
            }
        } catch (error) {
            console.warn(`页面模块加载失败: ${pattern}`, error);
        }
    }
}

// 启动应用
document.addEventListener('DOMContentLoaded', init);
