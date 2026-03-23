/**
 * Portfolio Customization Module
 * Manages project customizations for portfolio display
 */

// State variables
let customizedProjectIds = [];
let currentCustomizingProjectId = null;

// Cache DOM elements for modal
let modalElements = null;

/**
 * Get and cache modal DOM elements
 * @returns {Object} Modal elements
 */
function getModalElements() {
    if (!modalElements) {
        modalElements = {
            modal: document.getElementById('customizeModal'),
            projectName: document.getElementById('modalProjectName'),
            title: document.getElementById('customTitle'),
            description: document.getElementById('customDescription'),
            role: document.getElementById('customRole')
        };
    }
    return modalElements;
}

/**
 * Load list of projects with customization status
 */
async function loadCustomizedProjects() {
    const container = document.getElementById('customizeProjectsList');
    if (!container) return;

    container.innerHTML = '<p style="text-align: center; padding: 20px;">Loading projects...</p>';

    if (!currentUser || !currentUser.user_name) {
        container.innerHTML = '<p class="message error">Not logged in</p>';
        return;
    }

    const result = await apiCall(`/api/portfolio/${currentUser.user_name}/custom-data`);

    if (!result.ok) {
        container.innerHTML = '<p class="message error">Error loading projects</p>';
        showMessage(result.error || 'Failed to load projects', 'error');
        return;
    }

    customizedProjectIds = result.data.project_ids || [];

    // Access global projects variable from dashboard
    if (!window.projects || !window.projects.length) {
        container.innerHTML = '<p>No projects found. Upload projects first.</p>';
        return;
    }

    container.innerHTML = window.projects.map(p => {
        const isCustomized = customizedProjectIds.includes(p.id);
        const badge = isCustomized ? '<span class="badge-customized">CUSTOMIZED</span>' : '';
        return `<div class="project-item">
            <div class="project-row">
                <div class="project-info">
                    <strong>${escapeHtml(p.filename)}</strong> (ID: ${p.id})${badge}
                    <br>
                    <small>Files: ${p.file_count || 0} | Created: ${new Date(p.created_at).toLocaleDateString()}</small>
                </div>
                <button class="btn-customize" onclick="openCustomizeModal(${p.id}, '${p.filename.replace(/'/g, "\\'")}')">
                    ${isCustomized ? 'Edit' : 'Customize'}
                </button>
            </div>
        </div>`;
    }).join('');
}

/**
 * Open customization modal for a project
 * @param {number} projectId - Project ID
 * @param {string} projectName - Project name
 */
async function openCustomizeModal(projectId, projectName) {
    currentCustomizingProjectId = projectId;
    const elements = getModalElements();
    
    if (!elements.modal) {
        console.error('Customize modal not found');
        return;
    }
    
    elements.projectName.textContent = projectName;
    
    // Clear form
    elements.title.value = '';
    elements.description.value = '';
    elements.role.value = '';
    
    // Load existing customization if any
    try {
        if (!currentUser || !currentUser.user_name) {
            console.error('No current user');
            return;
        }
        
        const data = await apiCall(`/api/portfolio/${currentUser.user_name}/custom-data/${projectId}`);
        if (data.ok && data.data.success) {
            elements.title.value = data.data.custom_title || '';
            elements.description.value = data.data.custom_description || '';
            elements.role.value = data.data.custom_role || '';
        }
    } catch (e) {
        // No existing customization, keep form empty
        console.log('No existing customization for project', projectId);
    }
    
    elements.modal.classList.add('show');
}

/**
 * Close customization modal
 */
function closeCustomizeModal() {
    const elements = getModalElements();
    if (elements.modal) {
        elements.modal.classList.remove('show');
    }
    currentCustomizingProjectId = null;
}

/**
 * Save customization data
 * @param {Event} event - Form submit event
 */
async function saveCustomization(event) {
    event.preventDefault();

    if (!currentCustomizingProjectId) {
        showMessage('No project selected', 'error');
        return;
    }

    if (!currentUser || !currentUser.user_name) {
        showMessage('Not logged in', 'error');
        return;
    }

    const elements = getModalElements();
    const customTitle = elements.title.value.trim();
    const customDescription = elements.description.value.trim();
    const customRole = elements.role.value.trim();

    const result = await apiCall(`/api/portfolio/${currentUser.user_name}/custom-data`, {
        method: 'POST',
        body: JSON.stringify({
            project_id: currentCustomizingProjectId,
            custom_title: customTitle,
            custom_description: customDescription,
            custom_role: customRole
        })
    });

    if (!result.ok) {
        showMessage(result.error || 'Error saving customization', 'error');
        return;
    }

    showMessage('Portfolio customization saved successfully', 'success');
    closeCustomizeModal();
    await loadCustomizedProjects();
}

/**
 * Clear all customizations for current project
 */
async function clearCustomization() {
    if (!currentCustomizingProjectId) {
        showMessage('No project selected', 'error');
        return;
    }

    if (!confirm('Are you sure you want to clear all customizations for this project?')) {
        return;
    }

    if (!currentUser || !currentUser.user_name) {
        showMessage('Not logged in', 'error');
        return;
    }

    const result = await apiCall(`/api/portfolio/${currentUser.user_name}/custom-data/${currentCustomizingProjectId}`, {
        method: 'DELETE'
    });

    if (!result.ok) {
        showMessage(result.error || 'Error clearing customization', 'error');
        return;
    }

    showMessage('Portfolio customization cleared', 'success');
    closeCustomizeModal();
    await loadCustomizedProjects();
}

/**
 * Initialize portfolio customization module
 * Sets up event listeners and modal close handlers
 */
function initPortfolioCustomization() {
    // Close modal when clicking outside
    window.addEventListener('click', function(event) {
        const elements = getModalElements();
        if (elements.modal && event.target === elements.modal) {
            closeCustomizeModal();
        }
    });
}

// Initialize when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initPortfolioCustomization);
} else {
    initPortfolioCustomization();
}
