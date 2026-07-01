/**
 * 模态框组件
 */

/**
 * 显示模态框
 * @param {Object} config
 * @param {String} config.title - 标题
 * @param {String} config.content - 内容HTML
 * @param {Boolean} config.showConfirm - 是否显示确认按钮
 * @param {Boolean} config.showCancel - 是否显示取消按钮
 * @param {String} config.confirmText - 确认按钮文字
 * @param {String} config.cancelText - 取消按钮文字
 * @param {Function} config.onConfirm - 确认回调
 * @param {Function} config.onCancel - 取消回调
 */
export function showModal(config = {}) {
    const {
        title = '提示',
        content = '',
        showConfirm = true,
        showCancel = true,
        confirmText = '确认',
        cancelText = '取消',
        onConfirm,
        onCancel,
    } = config;

    const container = document.getElementById('modal-container');
    if (!container) return;

    const modal = document.createElement('div');
    modal.className = 'modal-overlay';
    modal.id = 'currentModal';

    modal.innerHTML = `
        <div class="modal-dialog">
            <div class="modal-header">
                <h3 class="modal-title">${title}</h3>
                <button class="modal-close" id="modalClose">×</button>
            </div>
            <div class="modal-body">${content}</div>
            ${showConfirm || showCancel ? `
                <div class="modal-footer">
                    ${showCancel ? `<button class="btn btn-outline" id="modalCancel">${cancelText}</button>` : ''}
                    ${showConfirm ? `<button class="btn btn-primary" id="modalConfirm">${confirmText}</button>` : ''}
                </div>
            ` : ''}
        </div>
    `;

    container.appendChild(modal);

    const close = () => {
        modal.remove();
        if (onCancel) onCancel();
    };

    const confirm = () => {
        modal.remove();
        if (onConfirm) onConfirm();
    };

    // 关闭按钮
    modal.querySelector('#modalClose')?.addEventListener('click', close);

    // 点击背景关闭
    modal.addEventListener('click', (e) => {
        if (e.target === modal) close();
    });

    // ESC 关闭
    const escHandler = (e) => {
        if (e.key === 'Escape') { close(); document.removeEventListener('keydown', escHandler); }
    };
    document.addEventListener('keydown', escHandler);

    // 确认/取消按钮
    modal.querySelector('#modalConfirm')?.addEventListener('click', confirm);
    modal.querySelector('#modalCancel')?.addEventListener('click', close);
}

/**
 * 关闭当前模态框
 */
export function closeModal() {
    const modal = document.getElementById('currentModal');
    if (modal) modal.remove();
}
