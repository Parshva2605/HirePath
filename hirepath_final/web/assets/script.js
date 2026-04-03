// HirePath - Global Script
const API_URL = 'http://localhost:8000';

// Page Navigation
function navigateTo(page) {
    // Hide all pages
    document.querySelectorAll('.page').forEach(p => p.style.display = 'none');
    
    // Show target page
    const targetPage = document.getElementById(page);
    if (targetPage) {
        targetPage.style.display = 'block';
        window.scrollTo(0, 0);
    }

    // Update nav
    document.querySelectorAll('.nav-links a').forEach(link => {
        link.classList.remove('active');
        if (link.dataset.page === page) {
            link.classList.add('active');
        }
    });
}

// API Calls
async function apiCall(endpoint, method = 'GET', data = null) {
    try {
        const options = {
            method,
            headers: {
                'Content-Type': 'application/json'
            }
        };

        if (data && method !== 'GET') {
            options.body = JSON.stringify(data);
        }

        const response = await fetch(`${API_URL}${endpoint}`, options);
        
        if (!response.ok) {
            throw new Error(`API Error: ${response.statusText}`);
        }

        return await response.json();
    } catch (error) {
        console.error('API Error:', error);
        throw error;
    }
}

async function apiCallFormData(endpoint, formData) {
    try {
        const response = await fetch(`${API_URL}${endpoint}`, {
            method: 'POST',
            body: formData
        });

        if (!response.ok) {
            throw new Error(`API Error: ${response.statusText}`);
        }

        return await response.json();
    } catch (error) {
        console.error('API Error:', error);
        throw error;
    }
}

// Status Checking
async function checkBackendStatus() {
    try {
        const data = await apiCall('/api/status');
        const statusEl = document.getElementById('backend-status');
        if (statusEl) {
            statusEl.innerHTML = `
                <span class="status online">
                    <span class="dot"></span> Backend Online
                </span>
            `;
        }
        return true;
    } catch {
        const statusEl = document.getElementById('backend-status');
        if (statusEl) {
            statusEl.innerHTML = `
                <span class="status offline">
                    <span class="dot"></span> Backend Offline
                </span>
            `;
        }
        return false;
    }
}

// Utility Functions
function showLoading(element) {
    element.innerHTML = '<div style="padding: 20px; text-align: center; color: #666;">Loading...</div>';
}

function showError(element, message) {
    element.innerHTML = `<div class="alert alert-danger">${message}</div>`;
}

function formatBytes(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
}

function getScoreBadgeClass(score) {
    if (score >= 80) return 'success';
    if (score >= 60) return 'warning';
    return 'danger';
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', function() {
    // Check backend status
    checkBackendStatus();

    // Setup navigation listeners
    document.querySelectorAll('.nav-links a').forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            const page = this.dataset.page;
            navigateTo(page);
        });
    });

    // Show home page by default
    navigateTo('home');
});

// Prevent form submissions from reloading page
document.addEventListener('submit', function(e) {
    if (e.target.tagName === 'FORM') {
        e.preventDefault();
    }
}, true);
