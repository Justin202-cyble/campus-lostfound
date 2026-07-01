/**
 * 留言/消息页面
 */

import api from '../api.js';
import { isLoggedIn, getCurrentUser, navigateTo } from '../app.js';
import { timeAgo, showToast, getInitial, getQueryParams } from '../utils.js';
import { updateUnreadBadge } from '../components/navbar.js';

export default async function renderMessagesPage(params) {
    if (!isLoggedIn()) {
        navigateTo('/login');
        return '<div class="page-container text-center"><p>正在跳转...</p></div>';
    }

    // 预加载对话列表
    let conversations = [];
    try {
        const data = await api.get('/api/messages/conversations');
        conversations = data.conversations || [];
    } catch (e) {
        showToast('加载失败: ' + e.message, 'error');
    }

    const queryParams = getQueryParams();
    const activeUserId = queryParams.user_id;
    const activeItemId = queryParams.item_id;
    const activeItemType = queryParams.item_type;

    setTimeout(() => {
        bindMessageEvents(conversations, activeUserId, activeItemId, activeItemType);
    }, 0);

    return `
        <div class="page-container" style="padding:0">
            <div class="chat-layout">
                <!-- 对话列表侧边栏 -->
                <div class="chat-sidebar" id="chatSidebar">
                    <div class="chat-sidebar-header">
                        💬 我的对话
                    </div>
                    <div id="conversationList">
                        ${conversations.length === 0 ? `
                            <div class="empty-state" style="padding:40px 16px">
                                <div class="icon">💬</div>
                                <p>暂无对话</p>
                                <p style="font-size:0.8rem">点击物品详情中的"联系"按钮开始对话</p>
                            </div>
                        ` : conversations.map(conv => `
                            <div class="conversation-item ${String(conv.other_user_id) === String(activeUserId) ? 'active' : ''}"
                                 data-user-id="${conv.other_user_id}"
                                 data-item-id="${conv.item_id}"
                                 data-item-type="${conv.item_type}">
                                <div class="conv-avatar">${getInitial(conv.username)}</div>
                                <div class="conv-info">
                                    <div class="conv-name">${conv.username || '用户'}</div>
                                    <div class="conv-preview">${conv.last_message || ''}</div>
                                </div>
                                <div class="conv-meta">
                                    <div class="conv-time">${timeAgo(conv.last_time)}</div>
                                    ${conv.unread_count > 0 ? `<div class="conv-badge">${conv.unread_count > 99 ? '99+' : conv.unread_count}</div>` : ''}
                                </div>
                            </div>
                        `).join('')}
                    </div>
                </div>

                <!-- 聊天主区域 -->
                <div class="chat-main" id="chatMain">
                    ${activeUserId && activeItemId ? `
                        <div class="chat-header" id="chatHeader">
                            加载中...
                        </div>
                        <div class="chat-messages" id="chatMessages">
                            <div class="loading-spinner"><div class="spinner"></div></div>
                        </div>
                        <div class="chat-input-area" id="chatInput">
                            <textarea id="messageInput" placeholder="输入留言..." rows="1"></textarea>
                            <button class="btn btn-primary" id="sendBtn">发送</button>
                        </div>
                    ` : `
                        <div class="empty-state" style="height:100%;display:flex;align-items:center;justify-content:center">
                            <div>
                                <div class="icon">👈</div>
                                <p>选择左侧对话开始聊天</p>
                            </div>
                        </div>
                    `}
                </div>
            </div>
        </div>
    `;
}

