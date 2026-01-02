/**
 * Document Generation Platform - Frontend Application
 * Forvis Mazars Tax & Legal, S.L.P.
 */

// ============================================================================
// Configuration
// ============================================================================

const API_BASE = window.location.origin;
const REFRESH_INTERVAL = 30000; // 30 seconds

// ============================================================================
// State Management
// ============================================================================

const AppState = {
    currentPlugin: null,
    schema: null,
    formData: {},
    listData: {},
    isLoading: false,

    setPlugin(plugin) {
        this.currentPlugin = plugin;
        this.formData = {};
        this.listData = {};
    },

    setSchema(schema) {
        this.schema = schema;
    },

    setFormValue(fieldName, value) {
        this.formData[fieldName] = value;
    },

    getFormValue(fieldName) {
        return this.formData[fieldName];
    },

    getListItems(fieldName) {
        if (!this.listData[fieldName]) {
            this.listData[fieldName] = [];
        }
        return this.listData[fieldName];
    },

    addListItem(fieldName, item) {
        if (!this.listData[fieldName]) {
            this.listData[fieldName] = [];
        }
        this.listData[fieldName].push({ ...item, _id: Date.now() });
    },

    removeListItem(fieldName, index) {
        if (this.listData[fieldName]) {
            this.listData[fieldName].splice(index, 1);
        }
    },

    updateListItem(fieldName, index, key, value) {
        if (this.listData[fieldName] && this.listData[fieldName][index]) {
            this.listData[fieldName][index][key] = value;
        }
    },

    getAllData() {
        const data = { ...this.formData };
        // Add list data
        for (const [fieldName, items] of Object.entries(this.listData)) {
            data[fieldName] = items.map(item => {
                const cleaned = {};
                for (const [k, v] of Object.entries(item)) {
                    if (!k.startsWith('_')) {
                        cleaned[k] = v;
                    }
                }
                // Flatten simple text lists: if item only has 'value' key, extract the value
                const keys = Object.keys(cleaned);
                if (keys.length === 1 && keys[0] === 'value') {
                    return cleaned.value;
                }
                return cleaned;
            });
        }
        return data;
    },

    clearAll() {
        this.formData = {};
        this.listData = {};
    }
};

// ============================================================================
// API Functions
// ============================================================================

async function apiCall(endpoint, options = {}) {
    const url = `${API_BASE}${endpoint}`;
    const defaultOptions = {
        headers: {
            'Content-Type': 'application/json',
        },
    };

    try {
        const response = await fetch(url, { ...defaultOptions, ...options });
        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.error || data.detail || 'API Error');
        }

        return data;
    } catch (error) {
        console.error('API Error:', error);
        throw error;
    }
}

async function checkApiHealth() {
    try {
        const data = await apiCall('/health');
        updateApiStatus(true);
        return true;
    } catch (error) {
        updateApiStatus(false);
        return false;
    }
}

async function loadPlugins() {
    try {
        const data = await apiCall('/plugins');
        return data.plugins;
    } catch (error) {
        showNotification('error', 'Failed to load plugins', error.message);
        return [];
    }
}

async function loadPluginSchema(pluginId) {
    try {
        const data = await apiCall(`/plugins/${pluginId}/schema`);
        return data;
    } catch (error) {
        showNotification('error', 'Failed to load schema', error.message);
        return null;
    }
}

async function validateData(pluginId, data) {
    try {
        const result = await apiCall(`/plugins/${pluginId}/validate`, {
            method: 'POST',
            body: JSON.stringify({ data }),
        });
        return result;
    } catch (error) {
        showNotification('error', 'Validation failed', error.message);
        return { is_valid: false, errors: [error.message] };
    }
}

async function generateDocument(pluginId, data) {
    try {
        const result = await apiCall(`/plugins/${pluginId}/generate`, {
            method: 'POST',
            body: JSON.stringify({
                data,
                validate: true,
                strict_validation: false,
                apply_cell_colors: true,
            }),
        });
        return result;
    } catch (error) {
        showNotification('error', 'Generation failed', error.message);
        return { success: false, error: error.message };
    }
}

// ============================================================================
// UI Functions
// ============================================================================

