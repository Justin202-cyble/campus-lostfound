/**
 * 搜索栏组件
 */

import { debounce } from '../utils.js';

/**
 * 渲染搜索栏
 * @param {Object} options
 * @param {Array} options.categories - 分类列表 [{id, name, icon}]
 * @param {String} options.type - 物品类型 found/lost/exchange
 * @param {Object} options.filters - 当前筛选值 {q, category_id, status/condition}
 * @param {Function} options.onSearch - 搜索回调 (filters) => void
 * @returns {String} HTML字符串
 */
export function renderSearchBar(options = {}) {
    const { categories = [], type = '', filters = {}, onSearch } = options;

    const currentQ = filters.q || '';
    const currentCategory = filters.category_id || '';
    const currentStatus = filters.status || '';
    const currentCondition = filters.condition || '';

    const statusOptions = type === 'found'
        ? `
            <option value="">全部状态</option>
            <option value="pending" ${currentStatus === 'pending' ? 'selected' : ''}>待认领</option>
            <option value="claimed" ${currentStatus === 'claimed' ? 'selected' : ''}>已认领</option>
            <option value="resolved" ${currentStatus === 'resolved' ? 'selected' : ''}>已解决</option>
        `
        : type === 'lost'
        ? `
            <option value="">全部状态</option>
            <option value="open" ${currentStatus === 'open' ? 'selected' : ''}>寻找中</option>
            <option value="found" ${currentStatus === 'found' ? 'selected' : ''}>已找到</option>
            <option value="resolved" ${currentStatus === 'resolved' ? 'selected' : ''}>已解决</option>
        `
        : `
            <option value="">全部状态</option>
            <option value="brand_new" ${currentCondition === 'brand_new' ? 'selected' : ''}>全新</option>
            <option value="good" ${currentCondition === 'good' ? 'selected' : ''}>较新</option>
            <option value="used" ${currentCondition === 'used' ? 'selected' : ''}>使用过</option>
            <option value="worn" ${currentCondition === 'worn' ? 'selected' : ''}>有磨损</option>
        `;

    const html = `
        <div class="search-bar" data-component="search-bar">
            <div class="search-input-wrapper">
                <span class="search-icon">🔍</span>
                <input type="text" id="searchInput" placeholder="搜索物品名称或描述..."
                       value="${escapeAttr(currentQ)}">
            </div>
            <select id="searchCategory">
                <option value="">全部分类</option>
                ${categories.map(c => `
                    <option value="${c.id}" ${String(currentCategory) === String(c.id) ? 'selected' : ''}>
                        ${c.icon} ${c.name}
                    </option>
                `).join('')}
            </select>
            <select id="searchStatus">
                ${statusOptions}
            </select>
            <button class="btn btn-primary" id="searchBtn">搜索</button>
            <button class="btn btn-ghost" id="searchClear">重置</button>
        </div>
    `;

    // 绑定事件
    setTimeout(() => {
        const searchInput = document.getElementById('searchInput');
        const searchCategory = document.getElementById('searchCategory');
        const searchStatus = document.getElementById('searchStatus');
        const searchBtn = document.getElementById('searchBtn');
        const searchClear = document.getElementById('searchClear');

        const doSearch = () => {
            const newFilters = {
                q: searchInput?.value || '',
                category_id: searchCategory?.value || '',
            };
            if (type === 'exchange') {
                newFilters.condition = searchStatus?.value || '';
            } else {
                newFilters.status = searchStatus?.value || '';
            }
            if (onSearch) onSearch(newFilters);
        };

        const debouncedSearch = debounce(doSearch, 500);

        if (searchInput) searchInput.addEventListener('input', debouncedSearch);
        if (searchCategory) searchCategory.addEventListener('change', doSearch);
        if (searchStatus) searchStatus.addEventListener('change', doSearch);
        if (searchBtn) searchBtn.addEventListener('click', doSearch);
        if (searchClear) {
            searchClear.addEventListener('click', () => {
                if (searchInput) searchInput.value = '';
                if (searchCategory) searchCategory.value = '';
                if (searchStatus) searchStatus.value = '';
                if (onSearch) onSearch({});
            });
        }

        // 回车搜索
        if (searchInput) {
            searchInput.addEventListener('keydown', (e) => {
                if (e.key === 'Enter') doSearch();
            });
        }
    }, 0);

    return html;
}

function escapeAttr(str) {
    return String(str).replace(/&/g, '&amp;').replace(/"/g, '&quot;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
}
