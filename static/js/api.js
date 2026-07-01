/**
 * API 请求封装模块
 */

const BASE_URL = window.location.origin;

const api = {
    /**
     * 发送 GET 请求
     */
    async get(url, params = {}) {
        const query = new URLSearchParams(
            Object.entries(params).filter(([_, v]) => v !== '' && v !== null && v !== undefined)
        ).toString();
        const fullUrl = `${BASE_URL}${url}${query ? '?' + query : ''}`;
        return this._request(fullUrl, { method: 'GET' });
    },

    /**
     * 发送 POST 请求
     */
    async post(url, data) {
        const isFormData = data instanceof FormData;
        const options = {
            method: 'POST',
            headers: isFormData ? {} : { 'Content-Type': 'application/json' },
            body: isFormData ? data : JSON.stringify(data),
        };
        return this._request(`${BASE_URL}${url}`, options);
    },

    /**
     * 发送 PUT 请求
     */
    async put(url, data) {
        const options = {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data),
        };
        return this._request(`${BASE_URL}${url}`, options);
    },

    /**
     * 发送 DELETE 请求
     */
    async delete(url) {
        return this._request(`${BASE_URL}${url}`, { method: 'DELETE' });
    },

    /**
     * 上传文件
     */
    async upload(url, formData) {
        const options = {
            method: 'POST',
            body: formData,
        };
        return this._request(`${BASE_URL}${url}`, options);
    },

    /**
     * 内部请求方法
     */
    async _request(url, options) {
        const response = await fetch(url, {
            ...options,
            credentials: 'same-origin',
        });

        // 尝试解析 JSON，失败则返回文本错误
        let data;
        const contentType = response.headers.get('content-type') || '';
        if (contentType.includes('application/json')) {
            data = await response.json();
        } else {
            const text = await response.text();
            // 401 未登录，跳转到登录页
            if (response.status === 401) {
                window.dispatchEvent(new CustomEvent('auth:required'));
            }
            throw new Error(`服务器错误 (${response.status})，请稍后重试`);
        }

        if (!response.ok) {
            if (response.status === 401) {
                window.dispatchEvent(new CustomEvent('auth:required'));
            }
            throw new Error(data.error || `请求失败 (${response.status})`);
        }

        return data;
    },
};

export default api;
