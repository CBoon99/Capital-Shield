/**
 * BoonMindX Coerentis Dashboard - Live Data Layer
 * 
 * Polls /healthz and /metrics endpoints every 10 seconds
 * Updates dashboard UI with live data
 */

// Remote API: query ?api=https://your-host, sessionStorage, or optional localStorage (remember)
const STORAGE_ORIGIN = 'coerentis_api_origin';
const STORAGE_KEY = 'coerentis_api_key';
const STORAGE_REMEMBER = 'coerentis_remember_credentials';
const LEGACY_KEY = 'api_key';

let API_BASE = '/api/v1';
let HEALTH_URL = `${API_BASE}/healthz`;
let DASHBOARD_METRICS_URL = `${API_BASE}/dashboard/metrics`;

const POLL_INTERVAL = 10000; // 10 seconds

function rebuildEndpoints() {
    const origin = getApiBaseUrl();
    API_BASE = origin ? `${origin.replace(/\/$/, '')}/api/v1` : '/api/v1';
    HEALTH_URL = `${API_BASE}/healthz`;
    DASHBOARD_METRICS_URL = `${API_BASE}/dashboard/metrics`;
}

function getApiBaseUrl() {
    try {
        const params = new URLSearchParams(window.location.search);
        const q = params.get('api');
        if (q) return q.trim().replace(/\/$/, '');
    } catch (e) { /* ignore */ }
    try {
        const fromSession = sessionStorage.getItem(STORAGE_ORIGIN);
        if (fromSession) return fromSession.replace(/\/$/, '');
        if (localStorage.getItem(STORAGE_REMEMBER) === '1') {
            const o = localStorage.getItem(STORAGE_ORIGIN);
            if (o) return o.replace(/\/$/, '');
        }
    } catch (e) { /* ignore */ }
    return '';
}

function saveConnectionSettings(origin, apiKey, remember) {
    const o = origin.replace(/\/$/, '');
    sessionStorage.setItem(STORAGE_ORIGIN, o);
    sessionStorage.setItem(STORAGE_KEY, apiKey);
    if (remember) {
        localStorage.setItem(STORAGE_REMEMBER, '1');
        localStorage.setItem(STORAGE_ORIGIN, o);
        localStorage.setItem(STORAGE_KEY, apiKey);
    } else {
        localStorage.removeItem(STORAGE_REMEMBER);
        localStorage.removeItem(STORAGE_ORIGIN);
        localStorage.removeItem(STORAGE_KEY);
    }
    rebuildEndpoints();
}

function clearConnectionSettings() {
    sessionStorage.removeItem(STORAGE_ORIGIN);
    sessionStorage.removeItem(STORAGE_KEY);
    localStorage.removeItem(STORAGE_REMEMBER);
    localStorage.removeItem(STORAGE_ORIGIN);
    localStorage.removeItem(STORAGE_KEY);
    localStorage.removeItem(LEGACY_KEY);
    rebuildEndpoints();
}

function initConnectionPanel() {
    const originInput = document.getElementById('conn-api-origin');
    const keyInput = document.getElementById('conn-api-key');
    const rememberInput = document.getElementById('conn-remember');
    const statusEl = document.getElementById('conn-status');
    const base = getApiBaseUrl();
    rebuildEndpoints();
    if (originInput) originInput.value = base || '';
    if (keyInput) keyInput.value = getApiKeyFromStorage() || '';
    if (rememberInput) rememberInput.checked = localStorage.getItem(STORAGE_REMEMBER) === '1';

    document.getElementById('conn-save')?.addEventListener('click', () => {
        const origin = (originInput?.value || '').trim();
        const key = (keyInput?.value || '').trim();
        if (!origin || !/^https:\/\//i.test(origin)) {
            if (statusEl) statusEl.textContent = 'Enter a valid HTTPS API origin (e.g. https://api.example.com).';
            return;
        }
        saveConnectionSettings(origin, key, !!rememberInput?.checked);
        if (statusEl) {
            statusEl.textContent = key
                ? 'Saved. Polling your API…'
                : 'API origin saved. Add an API key to load usage/billing stats.';
        }
        document.querySelector('.usage-section')?.style &&
            (document.querySelector('.usage-section').style.display = key ? 'block' : 'none');
        pollHealth();
        pollMetrics();
        pollUsageStats();
    });
    document.getElementById('conn-clear')?.addEventListener('click', () => {
        clearConnectionSettings();
        if (originInput) originInput.value = '';
        if (keyInput) keyInput.value = '';
        if (rememberInput) rememberInput.checked = false;
        if (statusEl) statusEl.textContent = 'Credentials cleared.';
        pollHealth();
        pollMetrics();
        pollUsageStats();
    });
}