function bindMessageEvents(conversations, activeUserId, activeItemId, activeItemType) {
    let currentThread = { userId: activeUserId, itemId: activeItemId, itemType: activeItemType };
    let pollTimer = null;

    // 加载对话
    async function loadThread(userId, itemId, itemType) {
        const header = document.getElementById('chatHeader');
        const messagesDiv = document.getElementById('chatMessages');
        const inputArea = document.getElementById('chatInput');

        if (!userId || !itemId || !itemType) return;

        currentThread = { userId: parseInt(userId), itemId: parseInt(itemId), itemType };

        if (header) header.textContent = '加载中...';
        if (messagesDiv) messagesDiv.innerHTML = '<div class="loading-spinner"><div class="spinner"></div></div>';

        try {
            const [threadData, itemData] = await Promise.all([
                api.get('/api/messages', { user_id: userId, item_id: itemId, item_type: itemType }),
                api.get(`/api/items/${itemType}/${itemId}`).catch(() => null),
            ]);

            const messages = threadData.messages || [];
            const item = itemData?.item;

            // 更新聊天头部
            if (header && item) {
                header.innerHTML = `
                    关于：<a href="#/item/${itemType}/${itemId}" style="color:var(--primary)">${item.title || '物品'}</a>
                    <span style="font-size:0.8rem;color:var(--text-muted)">(${itemType === 'found' ? '拾物' : itemType === 'lost' ? '寻物' : '交换'})</span>
                `;
            }

            // 更新对话列表高亮
            document.querySelectorAll('.conversation-item').forEach(el => {
                el.classList.remove('active');
                if (String(el.dataset.userId) === String(userId) &&
                    String(el.dataset.itemId) === String(itemId)) {
                    el.classList.add('active');
                }
            });

            // 显示消息
            const currentUser = getCurrentUser();
            if (messagesDiv) {
                if (messages.length === 0) {
                    messagesDiv.innerHTML = '<div class="empty-state"><p>暂无消息，发送第一条留言吧</p></div>';
                } else {
                    messagesDiv.innerHTML = messages.map(msg => {
                        const isSent = msg.sender_id === currentUser?.id;
                        return `
                            <div class="message-bubble ${isSent ? 'message-sent' : 'message-received'}">
                                <div>${msg.content}</div>
                                <div class="message-time">${timeAgo(msg.created_at)}</div>
                            </div>
                        `;
                    }).join('');
                    messagesDiv.scrollTop = messagesDiv.scrollHeight;
                }
            }

            // 显示输入区域
            if (inputArea) inputArea.style.display = 'flex';

            await updateUnreadBadge();
        } catch (e) {
            if (messagesDiv) messagesDiv.innerHTML = `<div class="empty-state"><p>加载失败: ${e.message}</p></div>`;
        }
    }

    // 发送消息
    async function sendMessage() {
        const input = document.getElementById('messageInput');
        const content = input?.value.trim();
        if (!content || !currentThread.userId || !currentThread.itemId) return;

        try {
            await api.post('/api/messages', {
                receiver_id: currentThread.userId,
                item_id: currentThread.itemId,
                item_type: currentThread.itemType,
                content,
            });
            if (input) input.value = '';
            await loadThread(currentThread.userId, currentThread.itemId, currentThread.itemType);
        } catch (e) {
            showToast('发送失败: ' + e.message, 'error');
        }
    }

    // 事件绑定
    document.getElementById('sendBtn')?.addEventListener('click', sendMessage);
    document.getElementById('messageInput')?.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
        }
    });

    // 对话列表点击
    document.getElementById('conversationList')?.addEventListener('click', (e) => {
        const item = e.target.closest('.conversation-item');
        if (!item) return;
        const userId = item.dataset.userId;
        const itemId = item.dataset.itemId;
        const itemType = item.dataset.itemType;
        if (userId && itemId) {
            window.location.hash = `#/messages?user_id=${userId}&item_id=${itemId}&item_type=${itemType}`;
        }
    });

    // 初始加载
    if (activeUserId && activeItemId) {
        loadThread(activeUserId, activeItemId, activeItemType);

        // 轮询新消息
        pollTimer = setInterval(() => {
            if (currentThread.userId && currentThread.itemId) {
                loadThread(currentThread.userId, currentThread.itemId, currentThread.itemType);
            }
        }, 10000);
    }

    // 清理定时器
    window.addEventListener('hashchange', () => {
        if (pollTimer) clearInterval(pollTimer);
    });
}
