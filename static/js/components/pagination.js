/**
 * 分页组件
 */

/**
 * 渲染分页导航
 * @param {Number} current - 当前页码
 * @param {Number} total - 总页数
 * @param {Function} onChange - 页码变化回调 (page) => void
 * @returns {String} HTML字符串
 */
export function renderPagination(current, total, onChange) {
    if (total <= 1) return '';

    let pages = [];
    const maxVisible = 7;

    if (total <= maxVisible) {
        pages = Array.from({ length: total }, (_, i) => i + 1);
    } else {
        pages.push(1);
        if (current > 3) pages.push('...');

        const start = Math.max(2, current - 1);
        const end = Math.min(total - 1, current + 1);

        for (let i = start; i <= end; i++) {
            pages.push(i);
        }

        if (current < total - 2) pages.push('...');
        pages.push(total);
    }

    const html = `
        <div class="pagination" data-component="pagination">
            <button data-page="${current - 1}" ${current <= 1 ? 'disabled' : ''}>‹ 上一页</button>
            ${pages.map(p => {
                if (p === '...') return '<span style="padding:0 4px">...</span>';
                return `<button data-page="${p}" ${p === current ? 'class="active"' : ''}>${p}</button>`;
            }).join('')}
            <button data-page="${current + 1}" ${current >= total ? 'disabled' : ''}>下一页 ›</button>
        </div>
    `;

    // 使用 setTimeout 确保DOM渲染后绑定事件
    setTimeout(() => {
        const container = document.querySelector('[data-component="pagination"]');
        if (container) {
            container.querySelectorAll('button[data-page]').forEach(btn => {
                btn.addEventListener('click', () => {
                    const page = parseInt(btn.getAttribute('data-page'));
                    if (page >= 1 && page <= total && page !== current) {
                        onChange(page);
                    }
                });
            });
        }
    }, 0);

    return html;
}