// State
let equityHistory = [];
let drawdownHistory = [];
let lastMetrics = null;
let lastHealth = null;

// Chart instances
let equityChart = null;
let drawdownChart = null;

/**
 * Initialize dashboard
 */
function init() {
    console.log('Coerentis operator dashboard initialized');
    rebuildEndpoints();
    initConnectionPanel();

    // Initialize charts
    initCharts();
    
    // Start polling
    pollHealth();
    pollMetrics();
    pollUsageStats();
    
    setInterval(pollHealth, POLL_INTERVAL);
    setInterval(pollMetrics, POLL_INTERVAL);
    setInterval(pollUsageStats, POLL_INTERVAL);
}

/**
 * Poll /healthz endpoint
 */
async function pollHealth() {
    try {
        const response = await fetch(HEALTH_URL);
        if (!response.ok) {
            throw new Error('Health check failed');
        }
        const data = await response.json();
        
        lastHealth = data;
        
        // Update header status
        const statusBadge = document.getElementById('system-status');
        if (data.status === 'ok') {
            statusBadge.textContent = 'HEALTHY';
            statusBadge.className = 'status-badge healthy';
        } else {
            statusBadge.textContent = 'UNHEALTHY';
            statusBadge.className = 'status-badge unhealthy';
        }
        
        // Update uptime
        const uptimeEl = document.getElementById('uptime');
        uptimeEl.textContent = formatUptime(data.uptime);
        
        // Update health rail status
        updateHealthRailStatus(data.status === 'ok');
        
    } catch (error) {
        console.error('Health check failed:', error);
        showWarning('Health endpoint unavailable');
        updateHealthRailStatus(false);
    }
}

/**
 * Poll /dashboard/metrics endpoint
 */
async function pollMetrics() {
    try {
        const response = await fetch(DASHBOARD_METRICS_URL);
        if (!response.ok) {
            throw new Error('Metrics fetch failed');
        }
        
        const metrics = await response.json();
        
        updateMetricsUI(metrics);
        updateCharts(metrics);
        addEventLog(metrics);
        
        // Hide warning if successful
        document.getElementById('warning-banner').classList.add('hidden');
        
    } catch (error) {
        console.error('Metrics fetch failed:', error);
        showWarning('Metrics endpoint unavailable');
    }
}

/**
 * Poll usage stats endpoint
 * Note: In controlled operations, this requires API key authentication
 */
async function pollUsageStats() {
    try {
        // For demo purposes, try to get usage stats
        // In controlled operations, this requires the user's API key
        // For now, we'll skip if no API key is available
        const apiKey = getApiKeyFromStorage();
        if (!apiKey) {
            // Hide usage section if no API key
            const usageSection = document.querySelector('.usage-section');
            if (usageSection) {
                usageSection.style.display = 'none';
            }
            return;
        }
        
        const response = await fetch(`${API_BASE}/billing/usage/${encodeURIComponent(apiKey)}`);
        if (!response.ok) {
            // If 404, user might not have billing set up yet
            if (response.status === 404) {
                return;
            }
            throw new Error('Usage stats fetch failed');
        }
        
        const usageData = await response.json();
        updateUsageUI(usageData);
        
    } catch (error) {
        console.error('Usage stats fetch failed:', error);
        // Don't show warning for usage stats failures (optional feature)
    }
}

/**
 * Get API key from localStorage (for demo purposes)
 * In controlled operations, this is handled via authentication
 */
