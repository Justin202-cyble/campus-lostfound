/**
 * 发布物品页
 */

import api from '../api.js';
import { isLoggedIn, navigateTo } from '../app.js';
import { showToast } from '../utils.js';

export default async function renderPostItemPage() {
    if (!isLoggedIn()) {
        navigateTo('/login');
        showToast('请先登录后再发布信息', 'warning');
        return '<div class="page-container text-center"><p>正在跳转到登录页...</p></div>';
    }

    let categories = [];
    try {
        const data = await api.get('/api/categories');
        categories = data.categories || [];
    } catch (e) {
        // 忽略
    }

    setTimeout(() => {
        bindPostEvents(categories);
    }, 0);

    return `
        <div class="page-container">
            <h1 class="mb">✏️ 发布信息</h1>

            <div style="max-width:700px">
                <!-- 类型选择 -->
                <div class="type-selector" id="typeSelector">
                    <div class="type-option active" data-type="found">
                        <div class="type-icon">📦</div>
                        <div class="type-label">我捡到了物品</div>
                    </div>
                    <div class="type-option" data-type="lost">
                        <div class="type-icon">🔍</div>
                        <div class="type-label">我丢失了物品</div>
                    </div>
                    <div class="type-option" data-type="exchange">
                        <div class="type-icon">🔄</div>
                        <div class="type-label">我想交换物品</div>
                    </div>
                </div>

                <div class="card">
                    <div class="card-body">
                        <form id="postForm" enctype="multipart/form-data">
                            <!-- 分类 -->
                            <div class="form-group">
                                <label class="form-label">物品分类 <span class="required">*</span></label>
                                <select class="form-select" id="postCategory" required>
                                    <option value="">请选择分类</option>
                                    ${categories.map(c => `
                                        <option value="${c.id}">${c.icon} ${c.name}</option>
                                    `).join('')}
                                </select>
                            </div>

                            <!-- 标题 -->
                            <div class="form-group">
                                <label class="form-label">物品名称 <span class="required">*</span></label>
                                <input type="text" class="form-input" id="postTitle"
                                       placeholder="如：黑色联想笔记本电脑" maxlength="100" required>
                            </div>

                            <!-- 动态字段（根据类型变化） -->
                            <div id="dynamicFields"></div>

                            <!-- 描述 -->
                            <div class="form-group">
                                <label class="form-label">详细描述 <span class="required">*</span></label>
                                <textarea class="form-textarea" id="postDescription"
                                          placeholder="请详细描述物品特征、品牌、颜色等..." rows="4" required></textarea>
                            </div>

                            <!-- 联系方式 -->
                            <div class="form-group" id="contactGroup">
                                <label class="form-label">联系方式</label>
                                <input type="text" class="form-input" id="postContact"
                                       placeholder="手机号/微信号（选填，方便失主联系您）">
                            </div>

                            <!-- 图片上传 -->
                            <div class="form-group">
                                <label class="form-label">物品图片</label>
                                <div class="upload-area" id="uploadArea">
                                    <div class="upload-placeholder" id="uploadPlaceholder">
                                        <div style="font-size:3rem">📷</div>
                                        <div class="upload-text">点击上传物品图片（可选）</div>
                                        <div class="form-hint">支持 JPG、PNG、GIF、WebP，最大 16MB</div>
                                    </div>
                                    <img id="uploadPreview" style="display:none" alt="预览">
                                    <input type="file" id="photoFile" accept="image/*">
                                </div>
                            </div>

                            <div class="form-error" id="postError" style="display:none"></div>

                            <button type="submit" class="btn btn-primary btn-lg btn-block mt" id="submitBtn">
                                发布信息
                            </button>
                        </form>
                    </div>
                </div>
            </div>
        </div>
    `;
}

