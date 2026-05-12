let currentTab = 'mktxp';
let expandedRouters = new Set();
let editingRouterName = null;

const BOOLEAN_KEYS = [
    'enabled', 'module_only', 'use_ssl', 'no_ssl_certificate', 'ssl_certificate_verify',
    'ssl_check_hostname', 'plaintext_login', 'health', 'installed_packages', 'dhcp',
    'dhcp_lease', 'connections', 'connection_stats', 'connection_stats_destinations',
    'interface', 'routerboard', 'wireguard_peers', 'bridge_vlan', 'route', 'pool',
    'firewall', 'neighbor', 'dns', 'ipv6_route', 'ipv6_pool', 'ipv6_firewall',
    'ipv6_neighbor', 'poe', 'monitor', 'netwatch', 'public_ip', 'wireless',
    'wireless_clients', 'capsman', 'capsman_clients', 'w60g', 'eoip', 'gre', 'ipip',
    'lte', 'ipsec', 'switch_port', 'kid_control_assigned', 'kid_control_dynamic',
    'user', 'queue', 'bfd', 'bgp', 'routing_stats', 'certificate', 'container', 'check_for_updates'
];

function init() {
    renderVisualView();
    
    // Support Tab key in editor
    const editor = document.getElementById('config-editor');
    editor.addEventListener('keydown', function(e) {
        if (e.key === 'Tab') {
            e.preventDefault();
            const start = this.selectionStart;
            const end = this.selectionEnd;
            this.value = this.value.substring(0, start) + "    " + this.value.substring(end);
            this.selectionStart = this.selectionEnd = start + 4;
            onRawInput();
        }
    });
}

function switchTab(tab) {
    currentTab = tab;
    
    const mktxpBtn = document.getElementById('tab-mktxp');
    const systemBtn = document.getElementById('tab-_mktxp');
    const logsBtn = document.getElementById('tab-logs');
    
    const saveBtn = document.getElementById('save-btn');
    const restartBtn = document.getElementById('restart-btn');
    
    const visualSection = document.getElementById('visual-section');
    const rawSection = document.getElementById('raw-section');
    const logsSection = document.getElementById('logs-section');
    
    const title = document.querySelector('h1');
    const subtitle = document.querySelector('.subtitle');
    const filenameLabel = document.getElementById('filename-label');
    const configTypeInput = document.getElementById('config_type');
    const editor = document.getElementById('config-editor');

    // Reset all tabs and sections
    [mktxpBtn, systemBtn, logsBtn].forEach(btn => btn?.classList.remove('active'));
    [visualSection, rawSection, logsSection].forEach(sec => {
        if (sec) sec.style.display = 'none';
    });

    if (tab === 'logs') {
        title.innerText = 'MKTXP Activity Logs';
        subtitle.innerText = 'Real-time monitoring of exporter tasks and errors';
        logsBtn.classList.add('active');
        logsSection.style.display = 'flex';
        saveBtn.style.display = 'none'; // Hide Save on Logs
        fetchLogs();
    } else if (tab === 'mktxp') {
        title.innerText = 'Router Configuration';
        subtitle.innerText = 'Manage your Mikrotik device entries and metrics';
        mktxpBtn.classList.add('active');
        visualSection.style.display = 'flex';
        rawSection.style.display = 'flex';
        saveBtn.style.display = 'flex'; // Show Save
        filenameLabel.innerText = 'mktxp.conf';
        configTypeInput.value = 'mktxp';
        editor.value = mktxp_raw;
        syncRawToVisual();
        renderVisualView();
    } else {
        title.innerText = 'System Configuration';
        subtitle.innerText = 'Configure exporter settings and logging';
        systemBtn.classList.add('active');
        rawSection.style.display = 'flex';
        saveBtn.style.display = 'flex'; // Show Save
        filenameLabel.innerText = '_mktxp.conf';
        configTypeInput.value = '_mktxp';
        editor.value = system_raw;
    }

    // Re-trigger animations
    const contentStack = document.querySelector('.content-stack');
    if (contentStack) {
        contentStack.style.animation = 'none';
        contentStack.offsetHeight; 
        contentStack.style.animation = null;
    }
}

