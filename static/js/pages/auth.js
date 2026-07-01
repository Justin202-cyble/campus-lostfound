/**
 * 登录/注册页面
 */

import api from '../api.js';
import { setCurrentUser, navigateTo } from '../app.js';
import { showToast } from '../utils.js';

export default async function renderAuthPage(params) {
    const isLogin = !window.location.hash.includes('register');

    setTimeout(() => {
        bindAuthEvents(isLogin);
    }, 0);

    return `
        <div class="page-container">
            <div style="max-width:420px;margin:0 auto;padding-top:20px">
                <div class="text-center mb-md">
                    <div style="font-size:3rem">🏫</div>
                    <h2>智慧校园失物招领</h2>
                    <p class="text-muted">${isLogin ? '欢迎回来，请登录您的账号' : '创建新账号，加入校园互助'}</p>
                </div>

                <!-- 选项卡 -->
                <div class="tabs">
                    <button class="tab ${isLogin ? 'active' : ''}" id="tabLogin">登录</button>
                    <button class="tab ${!isLogin ? 'active' : ''}" id="tabRegister">注册</button>
                </div>

                <!-- 登录表单 -->
                <div id="loginForm" style="display:${isLogin ? 'block' : 'none'}">
                    <div class="card">
                        <div class="card-body">
                            <div class="form-group">
                                <label class="form-label">用户名 <span class="required">*</span></label>
                                <input type="text" class="form-input" id="loginUsername" placeholder="请输入用户名" autocomplete="username">
                            </div>
                            <div class="form-group">
                                <label class="form-label">密码 <span class="required">*</span></label>
                                <input type="password" class="form-input" id="loginPassword" placeholder="请输入密码" autocomplete="current-password">
                            </div>
                            <div class="form-error" id="loginError" style="display:none"></div>
                            <button class="btn btn-primary btn-block mt" id="loginBtn">登录</button>
                        </div>
                    </div>
                </div>

                <!-- 注册表单 -->
                <div id="registerForm" style="display:${!isLogin ? 'block' : 'none'}">
                    <div class="card">
                        <div class="card-body">
                            <div class="form-group">
                                <label class="form-label">用户名 <span class="required">*</span></label>
                                <input type="text" class="form-input" id="regUsername" placeholder="2-20个字符，支持中文" autocomplete="username">
                            </div>
                            <div class="form-group">
                                <label class="form-label">邮箱 <span class="required">*</span></label>
                                <input type="email" class="form-input" id="regEmail" placeholder="请输入校园邮箱" autocomplete="email">
                            </div>
                            <div class="form-row">
                                <div class="form-group">
                                    <label class="form-label">手机号</label>
                                    <input type="text" class="form-input" id="regPhone" placeholder="选填" autocomplete="tel">
                                </div>
                                <div class="form-group">
                                    <label class="form-label">学号</label>
                                    <input type="text" class="form-input" id="regStudentId" placeholder="选填">
                                </div>
                            </div>
                            <div class="form-group">
                                <label class="form-label">密码 <span class="required">*</span></label>
                                <input type="password" class="form-input" id="regPassword" placeholder="至少6个字符" autocomplete="new-password">
                            </div>
                            <div class="form-group">
                                <label class="form-label">确认密码 <span class="required">*</span></label>
                                <input type="password" class="form-input" id="regPasswordConfirm" placeholder="再次输入密码" autocomplete="new-password">
                            </div>
                            <div class="form-error" id="regError" style="display:none"></div>
                            <button class="btn btn-primary btn-block mt" id="registerBtn">注册</button>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    `;
}

function bindAuthEvents(isLogin) {
    // 选项卡切换
    document.getElementById('tabLogin')?.addEventListener('click', () => {
        navigateTo('/login');
    });
    document.getElementById('tabRegister')?.addEventListener('click', () => {
        navigateTo('/register');
    });

    // 登录
    document.getElementById('loginBtn')?.addEventListener('click', async () => {
        const username = document.getElementById('loginUsername')?.value.trim();
        const password = document.getElementById('loginPassword')?.value;
        const errorEl = document.getElementById('loginError');

        if (!username || !password) {
            if (errorEl) { errorEl.textContent = '请填写用户名和密码'; errorEl.style.display = 'block'; }
            return;
        }

        try {
            const data = await api.post('/api/auth/login', { username, password });
            setCurrentUser(data.user);
            showToast('登录成功！', 'success');
            navigateTo('/');
        } catch (e) {
            if (errorEl) { errorEl.textContent = e.message; errorEl.style.display = 'block'; }
        }
    });

    // 注册
    document.getElementById('registerBtn')?.addEventListener('click', async () => {
        const username = document.getElementById('regUsername')?.value.trim();
        const email = document.getElementById('regEmail')?.value.trim();
        const phone = document.getElementById('regPhone')?.value.trim();
        const studentId = document.getElementById('regStudentId')?.value.trim();
        const password = document.getElementById('regPassword')?.value;
        const passwordConfirm = document.getElementById('regPasswordConfirm')?.value;
        const errorEl = document.getElementById('regError');

        if (!username || !email || !password) {
            if (errorEl) { errorEl.textContent = '请填写必填字段'; errorEl.style.display = 'block'; }
            return;
        }
        if (password !== passwordConfirm) {
            if (errorEl) { errorEl.textContent = '两次密码输入不一致'; errorEl.style.display = 'block'; }
            return;
        }
        if (password.length < 6) {
            if (errorEl) { errorEl.textContent = '密码至少6个字符'; errorEl.style.display = 'block'; }
            return;
        }

        try {
            const data = await api.post('/api/auth/register', {
                username, email, password, phone, student_id: studentId,
            });
            setCurrentUser(data.user);
            showToast('注册成功！', 'success');
            navigateTo('/');
        } catch (e) {
            if (errorEl) { errorEl.textContent = e.message; errorEl.style.display = 'block'; }
        }
    });

    // 回车提交
    document.addEventListener('keydown', function authKeyHandler(e) {
        if (e.key === 'Enter') {
            const loginVisible = document.getElementById('loginForm')?.style.display !== 'none';
            if (loginVisible) {
                document.getElementById('loginBtn')?.click();
            } else {
                document.getElementById('registerBtn')?.click();
            }
        }
    });
}
