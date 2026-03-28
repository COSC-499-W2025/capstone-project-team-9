/**
 * Upload Module
 * 
 * Handles all project upload and file merge functionality.
 * 
 * Dependencies:
 * - Global variables: currentUser, selectedProjectId, API_BASE_URL
 * - utils.js: showMessage, escapeHtml, renderError, renderSuccess
 * - api.js: apiRequest
 * - Dashboard functions: loadProjects
 */

/**
 * Sets up drag-and-drop functionality for file upload zones
 * @param {string} inputId - ID of the file input element
 * @param {string} infoId - ID of the info display element
 * @param {string} fileNameId - ID of the filename display element
 * @param {string} uploadBtnId - ID of the upload button
 * @param {string} clearBtnId - ID of the clear button
 */
function setupFileUploadDragDrop(inputId, infoId, fileNameId, uploadBtnId, clearBtnId) {
    const zone = document.getElementById(infoId)?.closest('.file-upload-zone') || document.getElementById(inputId)?.closest('div');
    const input = document.getElementById(inputId);
    if (!zone || !input) return;
    zone.addEventListener('dragover', (e) => { e.preventDefault(); e.stopPropagation(); zone.classList.add('dragover'); });
    zone.addEventListener('dragleave', (e) => { e.preventDefault(); zone.classList.remove('dragover'); });
    zone.addEventListener('drop', (e) => {
        e.preventDefault();
        e.stopPropagation();
        zone.classList.remove('dragover');
        const files = e.dataTransfer?.files;
        if (files?.length) {
            input.files = files;
            const nameEl = document.getElementById(fileNameId);
            if (nameEl) nameEl.textContent = files[0].name;
            const infoEl = document.getElementById(infoId);
            if (infoEl) infoEl.style.display = 'block';
            const uploadBtn = document.getElementById(uploadBtnId);
            if (uploadBtn) uploadBtn.disabled = false;
            const clearBtn = document.getElementById(clearBtnId);
            if (clearBtn) clearBtn.style.display = 'inline-block';
        }
    });
}

/**
 * Handles file selection for project upload
 */
function handleUploadFileSelect() {
    const fileInput = document.getElementById('zipFile');
    const fileInfo = document.getElementById('uploadFileInfo');
    const fileName = document.getElementById('uploadFileName');
    const uploadBtn = document.getElementById('uploadBtn');
    const clearBtn = document.getElementById('clearUploadBtn');
    const customFileNameInput = document.getElementById('customFileName');
    
    if (fileInput?.files[0]) {
        const file = fileInput.files[0];
        fileName.textContent = file.name;
        fileInfo.style.display = 'block';
        uploadBtn.disabled = false;
        clearBtn.style.display = 'inline-block';
        
        // Auto-populate custom filename field with original filename (without .zip)
        if (customFileNameInput && !customFileNameInput.value) {
            const baseName = file.name.replace(/\.zip$/i, '');
            customFileNameInput.placeholder = `Default: ${baseName}`;
        }
    }
}

/**
 * Clears the upload file selection and resets the form
 */
function clearUploadFile() {
    const fileInput = document.getElementById('zipFile');
    const fileInfo = document.getElementById('uploadFileInfo');
    const uploadBtn = document.getElementById('uploadBtn');
    const clearBtn = document.getElementById('clearUploadBtn');
    const customFileNameInput = document.getElementById('customFileName');
    
    if (fileInput) {
        fileInput.value = '';
        fileInfo.style.display = 'none';
        uploadBtn.disabled = true;
        clearBtn.style.display = 'none';
    }
    
    // Clear custom filename input
    if (customFileNameInput) {
        customFileNameInput.value = '';
        customFileNameInput.placeholder = 'Leave empty to use original filename';
    }
}

/**
 * Handles file selection for project merge
 */
function handleMergeFileSelect() {
    const fileInput = document.getElementById('mergeZipFile');
    const fileInfo = document.getElementById('mergeFileInfo');
    const fileName = document.getElementById('mergeFileName');
    const mergeBtn = document.getElementById('mergeBtn');
    const clearBtn = document.getElementById('clearMergeBtn');
    
    if (fileInput?.files[0]) {
        const file = fileInput.files[0];
        fileName.textContent = file.name;
        fileInfo.style.display = 'block';
        mergeBtn.disabled = false;
        clearBtn.style.display = 'inline-block';
    }
}

/**
 * Clears the merge file selection and resets the form
 */
function clearMergeFile() {
    const fileInput = document.getElementById('mergeZipFile');
    const fileInfo = document.getElementById('mergeFileInfo');
    const mergeBtn = document.getElementById('mergeBtn');
    const clearBtn = document.getElementById('clearMergeBtn');
    
    if (fileInput) {
        fileInput.value = '';
        fileInfo.style.display = 'none';
        mergeBtn.disabled = true;
        clearBtn.style.display = 'none';
    }
}

/**
 * Uploads a file with progress tracking
 * @param {string} url - The API endpoint URL
 * @param {FormData} formData - The form data containing the file
 * @param {Function} onProgress - Callback function for progress updates (pct, phase)
 * @returns {Promise<Object>} The server response
 */
