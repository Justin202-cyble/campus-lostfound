/**
 * 拾物列表页
 */

import api from '../api.js';
import { getQueryParams, showToast } from '../utils.js';
import { renderItemGrid } from '../components/item-card.js';
import { renderSearchBar } from '../components/search-bar.js';
import { renderPagination } from '../components/pagination.js';

export default async function renderFoundItemsPage() {
    const params = getQueryParams();
    let categories = [];
    let itemsData = { items: [], total: 0, page: 1, pages: 1 };

    try {
        const [catData, itemData] = await Promise.all([
            api.get('/api/categories'),
            api.get('/api/items/found', {
                page: params.page || 1,
                category_id: params.category_id,
                status: params.status,
                q: params.q,
            }),
        ]);
        categories = catData.categories || [];
        itemsData = itemData;
    } catch (e) {
        showToast('加载失败: ' + e.message, 'error');
    }

    // 渲染搜索栏
    const searchHtml = renderSearchBar({
        categories,
        type: 'found',
        filters: params,
        onSearch: (filters) => {
            const query = new URLSearchParams(
                Object.entries(filters).filter(([_, v]) => v !== '' && v !== null && v !== undefined)
            ).toString();
            window.location.hash = `#/found${query ? '?' + query : ''}`;
        },
    });

    // 渲染分页
    const paginationHtml = renderPagination(itemsData.page, itemsData.pages, (page) => {
        const filters = { ...params, page };
        const query = new URLSearchParams(
            Object.entries(filters).filter(([_, v]) => v !== '' && v !== null && v !== undefined)
        ).toString();
        window.location.hash = `#/found${query ? '?' + query : ''}`;
    });

    return `
        <div class="page-container">
            <div class="flex items-center justify-between mb">
                <h1>📦 拾物招领</h1>
                <button class="btn btn-primary btn-sm" onclick="window.location.hash='#/post'">
                    ✏️ 发布拾物信息
                </button>
            </div>
            <p class="text-muted mb">共 ${itemsData.total} 条拾物信息</p>
            ${searchHtml}
            ${renderItemGrid(itemsData.items, 'found')}
            ${paginationHtml}
        </div>
    `;
}