function bindPostEvents(categories) {
    let currentType = 'found';
    const typeOptions = document.querySelectorAll('.type-option');
    const dynamicFields = document.getElementById('dynamicFields');
    const contactGroup = document.getElementById('contactGroup');

    // 渲染动态字段
    function renderDynamicFields(type) {
        if (type === 'found') {
            contactGroup.style.display = 'block';
            dynamicFields.innerHTML = `
                <div class="form-row">
                    <div class="form-group">
                        <label class="form-label">拾取地点 <span class="required">*</span></label>
                        <input type="text" class="form-input" id="postLocation"
                               placeholder="如：图书馆二楼自习室" required>
                    </div>
                    <div class="form-group">
                        <label class="form-label">拾取时间 <span class="required">*</span></label>
                        <input type="datetime-local" class="form-input" id="postTime" required>
                    </div>
                </div>
            `;
        } else if (type === 'lost') {
            contactGroup.style.display = 'block';
            dynamicFields.innerHTML = `
                <div class="form-row">
                    <div class="form-group">
                        <label class="form-label">丢失地点 <span class="required">*</span></label>
                        <input type="text" class="form-input" id="postLocation"
                               placeholder="如：第一食堂二楼" required>
                    </div>
                    <div class="form-group">
                        <label class="form-label">丢失时间 <span class="required">*</span></label>
                        <input type="datetime-local" class="form-input" id="postTime" required>
                    </div>
                </div>
            `;
        } else if (type === 'exchange') {
            contactGroup.style.display = 'none';
            dynamicFields.innerHTML = `
                <div class="form-row">
                    <div class="form-group">
                        <label class="form-label">新旧程度 <span class="required">*</span></label>
                        <select class="form-select" id="postCondition" required>
                            <option value="brand_new">全新</option>
                            <option value="good" selected>较新</option>
                            <option value="used">使用过</option>
                            <option value="worn">有磨损</option>
                        </select>
                    </div>
                    <div class="form-group">
                        <label class="form-label">期望交换物品 <span class="required">*</span></label>
                        <input type="text" class="form-input" id="postDesired"
                               placeholder="想要换什么？如：蓝牙耳机" required>
                    </div>
                </div>
            `;
        }
    }

    // 初始化
    renderDynamicFields('found');

    // 类型切换
    typeOptions.forEach(option => {
        option.addEventListener('click', () => {
            typeOptions.forEach(o => o.classList.remove('active'));
            option.classList.add('active');
            currentType = option.dataset.type;
            renderDynamicFields(currentType);
        });
    });

    // 图片预览
    const photoInput = document.getElementById('photoFile');
    const uploadPreview = document.getElementById('uploadPreview');
    const uploadPlaceholder = document.getElementById('uploadPlaceholder');
    const uploadArea = document.getElementById('uploadArea');

    if (photoInput) {
        photoInput.addEventListener('change', () => {
            const file = photoInput.files[0];
            if (file) {
                const reader = new FileReader();
                reader.onload = (e) => {
                    uploadPreview.src = e.target.result;
                    uploadPreview.style.display = 'block';
                    uploadPlaceholder.style.display = 'none';
                    uploadArea.classList.add('has-image');
                };
                reader.readAsDataURL(file);
            } else {
                uploadPreview.style.display = 'none';
                uploadPlaceholder.style.display = '';
                uploadArea.classList.remove('has-image');
            }
        });
    }

    // 表单提交
    document.getElementById('postForm')?.addEventListener('submit', async (e) => {
        e.preventDefault();

        const title = document.getElementById('postTitle')?.value.trim();
        const categoryId = document.getElementById('postCategory')?.value;
        const description = document.getElementById('postDescription')?.value.trim();
        const errorEl = document.getElementById('postError');

        if (!title || !categoryId || !description) {
            if (errorEl) { errorEl.textContent = '请填写所有必填字段'; errorEl.style.display = 'block'; }
            return;
        }

        const formData = new FormData();
        formData.append('title', title);
        formData.append('category_id', categoryId);
        formData.append('description', description);

        if (currentType === 'found' || currentType === 'lost') {
            const location = document.getElementById('postLocation')?.value.trim();
            const time = document.getElementById('postTime')?.value;
            const contact = document.getElementById('postContact')?.value.trim();

            if (!location || !time) {
                if (errorEl) { errorEl.textContent = '请填写地点和时间'; errorEl.style.display = 'block'; }
                return;
            }

            formData.append(currentType === 'found' ? 'location_found' : 'location_lost', location);
            formData.append(currentType === 'found' ? 'found_time' : 'lost_time', time);
            if (contact) formData.append('contact_info', contact);
        } else if (currentType === 'exchange') {
            const condition = document.getElementById('postCondition')?.value || 'good';
            const desired = document.getElementById('postDesired')?.value.trim();

            if (!desired) {
                if (errorEl) { errorEl.textContent = '请填写期望交换物品'; errorEl.style.display = 'block'; }
                return;
            }

            formData.append('item_condition', condition);
            formData.append('desired_exchange', desired);
        }

        // 图片
        const photoFile = document.getElementById('photoFile')?.files[0];
        if (photoFile) {
            formData.append('photo_file', photoFile);
        }

        // 提交按钮加载状态
        const submitBtn = document.getElementById('submitBtn');
        submitBtn.disabled = true;
        submitBtn.textContent = '发布中...';

        try {
            const data = await api.upload(`/api/items/${currentType}`, formData);
            showToast('发布成功！', 'success');
            navigateTo(`/item/${currentType}/${data.item.id}`);
        } catch (err) {
            if (errorEl) { errorEl.textContent = err.message; errorEl.style.display = 'block'; }
            submitBtn.disabled = false;
            submitBtn.textContent = '发布信息';
        }
    });
}
