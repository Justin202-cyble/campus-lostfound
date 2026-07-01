/**
 * 物品卡片组件
 */

import { timeAgo, truncate, itemTypeLabel, statusLabel, getInitial } from '../utils.js';

/**
 * 渲染单个物品卡片
 * @param {Object} item - 物品数据
 * @param {String} type - 物品类型: found / lost / exchange
 * @returns {String} HTML字符串
 */
export function renderItemCard(item, type) {
    const itemType = type || item.item_type || 'found';
    const detailUrl = `#/item/${itemType}/${item.id}`;
    const photoSrc = item.photo ? `/static/${item.photo}` : null;

    const badgeClass = {
        found: 'badge-found',
        lost: 'badge-lost',
        exchange: 'badge-exchange',
    }[itemType] || 'badge-found';

    const status = item.status || '';
    const statusText = statusLabel(status, itemType);

    // 显示位置字段（根据类型不同）
    let locationText = '';
    if (itemType === 'found' && item.location_found) {
        locationText = `📍 ${item.location_found}`;
    } else if (itemType === 'lost' && item.location_lost) {
        locationText = `📍 ${item.location_lost}`;
    } else if (itemType === 'exchange' && item.item_condition) {
        const condMap = { brand_new: '全新', good: '较新', used: '使用过', worn: '有磨损' };
        locationText = `🏷️ ${condMap[item.item_condition] || item.item_condition}`;
    }

    return `
        <div class="item-card" onclick="window.location.hash='${detailUrl}'" title="${item.title || ''}">
            <div class="item-card-image">
                ${photoSrc
                    ? `<img src="${photoSrc}" alt="${item.title || ''}" loading="lazy">`
                    : `<div class="no-image">${item.category_icon || '📦'}</div>`
                }
                <span class="item-card-badge ${badgeClass}">${itemTypeLabel(itemType)}</span>
                ${status ? `<span class="item-card-badge" style="right:8px;left:auto;background:rgba(0,0,0,0.6)">${statusText}</span>` : ''}
            </div>
            <div class="item-card-body">
                <div class="item-card-title">${item.title || '无标题'}</div>
                ${item.category_name ? `<div class="item-card-meta">${item.category_icon || ''} ${item.category_name}</div>` : ''}
                ${locationText ? `<div class="item-card-meta">${locationText}</div>` : ''}
                <div class="item-card-footer">
                    <span class="username">
                        <span class="item-card-avatar">${getInitial(item.username)}</span>
                        ${item.username || '匿名'}
                    </span>
                    <span>${timeAgo(item.created_at)}</span>
                </div>
            </div>
        </div>
    `;
}

/**
 * 渲染物品卡片网格
 */
export function renderItemGrid(items, type) {
    if (!items || items.length === 0) {
        return `
            <div class="empty-state">
                <div class="icon">📭</div>
                <p>暂无相关物品信息</p>
            </div>
        `;
    }

    return `
        <div class="items-grid">
            ${items.map(item => renderItemCard(item, type)).join('')}
        </div>
    `;
}
