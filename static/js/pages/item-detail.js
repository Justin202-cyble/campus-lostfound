/**
 * 物品详情页
 */

import api from '../api.js';
import { isLoggedIn, getCurrentUser, navigateTo } from '../app.js';
import { formatDate, timeAgo, statusLabel, itemTypeLabel, conditionLabel, showToast, getInitial } from '../utils.js';

export default async function renderItemDetail(params) {
    const itemType = params.type || 'found';
    const itemId = params.id;

    if (!itemId) {
        return '<div class="page-container text-center"><h2>无效的物品ID</h2></div>';
    }

    let item = null;
    try {
        const data = await api.get(`/api/items/${itemType}/${itemId}`);
        item = data.item;
    } catch (e) {
        return `<div class="page-container text-center"><h2>加载失败</h2><p>${e.message}</p></div>`;
    }

    if (!item) {
        return '<div class="page-container text-center"><h2>物品不存在或已删除</h2></div>';
    }

    const user = getCurrentUser();
    const isOwner = user && user.id === item.user_id;

    // 状态信息
    let statusHtml = '';
    if (itemType === 'found') {
        const tags = { pending: 'tag-warning', claimed: 'tag-info', resolved: 'tag-success' };
        statusHtml = `<span class="tag ${tags[item.status] || 'tag-info'}">${statusLabel(item.status, 'found')}</span>`;
    } else if (itemType === 'lost') {
        const tags = { open: 'tag-danger', found: 'tag-info', resolved: 'tag-success' };
        statusHtml = `<span class="tag ${tags[item.status] || 'tag-info'}">${statusLabel(item.status, 'lost')}</span>`;
    } else {
        const tags = { available: 'tag-success', exchanged: 'tag-info', resolved: 'tag-success' };
        statusHtml = `<span class="tag ${tags[item.status] || 'tag-info'}">${statusLabel(item.status, 'exchange')}</span>`;
    }

    // 位置/时间信息
    let metaHtml = '';
    if (itemType === 'found') {
        metaHtml = `
            <span>📍 ${item.location_found || '未知'}</span>
            <span>🕐 ${formatDate(item.found_time)}</span>
        `;
    } else if (itemType === 'lost') {
        metaHtml = `
            <span>📍 ${item.location_lost || '未知'}</span>
            <span>🕐 ${formatDate(item.lost_time)}</span>
        `;
    } else {
        metaHtml = `
            <span>🏷️ ${conditionLabel(item.item_condition)}</span>
            <span>🔄 期望: ${item.desired_exchange || '不限'}</span>
        `;
    }

    const photoSrc = item.photo ? `/static/${item.photo}` : null;

    return `
        <div class="page-container">
            <div class="detail-layout">
                <!-- 主体内容 -->
                <div class="detail-main">
                    <div class="detail-image">
                        ${photoSrc
                            ? `<img src="${photoSrc}" alt="${item.title}">`
                            : `<div class="no-image">${item.category_icon || '📦'}</div>`
                        }
                    </div>

                    <div class="detail-info">
                        <div class="flex items-center gap-sm mb-sm">
                            <span class="tag tag-primary">${itemTypeLabel(itemType)}</span>
                            <span class="tag">${item.category_icon} ${item.category_name}</span>
                            ${statusHtml}
                        </div>

                        <h2>${item.title}</h2>

                        <div class="detail-meta mt">
                            ${metaHtml}
                            <span>📅 发布于 ${timeAgo(item.created_at)}</span>
                        </div>

                        ${item.description ? `
                            <h3 class="mt-md mb-sm">📝 详细描述</h3>
                            <div class="detail-description">${item.description}</div>
                        ` : ''}
                    </div>
                </div>

                <!-- 侧边栏 -->
                <div class="detail-sidebar">
                    <!-- 发布者信息 -->
                    <div class="card">
                        <div style="padding:var(--spacing)">
                            <h3 style="font-size:0.9rem;margin-bottom:12px">👤 发布者</h3>
                            <div class="poster-info">
                                <div class="poster-avatar">${getInitial(item.username)}</div>
                                <div>
                                    <div class="poster-name">${item.username || '匿名'}</div>
                                    <div class="poster-meta">${item.student_id ? '学号: ' + item.student_id : '校园用户'}</div>
                                </div>
                            </div>
                            ${item.contact_info ? `
                                <div class="text-sm text-muted mt-sm">
                                    📞 联系方式: ${item.contact_info}
                                </div>
                            ` : ''}
                        </div>
                    </div>

                    <!-- 操作按钮 -->
                    ${isLoggedIn() && !isOwner ? `
                        <div class="card" style="padding:var(--spacing)">
                            <button class="btn btn-primary btn-block" id="contactBtn">
                                💬 联系${itemType === 'found' ? '拾取者' : itemType === 'lost' ? '失主' : '发布者'}
                            </button>
                        </div>
                    ` : ''}

                    ${isOwner ? `
                        <div class="card" style="padding:var(--spacing)">
                            <p class="text-sm text-muted mb-sm">这是您发布的信息</p>
                            <div class="flex gap-sm">
                                ${itemType === 'found' && item.status === 'pending' ? `
                                    <button class="btn btn-success btn-sm flex-1" id="markClaimedBtn">标记为已认领</button>
                                ` : ''}
                                ${itemType === 'lost' && item.status === 'open' ? `
                                    <button class="btn btn-success btn-sm flex-1" id="markFoundBtn">标记为已找到</button>
                                ` : ''}
                                ${itemType === 'exchange' && item.status === 'available' ? `
                                    <button class="btn btn-success btn-sm flex-1" id="markExchangedBtn">标记为已交换</button>
                                ` : ''}
                            </div>
                        </div>
                    ` : ''}
                </div>
            </div>
        </div>
    `;
}

// 全局事件处理
document.addEventListener('click', async (e) => {
    const hash = window.location.hash;
    const match = hash.match(/^#\/item\/(found|lost|exchange)\/(\d+)/);
    if (!match) return;

    const itemType = match[1];
    const itemId = parseInt(match[2]);

    // 联系按钮
    if (e.target.id === 'contactBtn') {
        try {
            const data = await api.get(`/api/items/${itemType}/${itemId}`);
            const item = data.item;
            navigateTo(`/messages?user_id=${item.user_id}&item_id=${itemId}&item_type=${itemType}`);
        } catch (err) {
            showToast('操作失败: ' + err.message, 'error');
        }
    }

    // 状态变更按钮
    const statusUpdates = {
        markClaimedBtn: { type: 'found', status: 'claimed', apiPath: 'found' },
        markFoundBtn: { type: 'lost', status: 'found', apiPath: 'lost' },
        markExchangedBtn: { type: 'exchange', status: 'exchanged', apiPath: 'exchange' },
    };

    for (const [btnId, config] of Object.entries(statusUpdates)) {
        if (e.target.id === btnId) {
            try {
                await api.put(`/api/items/${config.apiPath}/${itemId}`, { status: config.status });
                showToast('状态更新成功', 'success');
                // 刷新页面
                window.location.hash = `#/item/${itemType}/${itemId}`;
                window.location.reload();
            } catch (err) {
                showToast('操作失败: ' + err.message, 'error');
            }
        }
    }
});