function getApiKeyFromStorage() {
    try {
        const k = sessionStorage.getItem(STORAGE_KEY);
        if (k) return k;
        if (localStorage.getItem(STORAGE_REMEMBER) === '1') {
            return localStorage.getItem(STORAGE_KEY);
        }
        const legacy = localStorage.getItem(LEGACY_KEY);
        if (legacy) return legacy;
    } catch (e) { /* ignore */ }
    return null;
}

/**
 * Update usage statistics UI
 */
function updateUsageUI(usageData) {
    // Show usage section
    const usageSection = document.querySelector('.usage-section');
    if (usageSection) {
        usageSection.style.display = 'block';
    }
    
    // Daily Usage
    const dailyUsageEl = document.getElementById('daily-usage');
    if (dailyUsageEl && usageData.usage?.daily_usage !== undefined) {
        dailyUsageEl.textContent = usageData.usage.daily_usage.toLocaleString();
    }
    
    // Daily Limit
    const dailyLimitEl = document.getElementById('daily-limit');
    if (dailyLimitEl && usageData.daily_limit !== undefined && usageData.daily_limit !== null) {
        dailyLimitEl.textContent = `of ${usageData.daily_limit.toLocaleString()}`;
        
        // Show warning if approaching limit
        const usagePercent = (usageData.usage.daily_usage / usageData.daily_limit) * 100;
        if (usagePercent > 90) {
            dailyUsageEl.style.color = '#ef4444'; // Red
        } else if (usagePercent > 75) {
            dailyUsageEl.style.color = '#f59e0b'; // Orange
        } else {
            dailyUsageEl.style.color = '#2EA8FF'; // Blue
        }
    } else if (dailyLimitEl && usageData.daily_limit === null) {
        dailyLimitEl.textContent = 'Unlimited';
    }
    
    // Monthly Total
    const monthlyTotalEl = document.getElementById('monthly-total');
    if (monthlyTotalEl && usageData.usage?.monthly_total !== undefined) {
        monthlyTotalEl.textContent = usageData.usage.monthly_total.toLocaleString();
    }
    
    // Monthly Average
    const monthlyAvgEl = document.getElementById('monthly-avg');
    if (monthlyAvgEl && usageData.usage?.monthly_average !== undefined) {
        monthlyAvgEl.textContent = `Avg: ${usageData.usage.monthly_average.toLocaleString()}/day`;
    }
    
    // Tier
    const tierEl = document.getElementById('usage-tier');
    if (tierEl && usageData.tier) {
        tierEl.textContent = usageData.tier.replace('_', ' ');
    }
    
    // Overage Info
    const overageEl = document.getElementById('overage-info');
    if (overageEl && usageData.overage_rate !== undefined) {
        if (usageData.overage_rate > 0) {
            overageEl.textContent = `Overage: £${usageData.overage_rate.toFixed(4)}/call`;
        } else {
            overageEl.textContent = 'No overages';
        }
    }
}

/**
 * Update metrics UI elements
 */
function updateMetricsUI(metrics) {
    // Current Equity
    const equityEl = document.getElementById('equity');
    if (metrics.equity !== undefined) {
        equityEl.textContent = formatCurrency(metrics.equity);
        updateChange('equity-change', metrics.equity, lastMetrics?.equity);
    }
    
    // P&L %
    const pnlEl = document.getElementById('pnl-percent');
    if (metrics.pnl_percent !== undefined) {
        pnlEl.textContent = formatPercent(metrics.pnl_percent);
        pnlEl.className = 'stat-value ' + (metrics.pnl_percent >= 0 ? 'positive' : 'negative');
        updateChange('pnl-change', metrics.pnl_percent, lastMetrics?.pnl_percent);
    }
    
    // Max Drawdown
    const ddEl = document.getElementById('max-drawdown');
    if (metrics.max_drawdown !== undefined) {
        ddEl.textContent = formatPercent(metrics.max_drawdown);
        ddEl.className = 'stat-value negative';
        updateChange('dd-change', metrics.max_drawdown, lastMetrics?.max_drawdown);
    }
    
    // Total Trades
    const tradesEl = document.getElementById('total-trades');
    if (metrics.trades !== undefined) {
        tradesEl.textContent = metrics.trades.toString();
        updateChange('trades-change', metrics.trades, lastMetrics?.trades);
    }
    
    // Blocked Trades
    const blockedEl = document.getElementById('blocked-trades');
    if (metrics.blocked_trades !== undefined) {
        blockedEl.textContent = metrics.blocked_trades.toString();
        updateChange('blocked-change', metrics.blocked_trades, lastMetrics?.blocked_trades);
    }
    
    // Current Preset
    const presetEl = document.getElementById('current-preset');
    if (metrics.preset) {
        presetEl.textContent = metrics.preset;
    }
    
    lastMetrics = metrics;
}