async function fetchLogs() {
    try {
        const response = await fetch('/logs');
        const text = await response.text();
        const logContent = document.getElementById('log-content');
        logContent.innerText = text || 'Waiting for logs...';
        logContent.parentElement.scrollTop = logContent.parentElement.scrollHeight;
    } catch (e) {
        console.error('Failed to fetch logs', e);
    }
}

// Auto-refresh logs if tab is active
setInterval(() => {
    if (document.getElementById('tab-logs').classList.contains('active')) {
        fetchLogs();
    }
}, 2000);

async function restartMKTXP() {
    if (!confirm('Are you sure you want to reload the configuration? This will briefly disconnect the Web UI.')) return;
    
    showToast('Reloading Config...');
    try {
        await fetch('/restart', { method: 'POST' });
        // Wait a bit and reload
        setTimeout(() => {
            window.location.reload();
        }, 2000);
    } catch (e) {
        showToast('Reload command sent');
        setTimeout(() => {
            window.location.reload();
        }, 3000);
    }
}

function onRawInput() {
    // Only sync if we're on the router tab
    if (currentTab === 'mktxp') {
        syncRawToVisual();
        renderVisualView();
    }
}

function syncRawToVisual() {
    const rawText = document.getElementById('config-editor').value;
    const lines = rawText.split('\n');
    let currentSection = null;
    const newData = {};

    lines.forEach(line => {
        const trimmed = line.trim();
        if (!trimmed || trimmed.startsWith('#')) return;

        if (trimmed.startsWith('[') && trimmed.endsWith(']')) {
            currentSection = trimmed.substring(1, trimmed.length - 1);
            newData[currentSection] = {};
        } else if (currentSection && trimmed.includes('=')) {
            let [key, ...valueParts] = trimmed.split('=');
            let value = valueParts.join('=').split('#')[0].trim();
            key = key.trim();

            if ((value.startsWith("'") && value.endsWith("'")) || (value.startsWith('"') && value.endsWith('"'))) {
                value = value.substring(1, value.length - 1);
            }

            newData[currentSection][key] = value;
        }
    });

    // Replace data
    Object.keys(MKTXP_DATA).forEach(k => delete MKTXP_DATA[k]);
    Object.assign(MKTXP_DATA, newData);
}

function syncVisualToRaw() {
    let content = '';

    const sortedKeys = Object.keys(MKTXP_DATA).sort((a, b) => {
        if (a === 'default') return -1;
        if (b === 'default') return 1;
        return a.localeCompare(b);
    });

    sortedKeys.forEach(section => {
        content += `[${section}]\n`;
        Object.entries(MKTXP_DATA[section]).forEach(([key, val]) => {
            content += `    ${key} = ${val}\n`;
        });
        content += '\n';
    });

    document.getElementById('config-editor').value = content;
}

function renderVisualView() {
    const container = document.getElementById('router-cards');
    container.innerHTML = '';

    if (currentTab !== 'mktxp') return;

    const sortedKeys = Object.keys(MKTXP_DATA).sort((a, b) => {
        if (a === 'default') return -1;
        if (b === 'default') return 1;
        return a.localeCompare(b);
    });

    sortedKeys.forEach(name => {
        const card = document.createElement('div');
        card.className = `router-card ${expandedRouters.has(name) ? 'expanded' : ''}`;

        const host = MKTXP_DATA[name].hostname || 'Inherited';
        const isDefault = name === 'default';
        const isEditing = editingRouterName === name;

        card.innerHTML = `
            <div class="router-card-header" onclick="toggleAccordion('${name}')">
                <div class="router-info">
                    ${isEditing ? `
                        <input type="text" class="inline-rename-input" value="${name}" 
                               onclick="event.stopPropagation()" 
                               onblur="finishRename('${name}', this.value)"
                               onkeydown="if(event.key==='Enter') this.blur()">
                    ` : `
                        <div class="router-name">${name}</div>
                        ${isDefault ? '' : `
                            <div class="header-actions">
                                <button class="btn-icon edit-pencil" title="Rename Router" onclick="event.stopPropagation(); startRename('${name}')">
                                    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M11 4H4a2 2 0 00-2 2v14a2 2 0 002 2h14a2 2 0 002-2v-7"></path><path d="M18.5 2.5a2.121 2.121 0 113 3L12 15l-4 1 1-4 9.5-9.5z"></path></svg>
                                </button>
                                <button class="btn-icon delete-btn" title="Remove Router" onclick="event.stopPropagation(); deleteRouter('${name}')">
                                    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="3 6 5 6 21 6"></polyline><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path></svg>
                                </button>
                            </div>
                        `}
                    `}
                    <div class="router-host">${host}</div>
                </div>
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <polyline points="6 9 12 15 18 9"></polyline>
                </svg>
            </div>
            <div class="router-card-body">
                ${renderSettings(name)}
            </div>
        `;
        container.appendChild(card);

        if (isEditing) {
            const input = card.querySelector('.inline-rename-input');
            input.focus();
            input.select();
        }
    });
}

