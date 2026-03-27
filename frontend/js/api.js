/**
 * API communication layer for dashboard
 */

// API base URL configuration
const DEFAULT_API_BASE_URL = (() => {
    const isLocalHost = ['localhost', '127.0.0.1'].includes(window.location.hostname);
    const isFileProtocol = window.location.protocol === 'file:';
    const isAltLocalPort = isLocalHost && window.location.port && window.location.port !== '8000';
    if (isFileProtocol || isAltLocalPort) return 'http://localhost:8000';
    return window.location.origin;
})();
window.__API_BASE_URL = DEFAULT_API_BASE_URL;
const API_BASE_URL = DEFAULT_API_BASE_URL;
const API_BASE = DEFAULT_API_BASE_URL;

// Timeout configuration (milliseconds)
const ANALYZE_LOCAL_TIMEOUT_MS = 90000;    // Local analysis timeout: 90 seconds
const ANALYZE_GEMINI_TIMEOUT_MS = 120000;  // Gemini AI analysis timeout: 120 seconds

/**
 * Primary API call function
 * @param {string} endpoint - API endpoint path
 * @param {Object} options - Fetch options
 * @returns {Promise<{ok: boolean, data: any, status: number, error?: string}>}
 */
async function apiCall(endpoint, options = {}) {
    try {
        const finalOptions = { ...options };

        if (finalOptions.body) {
            finalOptions.headers = {
                'Content-Type': 'application/json',
                ...(finalOptions.headers || {})
            };
        }

        const response = await fetch(`${DEFAULT_API_BASE_URL}${endpoint}`, finalOptions);
        const data = await response.json().catch(() => ({}));

        if (!response.ok) {
            let msg;

            if (Array.isArray(data?.detail)) {
                msg = data.detail.map(e => e.msg).join(', ');
            } else {
                msg =
                    data?.detail?.message ||
                    data?.detail ||
                    data?.message ||
                    `Request failed (${response.status})`;
            }

            return { ok: false, error: String(msg), status: response.status, data };
        }

        return { ok: true, data, status: response.status };
    } catch (e) {
        if (e.name === 'AbortError') throw e;
        const errorMsg = e.message || "Network error";
        return { ok: false, error: errorMsg, status: 0, data: null };
    }
}

/**
 * API call with timeout control
 * @param {string} endpoint - API endpoint path
 * @param {Object} options - Fetch options
 * @param {number} timeoutMs - Timeout duration (milliseconds)
 * @returns {Promise<{ok: boolean, data: any, status: number, error?: string}>}
 */
async function apiCallWithTimeout(endpoint, options, timeoutMs) {
    const controller = new AbortController();
    const id = setTimeout(() => controller.abort(), timeoutMs);
    try {
        const res = await apiCall(endpoint, { ...options, signal: controller.signal });
        clearTimeout(id);
        return res;
    } catch (e) {
        clearTimeout(id);
        if (e.name === 'AbortError') {
            return { ok: false, error: 'Request timed out. Try again or use a smaller project.', data: null };
        }
        throw e;
    }
}

/**
 * Multi-purpose API request function, supports JSON and FormData
 * @param {string} endpoint - API endpoint path
 * @param {Object} config - Configuration object
 * @param {string} config.method - HTTP method
 * @param {any} config.body - Request body
 * @param {Object} config.headers - Custom headers
 * @returns {Promise<any>} - Response data
 */
async function apiRequest(endpoint, { method = 'GET', body = null, headers = {} } = {}) {
    const opts = { method, headers: { ...headers } };

    const isFormData = body instanceof FormData;

    if (body) {
        opts.body = body;
        if (!isFormData) {
            opts.headers['Content-Type'] = 'application/json';
        }
    }

    const response = await fetch(`${DEFAULT_API_BASE_URL}${endpoint}`, opts);

    // try to parse JSON, but fallback to text if not possible
    const contentType = response.headers.get('content-type') || '';
    const payload = contentType.includes('application/json') ? await response.json() : await response.text();

    if (!response.ok) {
        const msg =
            (payload && typeof payload === 'object' && (payload.detail || payload.message)) ||
            (typeof payload === 'string' ? payload : 'Request failed');
        showMessage(msg, 'error');
        throw new Error(msg);
    }

    return payload;
}