function updateApiStatus(connected) {
    const statusDot = document.querySelector('.status-dot');
    const statusText = document.querySelector('.status-text');

    if (connected) {
        statusDot.classList.add('connected');
        statusDot.classList.remove('disconnected');
        statusText.textContent = 'Connected';
    } else {
        statusDot.classList.remove('connected');
        statusDot.classList.add('disconnected');
        statusText.textContent = 'Disconnected';
    }
}

function showLoading(text = 'Processing...') {
    const overlay = document.getElementById('loading-overlay');
    const loadingText = document.getElementById('loading-text');
    loadingText.textContent = text;
    overlay.classList.remove('hidden');
    AppState.isLoading = true;
}

function hideLoading() {
    const overlay = document.getElementById('loading-overlay');
    overlay.classList.add('hidden');
    AppState.isLoading = false;
}

function showNotification(type, title, message) {
    const area = document.getElementById('notification-area');

    const icons = {
        success: '✓',
        warning: '⚠',
        error: '✕',
        info: 'ℹ',
    };

    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.innerHTML = `
        <span class="notification-icon">${icons[type]}</span>
        <div class="notification-content">
            <div class="notification-title">${title}</div>
            <div class="notification-message">${message}</div>
        </div>
        <button class="notification-close" onclick="this.parentElement.remove()">✕</button>
    `;

    area.appendChild(notification);

    // Auto-remove after 5 seconds
    setTimeout(() => {
        if (notification.parentElement) {
            notification.remove();
        }
    }, 5000);
}

function clearNotifications() {
    const area = document.getElementById('notification-area');
    area.innerHTML = '';
}

// ============================================================================
// Form Rendering
// ============================================================================

function renderForm(schema) {
    const container = document.getElementById('form-container');
    container.innerHTML = '';

    if (!schema || !schema.fields) {
        container.innerHTML = `
            <div class="form-placeholder">
                <div class="placeholder-icon">❌</div>
                <h2>Failed to Load Form</h2>
                <p>Could not load the form schema. Please try again.</p>
            </div>
        `;
        return;
    }

    AppState.setSchema(schema);

    // Group fields by sections
    if (schema.ui_sections && schema.ui_sections.length > 0) {
        schema.ui_sections.forEach((section, idx) => {
            const sectionEl = renderSection(section, schema.fields, idx === 0);
            container.appendChild(sectionEl);
        });
    } else {
        // Render all fields flat
        const sectionEl = document.createElement('div');
        sectionEl.className = 'form-section';

        const content = document.createElement('div');
        content.className = 'section-content';

        schema.fields.forEach(field => {
            const fieldEl = renderField(field);
            if (fieldEl) {
                content.appendChild(fieldEl);
            }
        });

        sectionEl.appendChild(content);
        container.appendChild(sectionEl);
    }

    // Enable action buttons
    document.getElementById('btn-validate').disabled = false;
    document.getElementById('btn-generate').disabled = false;
}

function renderSection(section, allFields, expanded = true) {
    const sectionEl = document.createElement('div');
    sectionEl.className = 'form-section';
    sectionEl.dataset.sectionId = section.id;
    sectionEl.dataset.condition = section.condition || '';

    const header = document.createElement('div');
    header.className = 'section-header';
    header.innerHTML = `
        <span class="section-toggle ${expanded ? '' : 'collapsed'}">▼</span>
        <h3 class="section-title">${section.label}</h3>
    `;

    header.addEventListener('click', () => {
        const toggle = header.querySelector('.section-toggle');
        const content = sectionEl.querySelector('.section-content');
        toggle.classList.toggle('collapsed');
        content.classList.toggle('collapsed');
    });

    const content = document.createElement('div');
    content.className = `section-content ${expanded ? '' : 'collapsed'}`;

    // Find and render fields for this section
    const sectionFieldNames = section.fields || [];
    sectionFieldNames.forEach(fieldName => {
        const fieldDef = allFields.find(f => f.name === fieldName);
        if (fieldDef) {
            const fieldEl = renderField(fieldDef);
            if (fieldEl) {
                content.appendChild(fieldEl);
            }
        }
    });

    sectionEl.appendChild(header);
    sectionEl.appendChild(content);

    return sectionEl;
}

