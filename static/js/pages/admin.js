/**
 * 管理后台 — 数据可视化看板
 */

import api from '../api.js';
import { isLoggedIn, isAdmin, navigateTo } from '../app.js';
import { formatDate, timeAgo, showToast, getInitial } from '../utils.js';

export default async function renderAdminPage() {
    if (!isLoggedIn()) {
        navigateTo('/login');
        return '<div class="page-container text-center"><p>正在跳转...</p></div>';
    }
    if (!isAdmin()) {
        return '<div class="page-container text-center"><h2>权限不足</h2><p>仅管理员可访问此页面</p></div>';
    }

    // 加载数据
    let overview = {};
    let heatmap = { found_locations: [], lost_locations: [] };
    let timeDist = { hourly: { found: [], lost: [] }, weekly: { found: [], lost: [] } };
    let catDist = { categories: [] };
    let matchStats = { recent_matches: [] };
    let users = { users: [], total: 0 };

    try {
        const results = await Promise.all([
            api.get('/api/admin/stats/overview'),
            api.get('/api/admin/stats/heatmap'),
            api.get('/api/admin/stats/time-distribution'),
            api.get('/api/admin/stats/category-distribution'),
            api.get('/api/admin/stats/match-statistics'),
            api.get('/api/admin/users', { page: 1, per_page: 20 }),
        ]);
        overview = results[0];
        heatmap = results[1];
        timeDist = results[2];
        catDist = results[3];
        matchStats = results[4];
        users = results[5];
    } catch (e) {
        showToast('数据加载失败: ' + e.message, 'error');
    }

    // 渲染页面
    setTimeout(() => {
        initCharts(heatmap, timeDist, catDist, matchStats);
    }, 300);

    return `
        <div class="page-container">
            <div class="flex items-center justify-between mb-md">
                <h1>📊 管理后台</h1>
                <span class="text-muted text-sm">数据可视化看板</span>
            </div>

            <!-- 概览卡片 -->
            <div class="admin-cards">
                <div class="admin-card">
                    <div class="admin-card-icon" style="background:var(--primary-bg);color:var(--primary)">
                        👥
                    </div>
                    <div>
                        <div style="font-size:1.5rem;font-weight:700">${overview.total_users || 0}</div>
                        <div style="font-size:0.8rem;color:var(--text-secondary)">注册用户</div>
                    </div>
                </div>
                <div class="admin-card">
                    <div class="admin-card-icon" style="background:var(--success-bg);color:var(--success)">
                        📦
                    </div>
                    <div>
                        <div style="font-size:1.5rem;font-weight:700">${overview.total_items || 0}</div>
                        <div style="font-size:0.8rem;color:var(--text-secondary)">物品总数</div>
                    </div>
                </div>
                <div class="admin-card">
                    <div class="admin-card-icon" style="background:var(--info-bg);color:var(--info)">
                        ✅
                    </div>
                    <div>
                        <div style="font-size:1.5rem;font-weight:700">${overview.resolve_rate || 0}%</div>
                        <div style="font-size:0.8rem;color:var(--text-secondary)">解决率</div>
                    </div>
                </div>
                <div class="admin-card">
                    <div class="admin-card-icon" style="background:var(--warning-bg);color:var(--warning)">
                        🔗
                    </div>
                    <div>
                        <div style="font-size:1.5rem;font-weight:700">${overview.active_matches || 0}</div>
                        <div style="font-size:0.8rem;color:var(--text-secondary)">活跃匹配</div>
                    </div>
                </div>
            </div>

            <!-- 图表行1: 失物区域分布 + 时段分布 -->
            <div class="admin-chart-row">
                <div class="admin-chart">
                    <h3>📍 失物高发区域分布</h3>
                    <div id="chartHeatmap" style="height:350px"></div>
                </div>
                <div class="admin-chart">
                    <h3>🕐 时段分布统计</h3>
                    <div id="chartTimeDist" style="height:350px"></div>
                </div>
            </div>

            <!-- 图表行2: 分类分布 + 匹配统计 -->
            <div class="admin-chart-row">
                <div class="admin-chart">
                    <h3>📊 物品分类分布</h3>
                    <div id="chartCategory" style="height:350px"></div>
                </div>
                <div class="admin-chart">
                    <h3>🔗 匹配分数分布</h3>
                    <div id="chartMatchScore" style="height:350px"></div>
                </div>
            </div>

            <!-- 最近匹配记录 -->
            <div class="admin-chart admin-chart-full mb-md">
                <h3>📋 最近匹配记录</h3>
                <div style="overflow-x:auto">
                    <table class="data-table">
                        <thead>
                            <tr>
                                <th>丢失物品</th>
                                <th>拾取物品</th>
                                <th>相似度</th>
                                <th>状态</th>
                                <th>时间</th>
                            </tr>
                        </thead>
                        <tbody>
                            ${matchStats.recent_matches && matchStats.recent_matches.length > 0
                                ? matchStats.recent_matches.slice(0, 10).map(m => `
                                    <tr>
                                        <td>${m.lost_title || `寻物#${m.lost_item_id}`}</td>
                                        <td>${m.found_title || `拾物#${m.found_item_id}`}</td>
                                        <td>
                                            <span class="match-score ${m.similarity_score >= 0.55 ? 'match-high' : 'match-medium'}">
                                                ${(m.similarity_score * 100).toFixed(0)}%
                                            </span>
                                        </td>
                                        <td><span class="tag ${m.status === 'notified' ? 'tag-success' : m.status === 'resolved' ? 'tag-info' : 'tag-warning'}">${m.status === 'notified' ? '已通知' : m.status === 'resolved' ? '已解决' : '待处理'}</span></td>
                                        <td>${timeAgo(m.created_at)}</td>
                                    </tr>
                                `).join('')
                                : '<tr><td colspan="5" class="text-center text-muted">暂无匹配记录</td></tr>'
                            }
                        </tbody>
                    </table>
                </div>
            </div>

            <!-- 用户管理 -->
            <div class="admin-chart admin-chart-full">
                <h3>👥 用户管理</h3>
                <div style="overflow-x:auto">
                    <table class="data-table">
                        <thead>
                            <tr>
                                <th>ID</th>
                                <th>用户名</th>
                                <th>邮箱</th>
                                <th>角色</th>
                                <th>学号</th>
                                <th>注册时间</th>
                                <th>操作</th>
                            </tr>
                        </thead>
                        <tbody>
                            ${users.users && users.users.length > 0
                                ? users.users.map(u => `
                                    <tr>
                                        <td>${u.id}</td>
                                        <td><strong>${u.username}</strong></td>
                                        <td>${u.email}</td>
                                        <td><span class="tag ${u.role === 'admin' ? 'tag-warning' : 'tag-info'}">${u.role === 'admin' ? '管理员' : '学生'}</span></td>
                                        <td>${u.student_id || '-'}</td>
                                        <td>${formatDate(u.created_at)}</td>
                                        <td>
                                            ${u.role !== 'admin' ? `
                                                <button class="btn btn-sm btn-outline promote-btn" data-user-id="${u.id}">
                                                    设为管理员
                                                </button>
                                            ` : '<span class="text-sm text-muted">-</span>'}
                                        </td>
                                    </tr>
                                `).join('')
                                : '<tr><td colspan="7" class="text-center text-muted">暂无用户</td></tr>'
                            }
                        </tbody>
                    </table>
                </div>
                ${users.total > 20 ? `<p class="text-muted text-sm mt-sm">共 ${users.total} 个用户，显示前20条</p>` : ''}
            </div>
        </div>
    `;
}

