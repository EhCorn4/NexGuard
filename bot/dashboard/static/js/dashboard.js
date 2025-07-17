// NexGuard Dashboard JavaScript

// Global variables
let autoRefresh = false;
let refreshInterval = null;

// Initialize dashboard when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    initializeDashboard();
    setupEventListeners();
    updateTimestamps();
    
    // Update timestamps every minute
    setInterval(updateTimestamps, 60000);
});

// Initialize dashboard components
function initializeDashboard() {
    // Initialize tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function(tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
    
    // Initialize popovers
    var popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    var popoverList = popoverTriggerList.map(function(popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });
    
    // Check for saved theme preference
    const savedTheme = localStorage.getItem('nexguard-theme');
    if (savedTheme) {
        setTheme(savedTheme);
    }
    
    // Load auto-refresh preference
    const autoRefreshPref = localStorage.getItem('nexguard-auto-refresh');
    if (autoRefreshPref === 'true') {
        toggleAutoRefresh(true);
    }
}

// Setup event listeners
function setupEventListeners() {
    // Theme toggle
    const themeToggle = document.getElementById('themeToggle');
    if (themeToggle) {
        themeToggle.addEventListener('click', toggleTheme);
    }
    
    // Auto-refresh toggle
    const autoRefreshToggle = document.getElementById('autoRefreshToggle');
    if (autoRefreshToggle) {
        autoRefreshToggle.addEventListener('click', () => toggleAutoRefresh());
    }
    
    // Search functionality
    const searchInputs = document.querySelectorAll('[data-search]');
    searchInputs.forEach(input => {
        input.addEventListener('input', handleSearch);
    });
    
    // Copy to clipboard functionality
    const copyButtons = document.querySelectorAll('[data-copy]');
    copyButtons.forEach(button => {
        button.addEventListener('click', handleCopy);
    });
}

// Theme management
function toggleTheme() {
    const currentTheme = document.documentElement.getAttribute('data-bs-theme');
    const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
    setTheme(newTheme);
}

function setTheme(theme) {
    document.documentElement.setAttribute('data-bs-theme', theme);
    localStorage.setItem('nexguard-theme', theme);
    
    const themeIcon = document.querySelector('#themeToggle i');
    if (themeIcon) {
        themeIcon.className = theme === 'dark' ? 'bi bi-sun' : 'bi bi-moon';
    }
}

// Auto-refresh functionality
function toggleAutoRefresh(enable = null) {
    if (enable === null) {
        autoRefresh = !autoRefresh;
    } else {
        autoRefresh = enable;
    }
    
    if (autoRefresh) {
        refreshInterval = setInterval(refreshDashboardData, 30000); // 30 seconds
        showAlert('Auto-refresh enabled', 'info');
    } else {
        if (refreshInterval) {
            clearInterval(refreshInterval);
            refreshInterval = null;
        }
        showAlert('Auto-refresh disabled', 'info');
    }
    
    localStorage.setItem('nexguard-auto-refresh', autoRefresh.toString());
    
    const toggleButton = document.getElementById('autoRefreshToggle');
    if (toggleButton) {
        toggleButton.classList.toggle('active', autoRefresh);
        toggleButton.innerHTML = autoRefresh ? 
            '<i class="bi bi-pause"></i> Auto-refresh' : 
            '<i class="bi bi-play"></i> Auto-refresh';
    }
}

// Refresh dashboard data
async function refreshDashboardData() {
    try {
        const response = await fetch('/api/dashboard/data');
        if (response.ok) {
            const data = await response.json();
            updateDashboardElements(data);
        }
    } catch (error) {
        console.error('Failed to refresh dashboard data:', error);
    }
}

// Update dashboard elements with new data
function updateDashboardElements(data) {
    // Update bot status
    const statusElement = document.getElementById('botStatus');
    if (statusElement && data.bot_status) {
        statusElement.textContent = data.bot_status.status;
        statusElement.className = `badge bg-${data.bot_status.status === 'online' ? 'success' : 'danger'}`;
    }
    
    // Update statistics
    const statsElements = document.querySelectorAll('[data-stat]');
    statsElements.forEach(element => {
        const statName = element.getAttribute('data-stat');
        if (data.stats && data.stats[statName] !== undefined) {
            element.textContent = formatNumber(data.stats[statName]);
        }
    });
    
    // Update recent activity
    if (data.recent_activity) {
        updateRecentActivity(data.recent_activity);
    }
}

// Update recent activity list
function updateRecentActivity(activities) {
    const activityContainer = document.getElementById('recentActivity');
    if (!activityContainer) return;
    
    activityContainer.innerHTML = '';
    
    activities.forEach(activity => {
        const activityElement = createActivityElement(activity);
        activityContainer.appendChild(activityElement);
    });
}

// Create activity element
function createActivityElement(activity) {
    const div = document.createElement('div');
    div.className = 'activity-item d-flex align-items-center mb-3';
    
    const icon = activity.success ? 'check-circle text-success' : 'x-circle text-danger';
    const time = formatRelativeTime(new Date(activity.created_at));
    
    div.innerHTML = `
        <div class="activity-icon me-3">
            <i class="bi bi-${icon}"></i>
        </div>
        <div class="flex-grow-1">
            <div class="fw-bold">${activity.command_name}</div>
            <small class="text-muted">${time}</small>
        </div>
    `;
    
    return div;
}