function renderField(field) {
    const group = document.createElement('div');
    group.className = 'form-group';
    group.dataset.fieldName = field.name;
    group.dataset.condition = field.condition || '';

    // Check if it's a wide field
    if (field.multiline || field.type === 'list') {
        group.classList.add('full-width');
    }

    const label = document.createElement('label');
    label.className = 'form-label';
    label.innerHTML = `${field.label}${field.required ? '<span class="required">*</span>' : ''}`;

    let input;

    switch (field.type) {
        case 'text':
            if (field.multiline) {
                input = document.createElement('textarea');
                input.className = 'textarea-input';
                input.rows = 4;
            } else {
                input = document.createElement('input');
                input.type = 'text';
                input.className = 'form-input';
            }
            input.name = field.name;
            input.placeholder = field.description || '';
            input.addEventListener('input', (e) => {
                AppState.setFormValue(field.name, e.target.value);
            });
            break;

        case 'date':
            const dateWrapper = document.createElement('div');
            dateWrapper.className = 'date-input';
            input = document.createElement('input');
            input.type = 'date';
            input.className = 'form-input';
            input.name = field.name;
            input.addEventListener('change', (e) => {
                AppState.setFormValue(field.name, e.target.value);
            });
            dateWrapper.appendChild(input);
            input = dateWrapper;
            break;

        case 'currency':
        case 'decimal':
        case 'int':
            const currencyWrapper = document.createElement('div');
            currencyWrapper.className = 'currency-input';
            const numInput = document.createElement('input');
            numInput.type = 'number';
            numInput.className = 'form-input';
            numInput.name = field.name;
            numInput.step = field.type === 'int' ? '1' : '0.01';
            numInput.addEventListener('input', (e) => {
                const value = field.type === 'int' ? parseInt(e.target.value) : parseFloat(e.target.value);
                AppState.setFormValue(field.name, isNaN(value) ? null : value);
            });
            currencyWrapper.appendChild(numInput);
            if (field.type === 'currency') {
                const symbol = document.createElement('span');
                symbol.className = 'currency-symbol';
                symbol.textContent = '€';
                currencyWrapper.appendChild(symbol);
            }
            input = currencyWrapper;
            break;

        case 'enum':
            input = document.createElement('select');
            input.className = 'select-input';
            input.name = field.name;

            // Add empty option
            const emptyOpt = document.createElement('option');
            emptyOpt.value = '';
            emptyOpt.textContent = '-- Select --';
            input.appendChild(emptyOpt);

            // Add options
            const options = field.values || [];
            options.forEach(opt => {
                const option = document.createElement('option');
                if (typeof opt === 'object') {
                    option.value = opt.value;
                    option.textContent = opt.label || opt.value;
                } else {
                    option.value = opt;
                    option.textContent = opt;
                }
                input.appendChild(option);
            });

            input.addEventListener('change', (e) => {
                let value = e.target.value;
                // Try to parse as number if it looks like one
                if (/^\d+$/.test(value)) {
                    value = parseInt(value);
                }
                AppState.setFormValue(field.name, value);
                updateConditionalVisibility();
            });
            break;

        case 'bool':
            const checkWrapper = document.createElement('div');
            checkWrapper.className = 'checkbox-group';
            const checkItem = document.createElement('label');
            checkItem.className = 'checkbox-item';
            const checkbox = document.createElement('input');
            checkbox.type = 'checkbox';
            checkbox.name = field.name;
            checkbox.addEventListener('change', (e) => {
                AppState.setFormValue(field.name, e.target.checked);
            });
            checkItem.appendChild(checkbox);
            checkItem.appendChild(document.createTextNode(' Yes'));
            checkWrapper.appendChild(checkItem);
            input = checkWrapper;
            break;

        case 'list':
            input = renderDynamicList(field);
            break;

        default:
            input = document.createElement('input');
            input.type = 'text';
            input.className = 'form-input';
            input.name = field.name;
            input.addEventListener('input', (e) => {
                AppState.setFormValue(field.name, e.target.value);
            });
    }

    group.appendChild(label);
    if (input) {
        group.appendChild(input);
    }

    if (field.description && field.type !== 'text') {
        const hint = document.createElement('span');
        hint.className = 'form-hint';
        hint.textContent = field.description;
        group.appendChild(hint);
    }

    return group;
}