/**
 * Update change indicator
 */
function updateChange(elementId, current, previous) {
    const el = document.getElementById(elementId);
    if (!el || previous === undefined || previous === null) {
        el.textContent = '';
        return;
    }
    
    const change = current - previous;
    if (change === 0) {
        el.textContent = '';
        return;
    }
    
    const sign = change > 0 ? '+' : '';
    el.textContent = `${sign}${formatNumber(change)}`;
    el.className = 'stat-change ' + (change >= 0 ? 'positive' : 'negative');
}

/**
 * Update safety rails status
 */
function updateHealthRailStatus(healthy) {
    const statusEl = document.getElementById('health-rail-status');
    const indicator = statusEl.querySelector('.status-indicator');
    const text = statusEl.querySelector('.status-text');
    
    if (healthy) {
        indicator.className = 'status-indicator active';
        text.textContent = 'HEALTHY';
    } else {
        indicator.className = 'status-indicator inactive';
        text.textContent = 'UNHEALTHY';
    }
}

function updateDrawdownRailStatus(active) {
    const statusEl = document.getElementById('dd-rail-status');
    const indicator = statusEl.querySelector('.status-indicator');
    const text = statusEl.querySelector('.status-text');
    
    if (active) {
        indicator.className = 'status-indicator active';
        text.textContent = 'ACTIVE';
    } else {
        indicator.className = 'status-indicator warning';
        text.textContent = 'INACTIVE';
    }
}

function updateRegimeGuardStatus(mode) {
    const statusEl = document.getElementById('regime-guard-status');
    const indicator = statusEl.querySelector('.status-indicator');
    const text = statusEl.querySelector('.status-text');
    
    if (mode === 'STRICT') {
        indicator.className = 'status-indicator active';
        text.textContent = 'STRICT';
    } else if (mode === 'PERMISSIVE') {
        indicator.className = 'status-indicator warning';
        text.textContent = 'PERMISSIVE';
    } else {
        indicator.className = 'status-indicator inactive';
        text.textContent = 'UNKNOWN';
    }
}

/**
 * Initialize Chart.js charts
 */
function initCharts() {
    // Equity Chart
    const equityCtx = document.getElementById('equity-chart');
    if (equityCtx) {
        equityChart = new Chart(equityCtx, {
            type: 'line',
            data: {
                labels: [],
                datasets: [{
                    label: 'Equity',
                    data: [],
                    borderColor: '#10b981',
                    backgroundColor: 'rgba(16, 185, 129, 0.1)',
                    tension: 0.4,
                    fill: true
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: false
                    }
                },
                scales: {
                    y: {
                        beginAtZero: false,
                        ticks: {
                            color: '#94a3b8',
                            callback: function(value) {
                                return '$' + value.toLocaleString();
                            }
                        },
                        grid: {
                            color: 'rgba(148, 163, 184, 0.1)'
                        }
                    },
                    x: {
                        ticks: {
                            color: '#94a3b8'
                        },
                        grid: {
                            color: 'rgba(148, 163, 184, 0.1)'
                        }
                    }
                }
            }
        });
    }
    
    // Drawdown Chart
    const drawdownCtx = document.getElementById('drawdown-chart');
    if (drawdownCtx) {
        drawdownChart = new Chart(drawdownCtx, {
            type: 'line',
            data: {
                labels: [],
                datasets: [{
                    label: 'Max Drawdown',
                    data: [],
                    borderColor: '#ef4444',
                    backgroundColor: 'rgba(239, 68, 68, 0.1)',
                    tension: 0.4,
                    fill: true
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: false
                    }
                },
                scales: {
                    y: {
                        beginAtZero: false,
                        ticks: {
                            color: '#94a3b8',
                            callback: function(value) {
                                return (value * 100).toFixed(2) + '%';
                            }
                        },
                        grid: {
                            color: 'rgba(148, 163, 184, 0.1)'
                        }
                    },
                    x: {
                        ticks: {
                            color: '#94a3b8'
                        },
                        grid: {
                            color: 'rgba(148, 163, 184, 0.1)'
                        }
                    }
                }
            }
        });
    }
}

