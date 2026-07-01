/**
 * 通知中心页面
 */

import api from '../api.js';
import { isLoggedIn, navigateTo } from '../app.js';
import { timeAgo, showToast } from '../utils.js';
import { updateUnreadBadge } from '../components/navbar.js';
import { renderPagination } from '../components/pagination.js';

export default async function renderNotificationsPage() {
    if (!isLoggedIn()) {
        navigateTo('/login');
        return '<div class="page-container text-center"><p>正在跳转...</p></div>';
    }

    let notifData = { notifications: [], total: 0, page: 1, pages: 1 };

    try {
        notifData = await api.get('/api/notifications', { page: 1, per_page: 20 });
    } catch (e) {
        showToast('加载失败: ' + e.message, 'error');
    }

    const typeIcons = {
        match: { icon: '🔔', bg: '#FEF3C7' },
        message: { icon: '💬', bg: '#EFF6FF' },
        system: { icon: '📢', bg: '#ECFDF5' },
    };

    setTimeout(() => {
        bindNotifEvents();
    }, 0);

    return `
        <div class="page-container">
            <div class="flex items-center justify-between mb-md">
                <h1>🔔 通知中心</h1>
                ${notifData.total > 0 ? `
                    <button class="btn btn-outline btn-sm" id="readAllBtn">全部标为已读</button>
                ` : ''}
            </div>

            <div class="notification-list">
                ${notifData.notifications.length === 0 ? `
                    <div class="empty-state">
                        <div class="icon">🔔</div>
                        <p>暂无通知</p>
                    </div>
                ` : notifData.notifications.map(n => {
                    const typeInfo = typeIcons[n.notification_type] || typeIcons.system;
                    const relatedLink = n.related_item_id && n.related_item_type
                        ? `#/item/${n.related_item_type}/${n.related_item_id}`
                        : '#';

                    return `
                        <div class="notification-item ${n.is_read ? '' : 'unread'}"
                             data-id="${n.id}" data-link="${relatedLink}">
                            <div class="notification-icon" style="background:${typeInfo.bg}">
                                ${typeInfo.icon}
                            </div>
                            <div class="notification-content">
                                <div class="notification-title">${n.title}</div>
                                <div class="notification-body">${n.content}</div>
                                <div class="notification-time">${timeAgo(n.created_at)}</div>
                            </div>
                            ${!n.is_read ? '<span style="color:var(--primary);font-size:0.7rem">●</span>' : ''}
                        </div>
                    `;
                }).join('')}
            </div>

            ${renderPagination(notifData.page, notifData.pages, async (page) => {
                window.location.hash = `#/notifications?page=${page}`;
            })}
        </div>
    `;
}

function bindNotifEvents() {
    // 全部已读
    document.getElementById('readAllBtn')?.addEventListener('click', async () => {
        try {
            await api.put('/api/notifications/read-all');
            showToast('已全部标为已读', 'success');
            await updateUnreadBadge();
            window.location.reload();
        } catch (e) {
            showToast('操作失败', 'error');
        }
    });

    // 点击通知
    document.querySelector('.notification-list')?.addEventListener('click', async (e) => {
        const item = e.target.closest('.notification-item');
        if (!item) return;

        const notifId = item.dataset.id;
        const link = item.dataset.link;

        // 标记已读
        try {
            await api.put(`/api/notifications/${notifId}/read`);
            await updateUnreadBadge();
        } catch (e) {
            // 忽略
        }

        // 跳转
        if (link && link !== '#') {
            window.location.hash = link;
        }
    });
}