function renderDynamicList(field) {
    const container = document.createElement('div');
    container.className = 'dynamic-list';
    container.dataset.fieldName = field.name;

    const header = document.createElement('div');
    header.className = 'dynamic-list-header';
    header.innerHTML = `<span class="dynamic-list-title">${field.label}</span>`;

    const itemsContainer = document.createElement('div');
    itemsContainer.className = 'dynamic-list-items';
    itemsContainer.id = `list-items-${field.name}`;

    const addBtn = document.createElement('button');
    addBtn.type = 'button';
    addBtn.className = 'btn btn-outline btn-add-item';
    addBtn.innerHTML = `<span class="btn-icon">+</span> Add Item`;
    addBtn.addEventListener('click', () => {
        addListItem(field);
    });

    container.appendChild(header);
    container.appendChild(itemsContainer);
    container.appendChild(addBtn);

    return container;
}

function addListItem(field) {
    const itemsContainer = document.getElementById(`list-items-${field.name}`);
    const items = AppState.getListItems(field.name);
    const index = items.length;

    // Create new item data
    const newItem = {};
    if (field.item_schema) {
        for (const [subName, subDef] of Object.entries(field.item_schema)) {
            newItem[subName] = subDef.default || '';
        }
    } else {
        newItem.value = '';
    }

    AppState.addListItem(field.name, newItem);

    // Render the item
    const itemEl = renderListItem(field, index);
    itemsContainer.appendChild(itemEl);
}

function renderListItem(field, index) {
    const item = document.createElement('div');
    item.className = 'dynamic-list-item';
    item.dataset.index = index;

    const content = document.createElement('div');
    content.className = 'item-content';

    if (field.item_schema) {
        // Complex object
        for (const [subName, subDef] of Object.entries(field.item_schema)) {
            const subGroup = document.createElement('div');
            subGroup.className = 'form-group';

            const subLabel = document.createElement('label');
            subLabel.className = 'form-label';
            subLabel.textContent = subDef.label || subName;

            let subInput;
            if (subDef.type === 'currency' || subDef.type === 'decimal') {
                subInput = document.createElement('input');
                subInput.type = 'number';
                subInput.step = '0.01';
            } else if (subDef.type === 'bool') {
                subInput = document.createElement('input');
                subInput.type = 'checkbox';
            } else {
                subInput = document.createElement('input');
                subInput.type = 'text';
            }

            subInput.className = 'form-input';
            subInput.dataset.fieldName = field.name;
            subInput.dataset.index = index;
            subInput.dataset.subField = subName;

            subInput.addEventListener('input', (e) => {
                let value = e.target.type === 'checkbox' ? e.target.checked : e.target.value;
                if (e.target.type === 'number') {
                    value = parseFloat(value) || 0;
                }
                AppState.updateListItem(field.name, index, subName, value);
            });

            subGroup.appendChild(subLabel);
            subGroup.appendChild(subInput);
            content.appendChild(subGroup);
        }
    } else {
        // Simple text list
        const input = document.createElement('input');
        input.type = 'text';
        input.className = 'form-input';
        input.placeholder = 'Enter value...';
        input.dataset.fieldName = field.name;
        input.dataset.index = index;
        input.addEventListener('input', (e) => {
            AppState.updateListItem(field.name, index, 'value', e.target.value);
        });
        content.appendChild(input);
    }

    const removeBtn = document.createElement('button');
    removeBtn.type = 'button';
    removeBtn.className = 'btn-remove';
    removeBtn.innerHTML = '✕';
    removeBtn.addEventListener('click', () => {
        AppState.removeListItem(field.name, index);
        refreshListItems(field);
    });

    item.appendChild(content);
    item.appendChild(removeBtn);

    return item;
}

function refreshListItems(field) {
    const itemsContainer = document.getElementById(`list-items-${field.name}`);
    const items = AppState.getListItems(field.name);

    itemsContainer.innerHTML = '';
    items.forEach((_, index) => {
        const itemEl = renderListItem(field, index);
        itemsContainer.appendChild(itemEl);
    });
}