function uploadWithProgress(url, formData, onProgress) {
    return new Promise((resolve, reject) => {
        const xhr = new XMLHttpRequest();
        const fullUrl = (typeof API_BASE_URL !== 'undefined' ? API_BASE_URL : '') + url;
        xhr.open('POST', fullUrl);
        let extractShown = false;
        xhr.upload.addEventListener('progress', (e) => {
            if (e.lengthComputable && e.total > 0) {
                const pct = Math.round((e.loaded / e.total) * 100);
                onProgress(pct, 'upload');
                if (pct >= 100 && !extractShown) {
                    extractShown = true;
                    onProgress(100, 'extract');
                }
            }
        });
        xhr.addEventListener('load', () => {
            if (xhr.status >= 200 && xhr.status < 300) {
                try {
                    const data = JSON.parse(xhr.responseText || '{}');
                    resolve(data);
                } catch {
                    resolve({});
                }
            } else {
                try {
                    const err = JSON.parse(xhr.responseText || '{}');
                    reject(new Error(err.message || err.detail || `Upload failed (${xhr.status})`));
                } catch {
                    reject(new Error(`Upload failed (${xhr.status})`));
                }
            }
        });
        xhr.addEventListener('error', () => reject(new Error('Network error')));
        xhr.addEventListener('abort', () => reject(new Error('Upload cancelled')));
        xhr.send(formData);
    });
}

/**
 * Renders the upload progress UI
 * @param {number} pct - Progress percentage (0-100)
 * @param {string} phase - Current phase ('upload' or 'extract')
 * @returns {string} HTML string for the progress UI
 */
function renderUploadProgress(pct, phase) {
    const label = phase === 'extract' ? 'Extracting files…' : `Uploading… ${pct}%`;
    const isIndeterminate = phase === 'extract';
    const barStyle = isIndeterminate
        ? 'width: 100%; animation: upload-pulse 1.2s ease-in-out infinite;'
        : `width: ${pct}%; transition: width 0.15s ease;`;
    return `<div class="upload-progress-wrap" style="padding: 20px; max-width: 400px; margin: 0 auto;">
        <p class="upload-progress-label" style="margin: 0 0 10px 0; font-size: 14px; color: var(--text-secondary, #64748b);">${label}</p>
        <div class="upload-progress-track" style="height: 8px; background: var(--bg-tertiary, #e2e8f0); border-radius: 4px; overflow: hidden;">
            <div class="upload-progress-bar" style="height: 100%; background: var(--accent, #3b82f6); border-radius: 4px; ${barStyle}"></div>
        </div>
    </div>`;
}

/**
 * Uploads a project ZIP file to the server
 */
async function uploadFile() {
    const fileInput = document.getElementById('zipFile');
    const customFileNameInput = document.getElementById('customFileName');
    const resultDiv = document.getElementById('uploadResult');
    if (!fileInput?.files[0]) {
        showMessage('Please select a file', 'error');
        return;
    }
    const formData = new FormData();
    formData.append('file', fileInput.files[0]);
    
    // Get custom filename if provided
    const customFileName = customFileNameInput?.value?.trim();
    if (customFileName) {
        // Ensure .zip extension
        const fileName = customFileName.endsWith('.zip') ? customFileName : customFileName + '.zip';
        formData.append('custom_filename', fileName);
    }
    
    resultDiv.innerHTML = renderUploadProgress(0, 'upload');
    const updateProgress = (pct, phase) => {
        resultDiv.innerHTML = renderUploadProgress(pct, phase);
    };
    try {
        const data = await uploadWithProgress(
            `/api/projects/upload?user_name=${encodeURIComponent(currentUser.user_name || '')}`,
            formData,
            (pct, phase) => updateProgress(pct, phase || 'upload')
        );
        if (data.success) {
            const name = (data.data?.filename || data.filename || 'Project').replace(/^.*[/\\]/, '').replace(/\.zip$/i, '') || 'Project';
            const id = (data.data?.file_id ?? data.project_id ?? data.data?.project_id) != null ? String(data.data?.file_id ?? data.project_id ?? data.data?.project_id) : '—';
            resultDiv.innerHTML = `<div class="message success">Project uploaded successfully.<br><br><strong>Project name:</strong> ${escapeHtml(name)}<br><strong>Project ID:</strong> ${escapeHtml(id)}</div>`;
            showMessage('Project uploaded successfully', 'success');
            loadProjects();
            clearUploadFile();
        } else {
            renderError(resultDiv, data.message || data.data?.message || 'Upload failed');
        }
    } catch (e) {
        renderError(resultDiv, e.message || 'Upload failed');
    }
}

/**
 * Merges a ZIP file into an existing project
 */
async function mergeZipToProject() {
    if (!selectedProjectId) {
        renderError(document.getElementById('mergeResult'), 'Please select a project to merge into');
        return;
    }
    const fileInput = document.getElementById('mergeZipFile');
    const resultDiv = document.getElementById('mergeResult');
    if (!fileInput?.files[0]) {
        renderError(resultDiv, 'Please select a ZIP file to merge');
        return;
    }
    const file = fileInput.files[0];
    if (!file.name.endsWith('.zip')) {
        renderError(resultDiv, 'Only ZIP files can be merged');
        return;
    }
    const formData = new FormData();
    formData.append('file', file);
    resultDiv.innerHTML = '<div style="text-align: center; padding: 20px;"><p>Merging files into project...</p></div>';
    try {
        const data = await apiRequest(`/api/projects/${selectedProjectId}/merge?user_name=${currentUser.user_name}`, {
            method: 'POST',
            body: formData
        });
        if (data.success) {
            renderSuccess(resultDiv, `Files merged successfully into project ${selectedProjectId}.`);
            loadProjects();
            clearMergeFile();
        } else {
            renderError(resultDiv, data.message || 'Merge failed');
        }
    } catch (e) {
        renderError(resultDiv, e.message);
    }
}
