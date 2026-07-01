/**
 * 个人中心页面
 */

import api from '../api.js';
import { isLoggedIn, getCurrentUser, navigateTo } from '../app.js';
import { formatDate, showToast, getInitial } from '../utils.js';
import { renderItemCard } from '../components/item-card.js';

export default async function renderProfilePage() {
    if (!isLoggedIn()) {
        navigateTo('/login');
        return '<div class="page-container text-center"><p>正在跳转...</p></div>';
    }

    const user = getCurrentUser();

    // 获取用户各类型物品
    let foundItems = { items: [] };
    let lostItems = { items: [] };
    let exchangeItems = { items: [] };

    try {
        const [found, lost, exchange] = await Promise.all([
            api.get('/api/items/found', { user_id: user.id, per_page: 50 }),
            api.get('/api/items/lost', { user_id: user.id, per_page: 50 }),
            api.get('/api/items/exchange', { user_id: user.id, per_page: 50 }),
        ]);
        foundItems = found;
        lostItems = lost;
        exchangeItems = exchange;
    } catch (e) {
        // 忽略
    }

    setTimeout(() => {
        bindProfileTabs();
    }, 0);

    return `
        <div class="page-container">
            <!-- 用户信息卡片 -->
            <div class="card mb-md">
                <div class="card-body">
                    <div style="display:flex;align-items:center;gap:16px">
                        <div style="width:64px;height:64px;border-radius:50%;background:var(--primary-bg);
                                    color:var(--primary);display:flex;align-items:center;justify-content:center;
                                    font-size:1.5rem;font-weight:700">
                            ${getInitial(user.username)}
                        </div>
                        <div>
                            <h2 style="margin-bottom:4px">${user.username}
                                ${user.role === 'admin' ? '<span class="tag tag-warning" style="margin-left:8px">管理员</span>' : ''}
                            </h2>
                            <p class="text-muted">📧 ${user.email || '未设置'}</p>
                            ${user.phone ? `<p class="text-muted">📞 ${user.phone}</p>` : ''}
                            ${user.student_id ? `<p class="text-muted">🎓 学号: ${user.student_id}</p>` : ''}
                            <p class="text-muted text-sm mt-sm">🕐 注册于 ${formatDate(user.created_at)}</p>
                        </div>
                    </div>
                </div>
            </div>

            <!-- 统计 -->
            <div class="grid grid-3 mb-md">
                <div class="stat-card">
                    <div class="stat-value">${foundItems.total || 0}</div>
                    <div class="stat-label">拾物信息</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">${lostItems.total || 0}</div>
                    <div class="stat-label">寻物信息</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">${exchangeItems.total || 0}</div>
                    <div class="stat-label">交换信息</div>
                </div>
            </div>

            <!-- 物品选项卡 -->
            <div class="tabs" id="profileTabs">
                <button class="tab active" data-tab="found">📦 我的拾物 (${foundItems.total || 0})</button>
                <button class="tab" data-tab="lost">🔍 我的寻物 (${lostItems.total || 0})</button>
                <button class="tab" data-tab="exchange">🔄 我的交换 (${exchangeItems.total || 0})</button>
            </div>

            <!-- 物品列表 -->
            <div id="profileItemsFound" class="profile-items-tab">
                ${foundItems.items.length > 0
                    ? `<div class="items-grid">${foundItems.items.map(item => renderItemCard(item, 'found')).join('')}</div>`
                    : '<div class="empty-state"><p>暂无拾物信息</p></div>'
                }
            </div>
            <div id="profileItemsLost" class="profile-items-tab" style="display:none">
                ${lostItems.items.length > 0
                    ? `<div class="items-grid">${lostItems.items.map(item => renderItemCard(item, 'lost')).join('')}</div>`
                    : '<div class="empty-state"><p>暂无寻物信息</p></div>'
                }
            </div>
            <div id="profileItemsExchange" class="profile-items-tab" style="display:none">
                ${exchangeItems.items.length > 0
                    ? `<div class="items-grid">${exchangeItems.items.map(item => renderItemCard(item, 'exchange')).join('')}</div>`
                    : '<div class="empty-state"><p>暂无交换信息</p></div>'
                }
            </div>
        </div>
    `;
}

function bindProfileTabs() {
    const tabs = document.querySelectorAll('#profileTabs .tab');
    tabs.forEach(tab => {
        tab.addEventListener('click', () => {
            tabs.forEach(t => t.classList.remove('active'));
            tab.classList.add('active');

            const tabName = tab.dataset.tab;
            document.querySelectorAll('.profile-items-tab').forEach(el => el.style.display = 'none');

            const targetMap = {
                found: 'profileItemsFound',
                lost: 'profileItemsLost',
                exchange: 'profileItemsExchange',
            };

            const target = document.getElementById(targetMap[tabName]);
            if (target) target.style.display = 'block';
        });
    });
}