// Search functionality
function handleSearch(event) {
    const searchTerm = event.target.value.toLowerCase();
    const targetSelector = event.target.getAttribute('data-search');
    const targetElements = document.querySelectorAll(targetSelector);
    
    targetElements.forEach(element => {
        const text = element.textContent.toLowerCase();
        const shouldShow = text.includes(searchTerm);
        element.style.display = shouldShow ? '' : 'none';
    });
}

// Copy to clipboard functionality
async function handleCopy(event) {
    const textToCopy = event.target.getAttribute('data-copy');
    
    try {
        await navigator.clipboard.writeText(textToCopy);
        showAlert('Copied to clipboard', 'success');
    } catch (error) {
        // Fallback for older browsers
        const textArea = document.createElement('textarea');
        textArea.value = textToCopy;
        document.body.appendChild(textArea);
        textArea.select();
        document.execCommand('copy');
        document.body.removeChild(textArea);
        showAlert('Copied to clipboard', 'success');
    }
}

// Update relative timestamps
function updateTimestamps() {
    const timestamps = document.querySelectorAll('[data-timestamp]');
    timestamps.forEach(element => {
        const timestamp = element.getAttribute('data-timestamp');
        const date = new Date(timestamp);
        element.textContent = formatRelativeTime(date);
    });
}

// Format relative time
function formatRelativeTime(date) {
    const now = new Date();
    const diffInSeconds = Math.floor((now - date) / 1000);
    
    if (diffInSeconds < 60) {
        return 'Just now';
    } else if (diffInSeconds < 3600) {
        const minutes = Math.floor(diffInSeconds / 60);
        return `${minutes}m ago`;
    } else if (diffInSeconds < 86400) {
        const hours = Math.floor(diffInSeconds / 3600);
        return `${hours}h ago`;
    } else {
        const days = Math.floor(diffInSeconds / 86400);
        return `${days}d ago`;
    }
}

// Format numbers with appropriate suffixes
function formatNumber(num) {
    if (num >= 1000000) {
        return (num / 1000000).toFixed(1) + 'M';
    } else if (num >= 1000) {
        return (num / 1000).toFixed(1) + 'K';
    }
    return num.toString();
}

// Show alert notification
function showAlert(message, type = 'info', duration = 5000) {
    const alertContainer = document.getElementById('alertContainer') || createAlertContainer();
    
    const alertId = 'alert-' + Date.now();
    const alertElement = document.createElement('div');
    alertElement.id = alertId;
    alertElement.className = `alert alert-${type} alert-dismissible fade show`;
    alertElement.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    alertContainer.appendChild(alertElement);
    
    // Auto-dismiss after duration
    setTimeout(() => {
        const alert = document.getElementById(alertId);
        if (alert) {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }
    }, duration);
}

// Create alert container if it doesn't exist
function createAlertContainer() {
    const container = document.createElement('div');
    container.id = 'alertContainer';
    container.className = 'position-fixed top-0 end-0 p-3';
    container.style.zIndex = '1050';
    document.body.appendChild(container);
    return container;
}

// API request helper
async function apiRequest(url, options = {}) {
    const defaultOptions = {
        headers: {
            'Content-Type': 'application/json',
            'X-Requested-With': 'XMLHttpRequest'
        }
    };
    
    const mergedOptions = { ...defaultOptions, ...options };
    
    try {
        const response = await fetch(url, mergedOptions);
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const contentType = response.headers.get('content-type');
        if (contentType && contentType.includes('application/json')) {
            return await response.json();
        } else {
            return await response.text();
        }
    } catch (error) {
        console.error('API request failed:', error);
        showAlert('Request failed: ' + error.message, 'danger');
        throw error;
    }
}

// Command execution helper
async function executeCommand(command, guildId = null, args = {}) {
    try {
        const response = await apiRequest('/api/commands/execute', {
            method: 'POST',
            body: JSON.stringify({
                command: command,
                guild_id: guildId,
                args: args
            })
        });
        
        if (response.success) {
            showAlert(`Command /${command} executed successfully!`, 'success');
            return response;
        } else {
            showAlert(`Command /${command} failed: ${response.message}`, 'danger');
            return null;
        }
    } catch (error) {
        showAlert(`Failed to execute command /${command}`, 'danger');
        return null;
    }
}

// Form validation helper
function validateForm(formElement) {
    const requiredFields = formElement.querySelectorAll('[required]');
    let isValid = true;
    
    requiredFields.forEach(field => {
        if (!field.value.trim()) {
            field.classList.add('is-invalid');
            isValid = false;
        } else {
            field.classList.remove('is-invalid');
        }
    });
    
    return isValid;
}

// Loading state management
function setLoadingState(element, isLoading) {
    if (isLoading) {
        element.disabled = true;
        element.innerHTML = '<span class="loading-spinner me-2"></span>Loading...';
    } else {
        element.disabled = false;
        element.innerHTML = element.getAttribute('data-original-text') || 'Submit';
    }
}

// Export functions for global use
window.NexGuardDashboard = {
    showAlert,
    apiRequest,
    executeCommand,
    validateForm,
    setLoadingState,
    formatNumber,
    formatRelativeTime,
    toggleAutoRefresh,
    refreshDashboardData
};