/**
 * Update charts with new data
 */
function updateCharts(metrics) {
    const timestamp = new Date(metrics.timestamp || Date.now()).toLocaleTimeString();
    
    // Update equity chart
    if (equityChart && metrics.equity !== undefined) {
        equityHistory.push({
            x: timestamp,
            y: metrics.equity
        });
        
        // Keep last 50 points
        if (equityHistory.length > 50) {
            equityHistory.shift();
        }
        
        equityChart.data.labels = equityHistory.map(d => d.x);
        equityChart.data.datasets[0].data = equityHistory.map(d => d.y);
        equityChart.update('none');
        
        // Hide empty message
        document.getElementById('equity-chart-empty').style.display = 'none';
    }
    
    // Update drawdown chart
    if (drawdownChart && metrics.max_drawdown !== undefined) {
        drawdownHistory.push({
            x: timestamp,
            y: metrics.max_drawdown
        });
        
        // Keep last 50 points
        if (drawdownHistory.length > 50) {
            drawdownHistory.shift();
        }
        
        drawdownChart.data.labels = drawdownHistory.map(d => d.x);
        drawdownChart.data.datasets[0].data = drawdownHistory.map(d => d.y);
        drawdownChart.update('none');
        
        // Hide empty message
        document.getElementById('drawdown-chart-empty').style.display = 'none';
        
        // Update drawdown rail status
        updateDrawdownRailStatus(metrics.max_drawdown > -0.10); // Active if DD > -10%
    }
    
    // Update regime guard (from capital_shield_mode or preset)
    if (metrics.capital_shield_mode) {
        updateRegimeGuardStatus(metrics.capital_shield_mode);
    } else if (metrics.preset) {
        const mode = metrics.preset === 'CONSERVATIVE' || metrics.preset === 'BALANCED' ? 'STRICT' : 'PERMISSIVE';
        updateRegimeGuardStatus(mode);
    }
}

/**
 * Add event to log
 */
function addEventLog(metrics) {
    const logEl = document.getElementById('events-log');
    const timestamp = new Date(metrics.timestamp || Date.now()).toLocaleTimeString();
    
    const eventItem = document.createElement('div');
    eventItem.className = 'event-item';
    eventItem.innerHTML = `
        <span class="event-time">${timestamp}</span>
        <span class="event-message">
            Equity: ${formatCurrency(metrics.equity || 0)} | 
            P&L: ${formatPercent(metrics.pnl_percent || 0)} | 
            DD: ${formatPercent(metrics.max_drawdown || 0)} | 
            Trades: ${metrics.trades || 0}
        </span>
    `;
    
    logEl.insertBefore(eventItem, logEl.firstChild);
    
    // Keep last 20 events
    while (logEl.children.length > 20) {
        logEl.removeChild(logEl.lastChild);
    }
}

/**
 * Show warning banner
 */
function showWarning(message) {
    const banner = document.getElementById('warning-banner');
    const text = document.getElementById('warning-text');
    text.textContent = message;
    banner.classList.remove('hidden');
    
    // Auto-hide after 5 seconds
    setTimeout(() => {
        banner.classList.add('hidden');
    }, 5000);
}

/**
 * Format helpers
 */
function formatCurrency(value) {
    return '$' + value.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
}

function formatPercent(value) {
    return (value * 100).toFixed(2) + '%';
}

function formatNumber(value) {
    return value.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
}

function formatUptime(seconds) {
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    const secs = seconds % 60;
    
    if (hours > 0) {
        return `${hours}h ${minutes}m`;
    } else if (minutes > 0) {
        return `${minutes}m ${secs}s`;
    } else {
        return `${secs}s`;
    }
}

// Initialize on load
document.addEventListener('DOMContentLoaded', init);