function deleteRouter(name) {
    if (name === 'default') return;
    if (confirm(`Are you sure you want to remove [${name}]?`)) {
        delete MKTXP_DATA[name];
        expandedRouters.delete(name);
        syncVisualToRaw();
        renderVisualView();
    }
}

function addDevice() {
    let name = 'new_router';
    let counter = 1;
    while (MKTXP_DATA[name]) {
        name = `new_router_${counter++}`;
    }

    // Create new router with basic defaults
    MKTXP_DATA[name] = {
        'hostname': '192.168.88.1',
        'username': 'admin',
        'password': '',
        'enabled': 'True'
    };

    editingRouterName = name;
    expandedRouters.add(name);
    syncVisualToRaw();
    renderVisualView();
}

function renameRouter(oldName, newName) {
    if (!newName || oldName === newName || newName === 'default') return;
    MKTXP_DATA[newName] = MKTXP_DATA[oldName];
    delete MKTXP_DATA[oldName];
    if (expandedRouters.has(oldName)) {
        expandedRouters.delete(oldName);
        expandedRouters.add(newName);
    }
    syncVisualToRaw();
    renderVisualView();
}

function startRename(name) {
    editingRouterName = name;
    renderVisualView();
}

function finishRename(oldName, newName) {
    editingRouterName = null;
    if (newName && newName !== oldName && newName !== 'default') {
        renameRouter(oldName, newName);
    } else {
        renderVisualView();
    }
}

function toggleAccordion(name) {
    if (expandedRouters.has(name)) {
        expandedRouters.delete(name);
    } else {
        expandedRouters.add(name);
    }
    renderVisualView();
}

function renderSettings(routerName) {
    const data = MKTXP_DATA[routerName];
    const defaultData = MKTXP_DATA['default'] || {};
    const isDefaultSection = routerName === 'default';
    const connectionKeys = ['hostname', 'port', 'username', 'password', 'credentials_file', 'custom_labels', 'use_ssl'];

    let activeKeys = Object.keys(data);
    if (isDefaultSection) {
        activeKeys = Array.from(new Set([...connectionKeys, ...Object.keys(defaultData)]));
    }

    const groupConnection = activeKeys.filter(k => connectionKeys.includes(k));
    const groupMetrics = activeKeys.filter(k => !connectionKeys.includes(k));

    return `
        ${groupConnection.length > 0 ? `
        <div class="settings-group">
            <h4>Connection & Identity</h4>
            <div class="settings-grid">
                ${groupConnection.map(k => renderField(routerName, k)).join('')}
            </div>
        </div>` : ''}
        ${groupMetrics.length > 0 ? `
        <div class="settings-group">
            <h4>Metric Overrides</h4>
            <div class="settings-grid">
                ${groupMetrics.map(k => renderField(routerName, k)).join('')}
            </div>
        </div>` : ''}
        ${!isDefaultSection && activeKeys.length === 0 ? '<div style="padding: 1rem; color: var(--text-dim); font-size: 0.85rem;">No overrides set. Using all global settings.</div>' : ''}
        ${!isDefaultSection ? renderAddOverrideSection(routerName) : ''}
    `;
}

