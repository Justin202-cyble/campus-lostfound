/**
 * 通用工具函数
 */

/**
 * 格式化日期
 */
export function formatDate(isoString) {
    if (!isoString) return '';
    try {
        const d = new Date(isoString);
        const year = d.getFullYear();
        const month = String(d.getMonth() + 1).padStart(2, '0');
        const day = String(d.getDate()).padStart(2, '0');
        const hours = String(d.getHours()).padStart(2, '0');
        const minutes = String(d.getMinutes()).padStart(2, '0');
        return `${year}-${month}-${day} ${hours}:${minutes}`;
    } catch {
        return isoString;
    }
}

/**
 * 相对时间（多久之前）
 */
export function timeAgo(isoString) {
    if (!isoString) return '';
    try {
        const now = new Date();
        const d = new Date(isoString);
        const diff = now - d;
        const seconds = Math.floor(diff / 1000);
        const minutes = Math.floor(seconds / 60);
        const hours = Math.floor(minutes / 60);
        const days = Math.floor(hours / 24);

        if (seconds < 60) return '刚刚';
        if (minutes < 60) return `${minutes}分钟前`;
        if (hours < 24) return `${hours}小时前`;
        if (days < 7) return `${days}天前`;
        if (days < 30) return `${Math.floor(days / 7)}周前`;
        return formatDate(isoString);
    } catch {
        return isoString;
    }
}

/**
 * Toast 提示
 */
export function showToast(message, type = 'info', duration = 3000) {
    const container = document.getElementById('toast-container');
    if (!container) return;

    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;

    const icons = { success: '✅', error: '❌', info: 'ℹ️', warning: '⚠️' };
    toast.innerHTML = `<span>${icons[type] || ''}</span> ${escapeHtml(message)}`;

    container.appendChild(toast);

    setTimeout(() => {
        toast.style.opacity = '0';
        toast.style.transform = 'translateX(100%)';
        toast.style.transition = 'all 0.3s ease';
        setTimeout(() => toast.remove(), 300);
    }, duration);
}

/**
 * HTML 转义
 */
export function escapeHtml(text) {
    if (!text) return '';
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

/**
 * 防抖
 */
export function debounce(fn, delay = 300) {
    let timer;
    return function (...args) {
        clearTimeout(timer);
        timer = setTimeout(() => fn.apply(this, args), delay);
    };
}

/**
 * 解析 URL 查询参数
 */
export function getQueryParams() {
    const hash = window.location.hash;
    const queryIndex = hash.indexOf('?');
    if (queryIndex === -1) return {};
    const queryStr = hash.substring(queryIndex + 1);
    const params = new URLSearchParams(queryStr);
    const result = {};
    for (const [key, value] of params) {
        result[key] = value;
    }
    return result;
}

/**
 * 获取当前 hash 路径（不含查询参数）
 */
export function getHashPath() {
    const hash = window.location.hash;
    const queryIndex = hash.indexOf('?');
    if (queryIndex === -1) return hash.slice(1) || '/';
    return hash.slice(1, queryIndex) || '/';
}

/**
 * 截断文本
 */
export function truncate(text, maxLength = 50) {
    if (!text || text.length <= maxLength) return text || '';
    return text.slice(0, maxLength) + '...';
}

/**
 * 物品类型中文名
 */
export function itemTypeLabel(type) {
    const map = { found: '拾物', lost: '寻物', exchange: '交换' };
    return map[type] || type;
}

/**
 * 物品状态标签
 */
export function statusLabel(status, type) {
    const labelMap = {
        found: { pending: '待认领', claimed: '已认领', resolved: '已解决' },
        lost: { open: '寻找中', found: '已找到', resolved: '已解决' },
        exchange: { available: '可交换', exchanged: '已交换', resolved: '已解决' },
    };
    return (labelMap[type] && labelMap[type][status]) || status;
}

/**
 * 新旧程度标签
 */
export function conditionLabel(condition) {
    const map = {
        'brand_new': '全新',
        'good': '较新',
        'used': '使用过',
        'worn': '有磨损',
    };
    return map[condition] || condition;
}

/**
 * 获取首字母作为头像
 */
export function getInitial(name) {
    if (!name) return '?';
    return name.charAt(0).toUpperCase();
}
