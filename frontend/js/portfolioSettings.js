/**
 * Portfolio Settings Module
 * Manages portfolio visibility settings and component toggles
 */

// Portfolio settings state
let portfolioSettings = {
    is_public: false,
    show_timeline: true,
    show_heatmap: true,
    show_top_projects: true,
    show_skills: true,
    show_stats: true
};

/**
 * Get current portfolio settings
 * @returns {Object} Current portfolio settings
 */
function getPortfolioSettings() {
    return { ...portfolioSettings };
}

/**
 * Set portfolio mode (public/private)
 * @param {string} mode - 'public' or 'private'
 */
async function setPortfolioMode(mode) {
    portfolioSettings.is_public = (mode === 'public');
    syncSettingsUI();
    await savePortfolioSettings();
}

/**
 * Toggle visibility of a portfolio component
 * @param {string} key - Component key (show_timeline, show_heatmap, etc.)
 */
async function toggleComponent(key) {
    const toggleMap = {
        'show_timeline': 'togTimeline',
        'show_heatmap': 'togHeatmap',
        'show_top_projects': 'togTopProjects',
        'show_skills': 'togSkills',
        'show_stats': 'togStats'
    };
    const el = document.getElementById(toggleMap[key]);
    if (el) portfolioSettings[key] = el.checked;
    applySectionVisibility();
    await savePortfolioSettings();
}

/**
 * Synchronize UI with current settings
 */
function syncSettingsUI() {
    const s = portfolioSettings;
    const priv = document.getElementById('pdPrivateBtn');
    const pub = document.getElementById('pdPublicBtn');
    if (priv && pub) {
        priv.classList.toggle('active', !s.is_public);
        pub.classList.toggle('active', s.is_public);
    }
    const toggleMap = {
        'togTimeline': 'show_timeline',
        'togHeatmap': 'show_heatmap',
        'togTopProjects': 'show_top_projects',
        'togSkills': 'show_skills',
        'togStats': 'show_stats'
    };
    for (const [elId, key] of Object.entries(toggleMap)) {
        const el = document.getElementById(elId);
        if (el) el.checked = s[key] !== false;
    }
    applySectionVisibility();
}

/**
 * Apply section visibility based on settings
 */
function applySectionVisibility() {
    const s = portfolioSettings;
    const map = {
        'pdStatsRow': s.show_stats,
        'pdTimelineSection': s.show_timeline,
        'pdHeatmapSection': s.show_heatmap,
        'pdTopProjectsSection': s.show_top_projects,
        'pdSkillsSection': s.show_skills
    };
    for (const [id, visible] of Object.entries(map)) {
        const el = document.getElementById(id);
        if (el) el.style.display = visible !== false ? '' : 'none';
    }
}

/**
 * Save portfolio settings to server
 */
async function savePortfolioSettings() {
    try {
        if (!currentUser || !currentUser.user_name) {
            console.error('No current user for portfolio settings');
            return;
        }
        
        await apiCall(`/api/portfolio/${currentUser.user_name}/settings`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(portfolioSettings)
        });
    } catch (e) {
        console.error('Failed to save portfolio settings:', e);
    }
}

/**
 * Load portfolio settings from server
 * @param {string} username - Username
 */
async function loadPortfolioSettings(username) {
    try {
        const settingsRes = await apiCall(`/api/portfolio/${username}/settings`);
        if (settingsRes.ok && settingsRes.data.settings) {
            portfolioSettings = settingsRes.data.settings;
            syncSettingsUI();
        }
    } catch (e) {
        console.error('Failed to load portfolio settings:', e);
        // Use defaults on error
    }
}
