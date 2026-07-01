/**
 * 首页
 */

import api from '../api.js';
import { timeAgo, getInitial } from '../utils.js';
import { renderItemCard } from '../components/item-card.js';

export default async function renderHomePage() {
    let stats = { total_found: 0, total_lost: 0, total_exchange: 0, total_resolved: 0 };
    let recentItems = { found: [], lost: [], exchange: [] };

    try {
        const [statsData, recentData] = await Promise.all([
            api.get('/api/items/home/stats'),
            api.get('/api/items/home/recent'),
        ]);
        stats = statsData;
        recentItems = recentData;
    } catch (e) {
        console.error('首页数据加载失败:', e);
    }

    return `
        <div class="page-container" style="padding-top: 0;">
            <!-- Hero -->
            <div class="hero">
                <h1>🏫 智慧校园失物招领与物品交换平台</h1>
                <p>捡到物品？丢失物品？闲置交换？这里都能帮你解决</p>
                <div class="hero-search">
                    <input type="text" id="heroSearchInput" placeholder="搜索失物、寻物或交换物品...">
                    <button id="heroSearchBtn">🔍 搜索</button>
                </div>
            </div>

            <div style="padding: 0 var(--spacing);">

                <!-- 统计数据 -->
                <div class="grid grid-4" style="margin-top: -20px; position: relative; z-index: 1;">
                    <div class="stat-card">
                        <div class="stat-icon">📦</div>
                        <div class="stat-value">${stats.total_found}</div>
                        <div class="stat-label">拾物信息</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-icon">🔍</div>
                        <div class="stat-value">${stats.total_lost}</div>
                        <div class="stat-label">寻物信息</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-icon">🔄</div>
                        <div class="stat-value">${stats.total_exchange}</div>
                        <div class="stat-label">交换物品</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-icon">✅</div>
                        <div class="stat-value">${stats.total_resolved}</div>
                        <div class="stat-label">已解决</div>
                    </div>
                </div>

                <!-- 最近拾物 -->
                <h2 class="mt-lg mb">📦 最新拾物招领</h2>
                ${recentItems.found.length > 0 ? `
                    <div class="items-grid">
                        ${recentItems.found.slice(0, 3).map(item => renderItemCard(item, 'found')).join('')}
                    </div>
                ` : '<div class="empty-state"><p>暂无拾物信息</p></div>'}

                <!-- 最近寻物 -->
                <h2 class="mt-lg mb">🔍 最新寻物启事</h2>
                ${recentItems.lost.length > 0 ? `
                    <div class="items-grid">
                        ${recentItems.lost.slice(0, 3).map(item => renderItemCard(item, 'lost')).join('')}
                    </div>
                ` : '<div class="empty-state"><p>暂无寻物信息</p></div>'}

                <!-- 最近交换 -->
                <h2 class="mt-lg mb">🔄 最新物品交换</h2>
                ${recentItems.exchange.length > 0 ? `
                    <div class="items-grid">
                        ${recentItems.exchange.slice(0, 3).map(item => renderItemCard(item, 'exchange')).join('')}
                    </div>
                ` : '<div class="empty-state"><p>暂无交换信息</p></div>'}

                <!-- 使用步骤 -->
                <h2 class="mt-lg mb text-center">📋 使用指南</h2>
                <div class="steps">
                    <div class="step-card">
                        <div class="step-number">1</div>
                        <h3>注册账号</h3>
                        <p>用校园邮箱注册，成为平台用户</p>
                    </div>
                    <div class="step-card">
                        <div class="step-number">2</div>
                        <h3>发布信息</h3>
                        <p>发布拾物、寻物或交换信息</p>
                    </div>
                    <div class="step-card">
                        <div class="step-number">3</div>
                        <h3>在线沟通</h3>
                        <p>通过留言功能联系对方，完成交接</p>
                    </div>
                </div>

                <!-- 底部CTA -->
                <div class="text-center mt-lg" style="padding: var(--spacing-xl) 0;">
                    <h2>准备好发布信息了吗？</h2>
                    <p class="text-muted mt-sm">捡到东西想让失主找到？丢了东西想快点找回？</p>
                    <button class="btn btn-primary btn-lg mt-md" onclick="window.location.hash='#/post'">
                        ✏️ 立即发布
                    </button>
                </div>
            </div>
        </div>
    `;
}

// 绑定Hero搜索事件
document.addEventListener('click', (e) => {
    if (e.target.id === 'heroSearchBtn') {
        const input = document.getElementById('heroSearchInput');
        if (input && input.value.trim()) {
            window.location.hash = `#/found?q=${encodeURIComponent(input.value.trim())}`;
        }
    }
});

document.addEventListener('keydown', (e) => {
    if (e.key === 'Enter' && document.activeElement?.id === 'heroSearchInput') {
        const input = document.getElementById('heroSearchInput');
        if (input && input.value.trim()) {
            window.location.hash = `#/found?q=${encodeURIComponent(input.value.trim())}`;
        }
    }
});