/**
 * 初始化 ECharts 图表
 */
function initCharts(heatmap, timeDist, catDist, matchStats) {
    // Chart 1: 失物高发区域 (柱状图)
    const heatmapDom = document.getElementById('chartHeatmap');
    if (heatmapDom) {
        const chart = echarts.init(heatmapDom);
        const allLocations = [
            ...(heatmap.found_locations || []),
            ...(heatmap.lost_locations || []),
        ];
        // 合并相同地点
        const locationMap = {};
        allLocations.forEach(loc => {
            if (!locationMap[loc.location]) {
                locationMap[loc.location] = { location: loc.location, found: 0, lost: 0 };
            }
        });
        (heatmap.found_locations || []).forEach(l => {
            if (locationMap[l.location]) locationMap[l.location].found = l.count;
        });
        (heatmap.lost_locations || []).forEach(l => {
            if (locationMap[l.location]) locationMap[l.location].lost = l.count;
            else locationMap[l.location] = { location: l.location, found: 0, lost: l.count };
        });

        const locations = Object.values(locationMap)
            .sort((a, b) => (b.found + b.lost) - (a.found + a.lost))
            .slice(0, 10);

        chart.setOption({
            tooltip: { trigger: 'axis' },
            legend: { data: ['拾物', '寻物'], bottom: 0 },
            grid: { left: '3%', right: '4%', bottom: '40px', top: '10px', containLabel: true },
            xAxis: {
                type: 'category',
                data: locations.map(l => l.location),
                axisLabel: { rotate: 30, fontSize: 11 },
            },
            yAxis: { type: 'value', name: '数量' },
            series: [
                {
                    name: '拾物',
                    type: 'bar',
                    data: locations.map(l => l.found),
                    itemStyle: { color: '#10B981' },
                },
                {
                    name: '寻物',
                    type: 'bar',
                    data: locations.map(l => l.lost),
                    itemStyle: { color: '#EF4444' },
                },
            ],
        });

        window.addEventListener('resize', () => chart.resize());
    }

    // Chart 2: 时段分布 (折线图)
    const timeDom = document.getElementById('chartTimeDist');
    if (timeDom) {
        const chart = echarts.init(timeDom);
        const hours = Array.from({ length: 24 }, (_, i) => i);
        const hourlyData = { found: new Array(24).fill(0), lost: new Array(24).fill(0) };

        (timeDist.hourly?.found || []).forEach(h => {
            if (h.hour >= 0 && h.hour < 24) hourlyData.found[h.hour] = h.count;
        });
        (timeDist.hourly?.lost || []).forEach(h => {
            if (h.hour >= 0 && h.hour < 24) hourlyData.lost[h.hour] = h.count;
        });

        chart.setOption({
            tooltip: { trigger: 'axis' },
            legend: { data: ['拾物', '寻物'], bottom: 0 },
            grid: { left: '3%', right: '4%', bottom: '40px', top: '10px', containLabel: true },
            xAxis: {
                type: 'category',
                data: hours.map(h => `${h}:00`),
                boundaryGap: false,
            },
            yAxis: { type: 'value', name: '数量' },
            series: [
                {
                    name: '拾物',
                    type: 'line',
                    data: hourlyData.found,
                    smooth: true,
                    itemStyle: { color: '#10B981' },
                    areaStyle: { opacity: 0.1 },
                },
                {
                    name: '寻物',
                    type: 'line',
                    data: hourlyData.lost,
                    smooth: true,
                    itemStyle: { color: '#EF4444' },
                    areaStyle: { opacity: 0.1 },
                },
            ],
        });

        window.addEventListener('resize', () => chart.resize());
    }

    // Chart 3: 分类分布 (饼图)
    const catDom = document.getElementById('chartCategory');
    if (catDom) {
        const chart = echarts.init(catDom);
        const pieData = (catDist.categories || [])
            .filter(c => c.total > 0)
            .map(c => ({ name: c.category, value: c.total }));

        chart.setOption({
            tooltip: { trigger: 'item', formatter: '{b}: {c} ({d}%)' },
            legend: { orient: 'vertical', right: 10, top: 'center' },
            series: [{
                type: 'pie',
                radius: ['40%', '75%'],
                center: ['40%', '50%'],
                data: pieData,
                emphasis: {
                    itemStyle: { shadowBlur: 10, shadowOffsetX: 0, shadowColor: 'rgba(0,0,0,0.5)' },
                },
                label: { formatter: '{b}\n{d}%' },
            }],
        });

        window.addEventListener('resize', () => chart.resize());
    }

    // Chart 4: 匹配分数分布 (仪表盘 + 柱状图)
    const matchDom = document.getElementById('chartMatchScore');
    if (matchDom) {
        const chart = echarts.init(matchDom);

        const total = matchStats.total_matches || 0;
        const high = matchStats.high_matches || 0;
        const medium = matchStats.medium_matches || 0;

        chart.setOption({
            tooltip: { trigger: 'axis' },
            grid: { left: '3%', right: '4%', bottom: '30px', top: '30px', containLabel: true },
            xAxis: {
                type: 'category',
                data: ['高匹配(≥55%)', '中匹配(40-55%)', '已通知', '已解决'],
            },
            yAxis: { type: 'value', name: '数量' },
            series: [{
                type: 'bar',
                data: [
                    { value: high, itemStyle: { color: '#10B981' } },
                    { value: medium, itemStyle: { color: '#F59E0B' } },
                    { value: matchStats.notified || 0, itemStyle: { color: '#3B82F6' } },
                    { value: matchStats.resolved || 0, itemStyle: { color: '#8B5CF6' } },
                ],
                label: { show: true, position: 'top' },
            }],
        });

        window.addEventListener('resize', () => chart.resize());
    }
}

// 全局事件：用户角色管理
document.addEventListener('click', async (e) => {
    if (e.target.classList.contains('promote-btn')) {
        const userId = e.target.dataset.userId;
        if (!userId) return;
        try {
            await api.put(`/api/admin/users/${userId}`, { role: 'admin' });
            showToast('已将用户设为管理员', 'success');
            setTimeout(() => window.location.reload(), 500);
        } catch (err) {
            showToast('操作失败: ' + err.message, 'error');
        }
    }
});