function updateConditionalVisibility() {
    const formData = AppState.getAllData();

    // Check sections
    document.querySelectorAll('.form-section[data-condition]').forEach(section => {
        const condition = section.dataset.condition;
        if (condition) {
            const visible = evaluateCondition(condition, formData);
            section.style.display = visible ? '' : 'none';
        }
    });

    // Check fields
    document.querySelectorAll('.form-group[data-condition]').forEach(group => {
        const condition = group.dataset.condition;
        if (condition) {
            const visible = evaluateCondition(condition, formData);
            group.style.display = visible ? '' : 'none';
        }
    });
}

function evaluateCondition(condition, data) {
    if (!condition) return true;

    try {
        // Parse simple conditions like "master_file == 1"
        const match = condition.match(/(\w+)\s*==\s*(\S+)/);
        if (match) {
            const [, field, expectedStr] = match;
            const actual = data[field];

            // Try to parse expected value
            let expected;
            if (expectedStr === 'true') expected = true;
            else if (expectedStr === 'false') expected = false;
            else if (/^\d+$/.test(expectedStr)) expected = parseInt(expectedStr);
            else expected = expectedStr.replace(/^["']|["']$/g, '');

            return actual === expected;
        }
    } catch (e) {
        console.warn('Failed to evaluate condition:', condition, e);
    }

    return true;
}

// ============================================================================
// Results Rendering
// ============================================================================

function showResults(result) {
    const panel = document.getElementById('results-panel');
    const content = document.getElementById('results-content');

    panel.classList.remove('hidden');

    if (result.success) {
        const filename = result.output_path ? result.output_path.split('/').pop() : 'document.docx';

        content.innerHTML = `
            <div class="result-success">
                <div class="success-icon">✓</div>
                <h4>Document Generated Successfully!</h4>
                <p>Your document has been created and is ready for download.</p>
                <a href="${API_BASE}/download/${filename}" class="btn btn-primary download-btn" download>
                    <span class="btn-icon">📥</span>
                    Download Document
                </a>
                <div class="trace-info">
                    <p>Trace ID: <span class="trace-id">${result.trace_id || 'N/A'}</span></p>
                    <p>Duration: ${result.duration_ms || 0}ms</p>
                </div>
            </div>
            ${renderDecisionTrace(result.decision_traces)}
        `;
    } else {
        content.innerHTML = `
            <div class="result-error">
                <h4 style="color: var(--danger);">Generation Failed</h4>
                <p>${result.error || 'An unknown error occurred'}</p>
                ${result.validation ? renderValidationErrors(result.validation) : ''}
            </div>
        `;
    }
}

function renderDecisionTrace(traces) {
    if (!traces || traces.length === 0) return '';

    let html = `
        <div class="decision-trace">
            <div class="decision-trace-title" onclick="this.nextElementSibling.classList.toggle('hidden')">
                ▶ Decision Trace (click to expand)
            </div>
            <div class="hidden">
    `;

    traces.forEach(trace => {
        html += `
            <div class="decision-item">
                <div class="decision-name">${trace.decision_name}</div>
                ${trace.rule_hits.map(hit => `
                    <div class="rule-hit ${hit.condition_met ? 'met' : 'not-met'}">
                        ${hit.condition_met ? '✓' : '○'} ${hit.rule_id}: ${hit.rule_name}
                    </div>
                `).join('')}
            </div>
        `;
    });

    html += '</div></div>';
    return html;
}

function renderValidationErrors(validation) {
    if (!validation.errors || validation.errors.length === 0) return '';

    return `
        <div class="validation-errors mt-lg">
            <h5>Validation Errors:</h5>
            <ul>
                ${validation.errors.map(e => `<li style="color: var(--danger)">${e}</li>`).join('')}
            </ul>
        </div>
    `;
}

function hideResults() {
    const panel = document.getElementById('results-panel');
    panel.classList.add('hidden');
}

// ============================================================================
// Plugin Info Update
// ============================================================================

function updatePluginInfo(plugin) {
    const infoPanel = document.getElementById('plugin-info');
    const nameEl = document.getElementById('plugin-name');
    const descEl = document.getElementById('plugin-description');
    const versionEl = document.getElementById('plugin-version');
    const langEl = document.getElementById('plugin-language');

    nameEl.textContent = plugin.name;
    descEl.textContent = plugin.description || 'No description available.';
    versionEl.textContent = plugin.version || '1.0.0';
    langEl.textContent = plugin.language || 'es';

    infoPanel.classList.remove('hidden');
}

// ============================================================================
// Sample Data
// ============================================================================

function loadSampleData() {
    const sampleData = {
        fecha_fin_fiscal: '2025-12-31',
        entidad_cliente: 'Empresa Ejemplo S.L.',
        master_file: 0,
        descripcion_actividad: 'La Compañía se dedica a la prestación de servicios de consultoría empresarial y asesoramiento estratégico a empresas del grupo multinacional.',
        contacto1: 'María García López',
        cargo_contacto1: 'Director',
        correo_contacto1: 'maria.garcia@forvismazars.es',
        contacto2: 'Carlos Rodríguez Martín',
        cargo_contacto2: 'Senior Manager',
        correo_contacto2: 'carlos.rodriguez@forvismazars.es',
        contacto3: 'Ana Fernández Ruiz',
        cargo_contacto3: 'Manager',
        correo_contacto3: 'ana.fernandez@forvismazars.es',
        cifra_1: 15000000,
        cifra_0: 14200000,
        ebit_1: 2250000,
        ebit_0: 2130000,
        resultado_fin_1: -75000,
        resultado_fin_0: -68000,
        ebt_1: 2175000,
        ebt_0: 2062000,
        resultado_net_1: 1631250,
        resultado_net_0: 1546500,
        cumplimiento_resumen_local_1: 'si',
        cumplimiento_resumen_local_2: 'si',
        cumplimiento_resumen_local_3: 'si',
    };

    // Add risk fields
    for (let i = 1; i <= 12; i++) {
        sampleData[`impacto_${i}`] = 'no';
        sampleData[`afectacion_pre_${i}`] = 'bajo';
        sampleData[`afectacion_final_${i}`] = 'bajo';
    }

    // Add compliance fields
    for (let i = 1; i <= 14; i++) {
        sampleData[`cumplido_local_${i}`] = 'si';
    }

    // Populate form with sample data
    AppState.formData = sampleData;

    // Update form inputs
    for (const [key, value] of Object.entries(sampleData)) {
        const input = document.querySelector(`[name="${key}"]`);
        if (input) {
            if (input.type === 'checkbox') {
                input.checked = Boolean(value);
            } else {
                input.value = value;
            }
        }
    }

    // Add sample list items
    AppState.listData.documentacion_facilitada = [
        { value: 'Local File ejercicio 2024', _id: 1 },
        { value: 'Estados Financieros auditados 2024', _id: 2 },
    ];

    AppState.listData.servicios_vinculados = [
        {
            servicio_vinculado: 'Servicios de gestión',
            entidades_vinculadas: [],
            _id: 1
        }
    ];

    // Refresh list displays
    const schema = AppState.schema;
    if (schema) {
        schema.fields.forEach(field => {
            if (field.type === 'list') {
                refreshListItems(field);
            }
        });
    }

    updateConditionalVisibility();
    showNotification('success', 'Sample Data Loaded', 'Form has been populated with sample data.');
}

function exportAsJson() {
    const data = AppState.getAllData();
    const json = JSON.stringify(data, null, 2);
    const blob = new Blob([json], { type: 'application/json' });
    const url = URL.createObjectURL(blob);

    const a = document.createElement('a');
    a.href = url;
    a.download = `${AppState.currentPlugin || 'form'}_data.json`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);

    showNotification('success', 'Export Complete', 'Form data has been exported as JSON.');
}

// ============================================================================
// Event Handlers
// ============================================================================

async function handlePluginChange(pluginId) {
    if (!pluginId) {
        document.getElementById('form-container').innerHTML = `
            <div class="form-placeholder">
                <div class="placeholder-icon">📋</div>
                <h2>Select a Plugin to Begin</h2>
                <p>Choose a document type from the sidebar to load the input form.</p>
            </div>
        `;
        document.getElementById('plugin-info').classList.add('hidden');
        document.getElementById('btn-validate').disabled = true;
        document.getElementById('btn-generate').disabled = true;
        return;
    }

    showLoading('Loading plugin schema...');

    try {
        // Get plugin info
        const plugins = await loadPlugins();
        const plugin = plugins.find(p => p.plugin_id === pluginId);

        if (plugin) {
            updatePluginInfo(plugin);
        }

        // Get schema
        const schema = await loadPluginSchema(pluginId);

        if (schema) {
            AppState.setPlugin(pluginId);
            renderForm(schema);
            showNotification('success', 'Plugin Loaded', `${plugin?.name || pluginId} is ready.`);
        }
    } catch (error) {
        showNotification('error', 'Failed to Load Plugin', error.message);
    } finally {
        hideLoading();
    }
}

async function handleValidate() {
    if (!AppState.currentPlugin) {
        showNotification('warning', 'No Plugin Selected', 'Please select a plugin first.');
        return;
    }

    clearNotifications();
    showLoading('Validating...');

    try {
        const data = AppState.getAllData();
        const result = await validateData(AppState.currentPlugin, data);

        if (result.is_valid) {
            showNotification('success', 'Validation Passed', 'All fields are valid.');
        } else {
            result.errors.forEach(error => {
                showNotification('error', 'Validation Error', error);
            });
        }

        if (result.warnings && result.warnings.length > 0) {
            result.warnings.forEach(warning => {
                showNotification('warning', 'Warning', warning);
            });
        }
    } finally {
        hideLoading();
    }
}

async function handleGenerate() {
    if (!AppState.currentPlugin) {
        showNotification('warning', 'No Plugin Selected', 'Please select a plugin first.');
        return;
    }

    clearNotifications();
    hideResults();
    showLoading('Generating document...');

    try {
        const data = AppState.getAllData();
        const result = await generateDocument(AppState.currentPlugin, data);

        if (result.success) {
            showNotification('success', 'Document Generated', 'Your document is ready for download.');
        }

        showResults(result);
    } finally {
        hideLoading();
    }
}

function handleClear() {
    AppState.clearAll();

    // Clear all form inputs
    document.querySelectorAll('.form-input, .select-input, .textarea-input').forEach(input => {
        if (input.type === 'checkbox') {
            input.checked = false;
        } else {
            input.value = '';
        }
    });

    // Clear list items
    document.querySelectorAll('.dynamic-list-items').forEach(container => {
        container.innerHTML = '';
    });

    clearNotifications();
    hideResults();
    showNotification('info', 'Form Cleared', 'All fields have been reset.');
}

// ============================================================================
// Initialization
// ============================================================================

async function init() {
    // Check API health
    await checkApiHealth();

    // Set up periodic health check
    setInterval(checkApiHealth, REFRESH_INTERVAL);

    // Load plugins
    const plugins = await loadPlugins();
    const select = document.getElementById('plugin-select');

    select.innerHTML = '<option value="">-- Select Plugin --</option>';
    plugins.forEach(plugin => {
        const option = document.createElement('option');
        option.value = plugin.plugin_id;
        option.textContent = plugin.name;
        select.appendChild(option);
    });

    // Event listeners
    select.addEventListener('change', (e) => handlePluginChange(e.target.value));
    document.getElementById('btn-validate').addEventListener('click', handleValidate);
    document.getElementById('btn-generate').addEventListener('click', handleGenerate);
    document.getElementById('btn-clear').addEventListener('click', handleClear);
    document.getElementById('btn-load-sample').addEventListener('click', loadSampleData);
    document.getElementById('btn-export-json').addEventListener('click', exportAsJson);
    document.getElementById('btn-close-results').addEventListener('click', hideResults);

    // Modal close handlers
    document.querySelectorAll('.modal-close, .modal-cancel').forEach(btn => {
        btn.addEventListener('click', () => {
            document.getElementById('modal-backdrop').classList.add('hidden');
        });
    });

    console.log('Document Generation Platform initialized');
}

// Start the application
document.addEventListener('DOMContentLoaded', init);