function renderAddOverrideSection(routerName) {
    const data = MKTXP_DATA[routerName];
    const defaultData = MKTXP_DATA['default'] || {};
    const availableKeys = Object.keys(defaultData).filter(k => !(k in data)).sort();
    if (availableKeys.length === 0) return '';
    return `
        <div class="add-override-section">
            <select class="override-select" onchange="addOverride('${routerName}', this.value)">
                <option value="">Add Override...</option>
                ${availableKeys.map(k => `<option value="${k}">${k}</option>`).join('')}
            </select>
        </div>
    `;
}

function addOverride(routerName, key) {
    if (!key) return;
    const defaultValue = MKTXP_DATA['default'][key] || '';
    MKTXP_DATA[routerName][key] = defaultValue;
    syncVisualToRaw();
    renderVisualView();
}

function renderField(routerName, key) {
    const val = MKTXP_DATA[routerName][key];
    const isInherited = !(key in MKTXP_DATA[routerName]);
    const isBool = BOOLEAN_KEYS.includes(key);
    const isDefaultSection = routerName === 'default';

    if (isBool) {
        const state = isInherited ? 'global' : (val === 'True' || val === true ? 'on' : 'off');
        return `
            <div class="setting-row">
                <span class="setting-label">${key}</span>
                <div class="input-wrapper">
                    <div class="tri-state">
                        <button class="tri-btn ${state === 'on' ? 'active on' : ''}" onclick="updateField('${routerName}', '${key}', 'True')">True</button>
                        <button class="tri-btn ${state === 'off' ? 'active off' : ''}" onclick="updateField('${routerName}', '${key}', 'False')">False</button>
                    </div>
                    ${(!isInherited && !isDefaultSection) ? `<button class="btn-icon" title="Reset to Global" onclick="updateField('${routerName}', '${key}', null)">
                        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M3 6h18m-2 0v14a2 2 0 01-2 2H7a2 2 0 01-2-2V6m3 0V4a2 2 0 012-2h4a2 2 0 012 2v2"></path></svg>
                    </button>` : ''}
                </div>
            </div>
        `;
    } else {
        const displayVal = isInherited ? '' : val;
        const placeholder = isDefaultSection ? 'Not set' : (MKTXP_DATA['default'] && MKTXP_DATA['default'][key]) || 'Global Default';
        return `
            <div class="setting-row">
                <span class="setting-label">${key}</span>
                <div class="input-wrapper">
                    <input type="${key === 'password' ? 'password' : 'text'}" 
                           value="${displayVal}" 
                           placeholder="${placeholder}"
                           onchange="updateField('${routerName}', '${key}', this.value)">
                    ${(!isInherited && !isDefaultSection) ? `<button class="btn-icon" title="Reset to Global" onclick="updateField('${routerName}', '${key}', null)">
                        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M3 6h18m-2 0v14a2 2 0 01-2 2H7a2 2 0 01-2-2V6m3 0V4a2 2 0 012-2h4a2 2 0 012 2v2"></path></svg>
                    </button>` : ''}
                </div>
            </div>
        `;
    }
}

function updateField(routerName, key, value) {
    if (value === null) {
        delete MKTXP_DATA[routerName][key];
    } else {
        MKTXP_DATA[routerName][key] = value;
    }
    syncVisualToRaw();
    renderVisualView();
}

function saveConfig() {
    const form = document.getElementById('config-form');
    const formData = new FormData(form);
    const params = new URLSearchParams(formData);

    fetch('/save', {
        method: 'POST',
        body: params
    })
        .then(response => {
            if (response.ok) {
                showToast('Configuration saved successfully!');
            } else {
                showToast('Error saving configuration', true);
            }
        })
        .catch(error => {
            showToast('Error: ' + error.message, true);
        });
}

function showToast(message, isError = false) {
    const toast = document.getElementById('toast');
    toast.innerText = message;
    toast.style.background = isError ? 'var(--danger)' : 'var(--accent)';
    toast.classList.add('show');
    setTimeout(() => toast.classList.remove('show'), 3000);
}

document.addEventListener('DOMContentLoaded', init);
