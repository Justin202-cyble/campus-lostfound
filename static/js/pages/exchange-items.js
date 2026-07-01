/**
 * 交换物品列表页
 */

import api from '../api.js';
import { getQueryParams, showToast } from '../utils.js';
import { renderItemGrid } from '../components/item-card.js';
import { renderSearchBar } from '../components/search-bar.js';
import { renderPagination } from '../components/pagination.js';

export default async function renderExchangeItemsPage() {
    const params = getQueryParams();
    let categories = [];
    let itemsData = { items: [], total: 0, page: 1, pages: 1 };

    try {
        const [catData, itemData] = await Promise.all([
            api.get('/api/categories'),
            api.get('/api/items/exchange', {
                page: params.page || 1,
                category_id: params.category_id,
                condition: params.condition,
                q: params.q,
            }),
        ]);
        categories = catData.categories || [];
        itemsData = itemData;
    } catch (e) {
        showToast('加载失败: ' + e.message, 'error');
    }

    const searchHtml = renderSearchBar({
        categories,
        type: 'exchange',
        filters: params,
        onSearch: (filters) => {
            const query = new URLSearchParams(
                Object.entries(filters).filter(([_, v]) => v !== '' && v !== null && v !== undefined)
            ).toString();
            window.location.hash = `#/exchange${query ? '?' + query : ''}`;
        },
    });

    const paginationHtml = renderPagination(itemsData.page, itemsData.pages, (page) => {
        const filters = { ...params, page };
        const query = new URLSearchParams(
            Object.entries(filters).filter(([_, v]) => v !== '' && v !== null && v !== undefined)
        ).toString();
        window.location.hash = `#/exchange${query ? '?' + query : ''}`;
    });

    return `
        <div class="page-container">
            <div class="flex items-center justify-between mb">
                <h1>🔄 物品交换</h1>
                <button class="btn btn-primary btn-sm" onclick="window.location.hash='#/post'">
                    ✏️ 发布交换物品
                </button>
            </div>
            <p class="text-muted mb">共 ${itemsData.total} 条交换信息</p>
            ${searchHtml}
            ${renderItemGrid(itemsData.items, 'exchange')}
            ${paginationHtml}
        </div>
    `;
}
