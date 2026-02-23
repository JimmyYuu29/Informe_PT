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
    comentariosData: null,  // Cached comentarios valorativos definitions
    isLoading: false,

    setPlugin(plugin) {
        this.currentPlugin = plugin;
        this.formData = {};
        this.listData = {};
        this.comentariosData = null;
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

async function loadComentariosValorativos(pluginId) {
    try {
        const data = await apiCall(`/plugins/${pluginId}/comentarios-valorativos`);
        AppState.comentariosData = data.comentarios;
        return data.comentarios;
    } catch (error) {
        console.warn('Failed to load comentarios valorativos:', error.message);
        return [];
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

    // Use specialized renderers for specific sections
    const sectionId = section.id || '';
    const sectionFieldNames = section.fields || [];

    if (sectionId === 'sec_financials') {
        const tableEl = renderFinancialDataTable(allFields);
        content.appendChild(tableEl);
    } else if (sectionId === 'sec_risks' || sectionFieldNames.includes('risk_elements')) {
        const tableEl = renderRiskTable(allFields);
        content.appendChild(tableEl);
    } else if (sectionId === 'sec_local_detail' || sectionFieldNames.includes('local_file_compliance')) {
        const tableEl = renderComplianceDetailTable('local', 14, allFields);
        content.appendChild(tableEl);
    } else if (sectionId === 'sec_master_detail' || sectionFieldNames.includes('master_file_compliance')) {
        const tableEl = renderComplianceDetailTable('mast', 17, allFields);
        content.appendChild(tableEl);
    } else if (sectionId === 'sec_compliance_local') {
        const tableEl = renderComplianceSummaryTable('local', 3, allFields);
        content.appendChild(tableEl);
    } else if (sectionId === 'sec_compliance_master') {
        const tableEl = renderComplianceSummaryTable('mast', 4, allFields);
        content.appendChild(tableEl);
    } else if (sectionId === 'sec_contacts') {
        const contactsEl = renderContactsSection(allFields);
        content.appendChild(contactsEl);
    } else if (sectionId === 'sec_operations') {
        // Render operaciones vinculadas with peso indicators and valoracion_oovv
        const operationsEl = renderOperacionesVinculadasSection(allFields);
        content.appendChild(operationsEl);
    } else if (sectionId === 'sec_anexo3') {
        // Render texto_anexo3 field first
        const textoAnexo3Field = allFields.find(f => f.name === 'texto_anexo3');
        if (textoAnexo3Field) {
            const fieldEl = renderField(textoAnexo3Field);
            if (fieldEl) {
                content.appendChild(fieldEl);
            }
        }
        // Then render comentarios valorativos section
        const comentariosEl = renderComentariosVlorativosSection();
        content.appendChild(comentariosEl);
    } else {
        // Default rendering
        sectionFieldNames.forEach(fieldName => {
            const fieldDef = allFields.find(f => f.name === fieldName);
            if (fieldDef) {
                const fieldEl = renderField(fieldDef);
                if (fieldEl) {
                    content.appendChild(fieldEl);
                }
            }
        });
    }

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

// ============================================================================
// Specialized Table Renderers (Matching Streamlit Layout)
// ============================================================================

function renderFinancialDataTable(allFields) {
    const container = document.createElement('div');
    container.className = 'form-table financial-table-3col';

    const financialRows = [
        { label: 'Cifra de negocios', field_1: 'cifra_1', field_0: 'cifra_0' },
        { label: 'EBIT', field_1: 'ebit_1', field_0: 'ebit_0' },
        { label: 'Resultado Financiero', field_1: 'resultado_fin_1', field_0: 'resultado_fin_0' },
        { label: 'EBT', field_1: 'ebt_1', field_0: 'ebt_0' },
        { label: 'Resultado Neto', field_1: 'resultado_net_1', field_0: 'resultado_net_0' },
    ];

    // Header - 3 data columns
    const header = document.createElement('div');
    header.className = 'form-table-header';
    header.innerHTML = `
        <span>Partidas Contables</span>
        <span>Variación (%)</span>
        <span>Ejercicio Actual (EUR)</span>
        <span>Ejercicio Anterior (EUR)</span>
    `;
    container.appendChild(header);

    // Data rows with inputs
    financialRows.forEach(row => {
        const rowEl = document.createElement('div');
        rowEl.className = 'form-table-row';
        rowEl.dataset.row = row.field_1;

        // Label column
        const labelCell = document.createElement('span');
        labelCell.className = 'form-table-cell label';
        labelCell.textContent = row.label;

        // Column 1: Variation (auto-calculated)
        const variationCell = document.createElement('span');
        variationCell.className = 'form-table-cell number calculated-value';
        variationCell.id = `variation-${row.field_1}`;
        variationCell.textContent = 'N/A';

        // Column 2: Ejercicio Actual input
        const currentCell = document.createElement('span');
        currentCell.className = 'form-table-cell';
        const currentInput = document.createElement('input');
        currentInput.type = 'number';
        currentInput.className = 'form-input';
        currentInput.name = row.field_1;
        currentInput.step = '0.01';
        currentInput.placeholder = '0.00';
        currentInput.addEventListener('input', (e) => {
            const value = parseFloat(e.target.value);
            AppState.setFormValue(row.field_1, isNaN(value) ? null : value);
            updateFinancialVariation(row.field_1, row.field_0);
            updateDerivedValues();
        });
        currentCell.appendChild(currentInput);

        // Column 3: Ejercicio Anterior input
        const priorCell = document.createElement('span');
        priorCell.className = 'form-table-cell';
        const priorInput = document.createElement('input');
        priorInput.type = 'number';
        priorInput.className = 'form-input';
        priorInput.name = row.field_0;
        priorInput.step = '0.01';
        priorInput.placeholder = '0.00';
        priorInput.addEventListener('input', (e) => {
            const value = parseFloat(e.target.value);
            AppState.setFormValue(row.field_0, isNaN(value) ? null : value);
            updateFinancialVariation(row.field_1, row.field_0);
            updateDerivedValues();
        });
        priorCell.appendChild(priorInput);

        rowEl.appendChild(labelCell);
        rowEl.appendChild(variationCell);
        rowEl.appendChild(currentCell);
        rowEl.appendChild(priorCell);
        container.appendChild(rowEl);
    });

    // Divider before derived rows
    const divider = document.createElement('div');
    divider.className = 'form-table-divider';
    container.appendChild(divider);

    // Caption for derived rows
    const caption = document.createElement('p');
    caption.className = 'caption-text';
    caption.textContent = 'Valores calculados automáticamente:';
    container.appendChild(caption);

    // Derived rows (calculated values - 2 additional rows)
    const derivedRows = [
        { label: 'Total costes operativos', id: 'derived-cost', unit: '€' },
        { label: 'Operating Margin (OM)', id: 'derived-om', unit: '%' },
        { label: 'Net Cost Plus (NCP)', id: 'derived-ncp', unit: '%' },
    ];

    derivedRows.forEach(row => {
        const rowEl = document.createElement('div');
        rowEl.className = 'form-table-row derived-row';

        // Label
        const labelCell = document.createElement('span');
        labelCell.className = 'form-table-cell label derived-label';
        labelCell.textContent = row.label;

        // Variation (calculated)
        const variationCell = document.createElement('span');
        variationCell.className = 'form-table-cell number derived-value';
        variationCell.id = `${row.id}-variation`;
        variationCell.textContent = 'N/A';

        // Current year (calculated)
        const currentCell = document.createElement('span');
        currentCell.className = 'form-table-cell number derived-value';
        currentCell.id = `${row.id}-1`;
        currentCell.textContent = row.unit === '€' ? '0,00 €' : '0,00 %';

        // Prior year (calculated)
        const priorCell = document.createElement('span');
        priorCell.className = 'form-table-cell number derived-value';
        priorCell.id = `${row.id}-0`;
        priorCell.textContent = row.unit === '€' ? '0,00 €' : '0,00 %';

        rowEl.appendChild(labelCell);
        rowEl.appendChild(variationCell);
        rowEl.appendChild(currentCell);
        rowEl.appendChild(priorCell);
        container.appendChild(rowEl);
    });

    return container;
}

function updateDerivedValues() {
    const cifra_1 = AppState.getFormValue('cifra_1') || 0;
    const cifra_0 = AppState.getFormValue('cifra_0') || 0;
    const ebit_1 = AppState.getFormValue('ebit_1') || 0;
    const ebit_0 = AppState.getFormValue('ebit_0') || 0;

    // Total costes operativos = Cifra de negocios - EBIT
    const cost_1 = cifra_1 - ebit_1;
    const cost_0 = cifra_0 - ebit_0;

    // Operating Margin (OM) = (EBIT / Cifra de negocios) * 100
    const om_1 = cifra_1 !== 0 ? (ebit_1 / cifra_1) * 100 : 0;
    const om_0 = cifra_0 !== 0 ? (ebit_0 / cifra_0) * 100 : 0;

    // Net Cost Plus (NCP) = (EBIT / Total costes operativos) * 100
    const ncp_1 = cost_1 !== 0 ? (ebit_1 / cost_1) * 100 : 0;
    const ncp_0 = cost_0 !== 0 ? (ebit_0 / cost_0) * 100 : 0;

    // Format currency (Spanish format)
    const formatCurrency = (val) => {
        return val.toLocaleString('es-ES', { minimumFractionDigits: 2, maximumFractionDigits: 2 }) + ' €';
    };

    // Format percentage
    const formatPercent = (val) => {
        return val.toLocaleString('es-ES', { minimumFractionDigits: 2, maximumFractionDigits: 2 }) + ' %';
    };

    // Calculate variation percentage
    const calcVariation = (v1, v0) => {
        if (v0 === 0) return 'N/A';
        const variation = ((v1 - v0) / Math.abs(v0)) * 100;
        const sign = variation >= 0 ? '+' : '';
        return `${sign}${variation.toLocaleString('es-ES', { minimumFractionDigits: 2, maximumFractionDigits: 2 })} %`;
    };

    // Update Total costes operativos
    const costEl1 = document.getElementById('derived-cost-1');
    const costEl0 = document.getElementById('derived-cost-0');
    const costVarEl = document.getElementById('derived-cost-variation');
    if (costEl1) costEl1.textContent = formatCurrency(cost_1);
    if (costEl0) costEl0.textContent = formatCurrency(cost_0);
    if (costVarEl) costVarEl.textContent = calcVariation(cost_1, cost_0);

    // Update Operating Margin
    const omEl1 = document.getElementById('derived-om-1');
    const omEl0 = document.getElementById('derived-om-0');
    const omVarEl = document.getElementById('derived-om-variation');
    if (omEl1) omEl1.textContent = formatPercent(om_1);
    if (omEl0) omEl0.textContent = formatPercent(om_0);
    if (omVarEl) omVarEl.textContent = calcVariation(om_1, om_0);

    // Update Net Cost Plus
    const ncpEl1 = document.getElementById('derived-ncp-1');
    const ncpEl0 = document.getElementById('derived-ncp-0');
    const ncpVarEl = document.getElementById('derived-ncp-variation');
    if (ncpEl1) ncpEl1.textContent = formatPercent(ncp_1);
    if (ncpEl0) ncpEl0.textContent = formatPercent(ncp_0);
    if (ncpVarEl) ncpVarEl.textContent = calcVariation(ncp_1, ncp_0);

    // Also update peso OOVV indicators when financial data changes
    updatePesoOOVVIndicators();
}

function updateFinancialVariation(field1, field0) {
    const val1 = AppState.getFormValue(field1) || 0;
    const val0 = AppState.getFormValue(field0) || 0;
    const variationEl = document.getElementById(`variation-${field1}`);

    if (variationEl) {
        if (val0 === 0) {
            variationEl.textContent = 'N/A';
        } else {
            const variation = ((val1 - val0) / Math.abs(val0)) * 100;
            variationEl.textContent = `${variation >= 0 ? '+' : ''}${variation.toFixed(2)}%`;
            variationEl.className = `form-table-cell number ${variation >= 0 ? 'positive' : 'negative'}`;
        }
    }
}

function renderRiskTable(allFields) {
    const container = document.createElement('div');
    container.className = 'risk-table-vertical';

    const riskLabels = [
        "Restructuraciones empresariales",
        "Valoración de transmisiones intragrupo de activos intangibles",
        "Pagos por cánones derivados de la cesión de intangibles",
        "Pagos por servicios intragrupo",
        "Existencia de pérdidas reiteradas",
        "Operaciones financieras entre partes vinculadas",
        "Estructuras funcionales de bajo riesgo, tanto en el ámbito de la fabricación como de la distribución",
        "Falta de declaración de ingresos intragrupo por las prestaciones de servicios o de cesiones de activos intangibles no repercutidos",
        "Erosión de bases imponibles causada por el establecimiento de estructuras en el exterior en las que se remanses beneficios que deben tributar en España",
        "Revisión de las formas societarias utilizadas para el desempeño de la actividad económica con el objetivo de verificar si se está produciendo una minoración improcedente de la correcta tributación de la actividad desarrollada o una traslación de bases imponibles negativas hacia entidades jurídicas sometidas a menores tipos",
        "Operaciones con establecimientos permanentes",
        "Peso de las operaciones vinculadas relevante",
    ];

    const impactoOptions = ['si', 'no', 'posible'];
    const afectacionOptions = ['bajo', 'medio', 'alto'];

    // Section title
    const title = document.createElement('h4');
    title.className = 'section-subheader';
    title.textContent = 'Evaluación de Riesgos';
    container.appendChild(title);

    // Render each risk item with vertical layout (like Streamlit)
    riskLabels.forEach((label, idx) => {
        const i = idx + 1;

        // Item container
        const itemContainer = document.createElement('div');
        itemContainer.className = 'risk-item-vertical';

        // Item header with number and label
        const itemHeader = document.createElement('div');
        itemHeader.className = 'risk-item-header';
        itemHeader.innerHTML = `<strong>${i}. ${label}</strong>`;
        itemContainer.appendChild(itemHeader);

        // Input row with vertical layout (like Streamlit) - each on its own row
        const inputRow = document.createElement('div');
        inputRow.className = 'risk-item-inputs-vertical';

        // Impacto
        const impactoGroup = document.createElement('div');
        impactoGroup.className = 'form-group-row';
        const impactoLabel = document.createElement('label');
        impactoLabel.className = 'form-label-inline';
        impactoLabel.textContent = 'Impacto';
        impactoGroup.appendChild(impactoLabel);
        const impactoSelect = createSelect(`impacto_${i}`, impactoOptions, 'no');
        impactoGroup.appendChild(impactoSelect);
        inputRow.appendChild(impactoGroup);

        // Afectacion Preliminar
        const afectPreGroup = document.createElement('div');
        afectPreGroup.className = 'form-group-row';
        const afectPreLabel = document.createElement('label');
        afectPreLabel.className = 'form-label-inline';
        afectPreLabel.textContent = 'Afectación Prelim.';
        afectPreGroup.appendChild(afectPreLabel);
        const afectPreSelect = createSelect(`afectacion_pre_${i}`, afectacionOptions, 'bajo');
        afectPreGroup.appendChild(afectPreSelect);
        inputRow.appendChild(afectPreGroup);

        // Mitigadores
        const mitigadoresGroup = document.createElement('div');
        mitigadoresGroup.className = 'form-group-row';
        const mitigadoresLabel = document.createElement('label');
        mitigadoresLabel.className = 'form-label-inline';
        mitigadoresLabel.textContent = 'Mitigadores';
        mitigadoresGroup.appendChild(mitigadoresLabel);
        const mitigadoresInput = document.createElement('input');
        mitigadoresInput.type = 'text';
        mitigadoresInput.className = 'form-input';
        mitigadoresInput.name = `texto_mitigacion_${i}`;
        mitigadoresInput.placeholder = 'Texto de mitigación...';
        mitigadoresInput.addEventListener('input', (e) => {
            AppState.setFormValue(`texto_mitigacion_${i}`, e.target.value);
        });
        mitigadoresGroup.appendChild(mitigadoresInput);
        inputRow.appendChild(mitigadoresGroup);

        // Afectacion Final
        const afectFinalGroup = document.createElement('div');
        afectFinalGroup.className = 'form-group-row';
        const afectFinalLabel = document.createElement('label');
        afectFinalLabel.className = 'form-label-inline';
        afectFinalLabel.textContent = 'Afectación Final';
        afectFinalGroup.appendChild(afectFinalLabel);
        const afectFinalSelect = createSelect(`afectacion_final_${i}`, afectacionOptions, 'bajo');
        afectFinalGroup.appendChild(afectFinalSelect);
        inputRow.appendChild(afectFinalGroup);

        itemContainer.appendChild(inputRow);

        // Divider between items
        const divider = document.createElement('hr');
        divider.className = 'risk-item-divider';
        itemContainer.appendChild(divider);

        container.appendChild(itemContainer);
    });

    return container;
}

function renderComplianceDetailTable(prefix, count, allFields) {
    const container = document.createElement('div');
    container.className = 'compliance-table-vertical';

    const localFileItems = [
        'Estructura organizativa del obligado tributario',
        'Descripción de las actividades de la entidad',
        'Principales competidores',
        'Funciones ejercidas y riesgos asumidos',
        'Información detallada de las operaciones vinculadas',
        'Análisis de comparabilidad',
        'Método de valoración elegido',
        'Información financiera del contribuyente',
        'Criterios de reparto de costes',
        'Acuerdos de reparto de costes',
        'Acuerdos previos de valoración',
        'Información sobre establecimientos permanentes',
        'Información sobre operaciones con paraísos fiscales',
        'Información general sobre el grupo',
    ];

    const masterFileItems = [
        'Estructura organizativa del grupo multinacional',
        'Descripción del negocio del grupo',
        'Intangibles del grupo',
        'Actividades financieras intragrupo',
        'Situación financiera y fiscal del grupo',
        'Descripción de la cadena de suministro',
        'Lista de acuerdos importantes de servicios',
        'Descripción funcional y estrategia del grupo',
        'Principales operaciones de reestructuración',
        'Descripción de la estrategia del grupo respecto a intangibles',
        'Lista de intangibles importantes',
        'Descripción de acuerdos de coste',
        'Descripción de préstamos intragrupo',
        'Estados financieros consolidados',
        'Lista de APAs unilaterales',
        'Información sobre resoluciones fiscales',
        'Información sobre operaciones con paraísos fiscales',
    ];

    const items = prefix === 'local' ? localFileItems : masterFileItems;
    const cumplidoOptions = ['si', 'parcial', 'no'];

    // Section title
    const titleText = prefix === 'local' ? 'Cumplimiento Local File - Detalle' : 'Cumplimiento Master File - Detalle';
    const title = document.createElement('h4');
    title.className = 'section-subheader';
    title.textContent = titleText;
    container.appendChild(title);

    // Render each compliance item with vertical layout (like Streamlit)
    for (let i = 1; i <= count; i++) {
        // Item container
        const itemContainer = document.createElement('div');
        itemContainer.className = 'compliance-item-vertical';

        // Item header with number and content
        const itemHeader = document.createElement('div');
        itemHeader.className = 'compliance-item-header';
        itemHeader.innerHTML = `<strong>${i}. ${items[i - 1] || `Item ${i}`}</strong>`;
        itemContainer.appendChild(itemHeader);

        // Input row with vertical layout (like Streamlit)
        const inputRow = document.createElement('div');
        inputRow.className = 'compliance-item-inputs-vertical';

        // Cumplido
        const cumplidoGroup = document.createElement('div');
        cumplidoGroup.className = 'form-group-row';
        const cumplidoLabel = document.createElement('label');
        cumplidoLabel.className = 'form-label-inline';
        cumplidoLabel.textContent = 'Cumplido';
        cumplidoGroup.appendChild(cumplidoLabel);
        const cumplidoSelect = createSelect(`cumplido_${prefix}_${i}`, cumplidoOptions, 'si');
        cumplidoGroup.appendChild(cumplidoSelect);
        inputRow.appendChild(cumplidoGroup);

        // Comentario
        const comentarioGroup = document.createElement('div');
        comentarioGroup.className = 'form-group-row comentario-group';
        const comentarioLabel = document.createElement('label');
        comentarioLabel.className = 'form-label-inline';
        comentarioLabel.textContent = 'Comentario';
        comentarioGroup.appendChild(comentarioLabel);
        const comentarioInput = document.createElement('input');
        comentarioInput.type = 'text';
        comentarioInput.className = 'form-input';
        comentarioInput.name = `texto_cumplido_${prefix}_${i}`;
        comentarioInput.placeholder = 'Comentario (requerido si no cumple)...';
        comentarioInput.addEventListener('input', (e) => {
            AppState.setFormValue(`texto_cumplido_${prefix}_${i}`, e.target.value);
        });
        comentarioGroup.appendChild(comentarioInput);
        inputRow.appendChild(comentarioGroup);

        itemContainer.appendChild(inputRow);

        // Divider between items
        const divider = document.createElement('hr');
        divider.className = 'compliance-item-divider';
        itemContainer.appendChild(divider);

        container.appendChild(itemContainer);
    }

    return container;
}

function renderComplianceSummaryTable(prefix, count, allFields) {
    const container = document.createElement('div');
    container.className = 'compliance-summary-vertical';

    const localSections = [
        { num: 1, label: 'Información del contribuyente' },
        { num: 2, label: 'Información de las operaciones vinculadas' },
        { num: 3, label: 'Información económico-financiera del contribuyente' },
    ];

    const masterSections = [
        { num: 1, label: 'Información relativa a la estructura y actividades del Grupo' },
        { num: 2, label: 'Información relativa a los activos intangibles del Grupo' },
        { num: 3, label: 'Información relativa a la actividad financiera' },
        { num: 4, label: 'Situación financiera y fiscal del Grupo' },
    ];

    const sections = prefix === 'local' ? localSections : masterSections;
    const cumplimientoOptions = ['si', 'no'];

    const reglamento = prefix === 'local' ? 'Artículo 16 del Reglamento' : 'Artículo 15 del Reglamento';
    const titleText = prefix === 'local' ? 'Cumplimiento Local File (Resumen)' : 'Cumplimiento Master File (Resumen)';

    // Section title
    const title = document.createElement('h4');
    title.className = 'section-subheader';
    title.textContent = titleText;
    container.appendChild(title);

    // Info text
    const infoText = document.createElement('p');
    infoText.className = 'info-text';
    infoText.innerHTML = `<em>Secciones según ${reglamento}</em>`;
    container.appendChild(infoText);

    // Render each section with vertical layout (like Streamlit)
    sections.forEach(section => {
        // Item container
        const itemContainer = document.createElement('div');
        itemContainer.className = 'compliance-summary-item';

        // Item header with number and label
        const itemHeader = document.createElement('div');
        itemHeader.className = 'compliance-summary-header';
        itemHeader.innerHTML = `<strong>${section.num}. ${section.label}</strong>`;
        itemContainer.appendChild(itemHeader);

        // Input row with vertical layout
        const inputRow = document.createElement('div');
        inputRow.className = 'compliance-summary-inputs-vertical';

        // Cumplimiento
        const cumplimientoGroup = document.createElement('div');
        cumplimientoGroup.className = 'form-group-row';
        const cumplimientoLabel = document.createElement('label');
        cumplimientoLabel.className = 'form-label-inline';
        cumplimientoLabel.textContent = 'Cumplimiento';
        cumplimientoGroup.appendChild(cumplimientoLabel);
        const cumplimientoSelect = createSelect(`cumplimiento_resumen_${prefix}_${section.num}`, cumplimientoOptions, 'si');
        cumplimientoGroup.appendChild(cumplimientoSelect);
        inputRow.appendChild(cumplimientoGroup);

        itemContainer.appendChild(inputRow);

        // Divider between items
        const divider = document.createElement('hr');
        divider.className = 'compliance-summary-divider';
        itemContainer.appendChild(divider);

        container.appendChild(itemContainer);
    });

    return container;
}

function renderComentariosVlorativosSection() {
    const container = document.createElement('div');
    container.className = 'comentarios-valorativos-section';
    container.id = 'comentarios-valorativos-container';

    // Section title
    const divider = document.createElement('hr');
    divider.className = 'section-divider';
    container.appendChild(divider);

    const title = document.createElement('h4');
    title.className = 'section-subheader';
    title.textContent = 'Comentarios Valorativos';
    container.appendChild(title);

    const caption = document.createElement('p');
    caption.className = 'info-text';
    caption.textContent = 'Seleccione los comentarios que desea incluir en el documento.';
    container.appendChild(caption);

    // Get comentarios data from state
    const comentarios = AppState.comentariosData || [];

    if (comentarios.length === 0) {
        const loading = document.createElement('p');
        loading.className = 'info-text';
        loading.textContent = 'Cargando comentarios valorativos...';
        container.appendChild(loading);

        // Try to load comentarios if not already loaded
        if (AppState.currentPlugin) {
            loadComentariosValorativos(AppState.currentPlugin).then(data => {
                if (data && data.length > 0) {
                    refreshComentariosSection();
                }
            });
        }
        return container;
    }

    const siNoOptions = ['no', 'si'];

    comentarios.forEach(comentario => {
        const itemContainer = document.createElement('div');
        itemContainer.className = 'comentario-valorativo-item';
        itemContainer.dataset.fieldName = comentario.id;

        // Row with question, selector, and conditional preview
        const row = document.createElement('div');
        row.className = 'comentario-row';

        // Question column
        const questionCol = document.createElement('div');
        questionCol.className = 'comentario-question';
        questionCol.innerHTML = `<strong>${comentario.index}.</strong> ${comentario.question}`;
        row.appendChild(questionCol);

        // Selector column
        const selectorCol = document.createElement('div');
        selectorCol.className = 'comentario-selector';

        const select = document.createElement('select');
        select.className = 'select-input';
        select.name = comentario.id;
        select.dataset.comentarioId = comentario.id;

        siNoOptions.forEach(opt => {
            const option = document.createElement('option');
            option.value = opt;
            option.textContent = opt.charAt(0).toUpperCase() + opt.slice(1);
            if (opt === 'no') {
                option.selected = true;
            }
            select.appendChild(option);
        });

        // Set default value
        AppState.setFormValue(comentario.id, 'no');

        select.addEventListener('change', (e) => {
            AppState.setFormValue(comentario.id, e.target.value);
            updateComentarioPreview(comentario.id, e.target.value, comentario.text_preview);
        });

        selectorCol.appendChild(select);
        row.appendChild(selectorCol);

        // Preview column (initially hidden)
        const previewCol = document.createElement('div');
        previewCol.className = 'comentario-preview hidden';
        previewCol.id = `preview-${comentario.id}`;

        if (comentario.text_preview) {
            const previewText = document.createElement('textarea');
            previewText.className = 'preview-textarea';
            previewText.value = comentario.text_preview;
            previewText.disabled = true;
            previewText.rows = 3;
            previewCol.appendChild(previewText);
        }

        row.appendChild(previewCol);

        itemContainer.appendChild(row);

        // Divider
        const itemDivider = document.createElement('hr');
        itemDivider.className = 'comentario-divider';
        itemContainer.appendChild(itemDivider);

        container.appendChild(itemContainer);
    });

    return container;
}

function updateComentarioPreview(fieldId, value, textPreview) {
    const previewCol = document.getElementById(`preview-${fieldId}`);
    if (previewCol) {
        if (value === 'si' && textPreview) {
            previewCol.classList.remove('hidden');
        } else {
            previewCol.classList.add('hidden');
        }
    }
}

function refreshComentariosSection() {
    const container = document.getElementById('comentarios-valorativos-container');
    if (container && container.parentElement) {
        const newSection = renderComentariosVlorativosSection();
        container.parentElement.replaceChild(newSection, container);
    }
}

function renderContactsSection(allFields) {
    const container = document.createElement('div');
    container.className = 'contacts-grid';

    for (let i = 1; i <= 3; i++) {
        const card = document.createElement('div');
        card.className = 'contact-card';

        card.innerHTML = `<h4>Contacto ${i}</h4>`;

        // Name
        const nameGroup = document.createElement('div');
        nameGroup.className = 'form-group';
        nameGroup.innerHTML = `<label class="form-label">Nombre</label>`;
        const nameInput = document.createElement('input');
        nameInput.type = 'text';
        nameInput.className = 'form-input';
        nameInput.name = `contacto${i}`;
        nameInput.placeholder = 'Nombre completo';
        nameInput.addEventListener('input', (e) => {
            AppState.setFormValue(`contacto${i}`, e.target.value);
        });
        nameGroup.appendChild(nameInput);
        card.appendChild(nameGroup);

        // Position
        const cargoGroup = document.createElement('div');
        cargoGroup.className = 'form-group';
        cargoGroup.innerHTML = `<label class="form-label">Cargo</label>`;
        const cargoInput = document.createElement('input');
        cargoInput.type = 'text';
        cargoInput.className = 'form-input';
        cargoInput.name = `cargo_contacto${i}`;
        cargoInput.placeholder = 'Cargo';
        cargoInput.addEventListener('input', (e) => {
            AppState.setFormValue(`cargo_contacto${i}`, e.target.value);
        });
        cargoGroup.appendChild(cargoInput);
        card.appendChild(cargoGroup);

        // Email
        const emailGroup = document.createElement('div');
        emailGroup.className = 'form-group';
        emailGroup.innerHTML = `<label class="form-label">Correo</label>`;
        const emailInput = document.createElement('input');
        emailInput.type = 'email';
        emailInput.className = 'form-input';
        emailInput.name = `correo_contacto${i}`;
        emailInput.placeholder = 'email@example.com';
        emailInput.addEventListener('input', (e) => {
            AppState.setFormValue(`correo_contacto${i}`, e.target.value);
        });
        emailGroup.appendChild(emailInput);
        card.appendChild(emailGroup);

        container.appendChild(card);
    }

    return container;
}

function renderOperacionesVinculadasSection(allFields) {
    const container = document.createElement('div');
    container.className = 'operaciones-vinculadas-section';

    // ========================================================================
    // Section 1: Operaciones Intragrupo - List of operation types
    // ========================================================================
    const intragrupoSection = document.createElement('div');
    intragrupoSection.className = 'operaciones-intragrupo-section';

    const intragrupoTitle = document.createElement('h4');
    intragrupoTitle.className = 'subsection-title';
    intragrupoTitle.textContent = 'Operaciones Intragrupo';
    intragrupoSection.appendChild(intragrupoTitle);

    // Table header
    const intragrupoHeader = document.createElement('div');
    intragrupoHeader.className = 'form-table-header operations-intragrupo-header';
    intragrupoHeader.innerHTML = `
        <span style="flex: 0.1;">#</span>
        <span style="flex: 0.9;">Operaciones intragrupo</span>
    `;
    intragrupoSection.appendChild(intragrupoHeader);

    // Container for operation items
    const operacionesContainer = document.createElement('div');
    operacionesContainer.id = 'operaciones-intragrupo-items';
    operacionesContainer.className = 'operaciones-intragrupo-items';
    intragrupoSection.appendChild(operacionesContainer);

    // Add operation button
    const addOperacionBtn = document.createElement('button');
    addOperacionBtn.type = 'button';
    addOperacionBtn.className = 'btn btn-outline btn-add-item';
    addOperacionBtn.innerHTML = 'Añadir operación';
    addOperacionBtn.addEventListener('click', () => {
        addOperacionVinculada();
    });
    intragrupoSection.appendChild(addOperacionBtn);

    container.appendChild(intragrupoSection);

    // Divider
    const divider1 = document.createElement('hr');
    divider1.className = 'section-divider';
    container.appendChild(divider1);

    // ========================================================================
    // Section 2: Detalle de Operaciones Vinculadas - Entity breakdown
    // ========================================================================
    const detalleSection = document.createElement('div');
    detalleSection.className = 'operaciones-detalle-section';

    const detalleTitle = document.createElement('h4');
    detalleTitle.className = 'subsection-title';
    detalleTitle.textContent = 'Detalle de Operaciones Vinculadas';
    detalleSection.appendChild(detalleTitle);

    // Get fiscal year for column header
    const fechaFin = AppState.getFormValue('fecha_fin_fiscal');
    let anyoActual = 'FY 2026';
    if (fechaFin) {
        try {
            const year = new Date(fechaFin).getFullYear();
            if (!isNaN(year)) anyoActual = `FY ${year}`;
        } catch (e) { }
    }

    // Table header
    const detalleHeader = document.createElement('div');
    detalleHeader.className = 'form-table-header operations-detail-header';
    detalleHeader.innerHTML = `
        <span style="flex: 0.25;">Tipo de operación vinculada</span>
        <span style="flex: 0.25;">Entidad vinculada</span>
        <span style="flex: 0.25;">Ingreso ${anyoActual} (EUR)</span>
        <span style="flex: 0.25;">Gasto ${anyoActual} (EUR)</span>
    `;
    detalleSection.appendChild(detalleHeader);

    // Container for detail items (entities grouped by operation)
    const detalleContainer = document.createElement('div');
    detalleContainer.id = 'operaciones-detalle-items';
    detalleContainer.className = 'operaciones-detalle-items';
    detalleSection.appendChild(detalleContainer);

    // Totals row
    const totalsRow = document.createElement('div');
    totalsRow.className = 'form-table-totals operations-totals';
    totalsRow.innerHTML = `
        <span style="flex: 0.50;"><strong>Totales OOVV</strong></span>
        <span style="flex: 0.25;" id="total-ingreso-oovv"><strong>0,00 €</strong></span>
        <span style="flex: 0.25;" id="total-gasto-oovv"><strong>0,00 €</strong></span>
    `;
    detalleSection.appendChild(totalsRow);

    container.appendChild(detalleSection);

    // Divider
    const divider2 = document.createElement('hr');
    divider2.className = 'section-divider';
    container.appendChild(divider2);

    // ========================================================================
    // Section 3: Peso OOVV indicators
    // ========================================================================
    const pesoSection = document.createElement('div');
    pesoSection.className = 'peso-oovv-section';
    pesoSection.id = 'peso-oovv-indicators';

    const pesoTitle = document.createElement('p');
    pesoTitle.className = 'caption-text';
    pesoTitle.textContent = 'Indicadores calculados automáticamente:';
    pesoSection.appendChild(pesoTitle);

    // Peso OOVV sobre INCN row
    const pesoIncnRow = document.createElement('div');
    pesoIncnRow.className = 'peso-row';
    pesoIncnRow.innerHTML = `
        <span class="peso-label">Peso OOVV sobre INCN</span>
        <span class="peso-value derived-value" id="peso-incn-value">N/A %</span>
    `;
    pesoSection.appendChild(pesoIncnRow);

    // Peso OOVV sobre total costes row
    const pesoCostesRow = document.createElement('div');
    pesoCostesRow.className = 'peso-row';
    pesoCostesRow.innerHTML = `
        <span class="peso-label">Peso OOVV sobre total costes</span>
        <span class="peso-value derived-value" id="peso-costes-value">N/A %</span>
    `;
    pesoSection.appendChild(pesoCostesRow);

    container.appendChild(pesoSection);

    // Divider
    const divider3 = document.createElement('hr');
    divider3.className = 'section-divider';
    container.appendChild(divider3);

    // ========================================================================
    // Section 4: Valoración OOVV text field
    // ========================================================================
    const valoracionGroup = document.createElement('div');
    valoracionGroup.className = 'form-group full-width';
    valoracionGroup.dataset.fieldName = 'valoracion_oovv';

    const valoracionLabel = document.createElement('label');
    valoracionLabel.className = 'form-label';
    valoracionLabel.textContent = 'Valoración de Operaciones Vinculadas';
    valoracionGroup.appendChild(valoracionLabel);

    const valoracionInput = document.createElement('textarea');
    valoracionInput.className = 'textarea-input';
    valoracionInput.name = 'valoracion_oovv';
    valoracionInput.rows = 4;
    valoracionInput.placeholder = 'Texto de valoración basado en los indicadores de peso OOVV';
    valoracionInput.addEventListener('input', (e) => {
        AppState.setFormValue('valoracion_oovv', e.target.value);
    });
    valoracionGroup.appendChild(valoracionInput);

    const valoracionHint = document.createElement('span');
    valoracionHint.className = 'form-hint';
    valoracionHint.textContent = 'Texto de valoración basado en los indicadores de peso OOVV';
    valoracionGroup.appendChild(valoracionHint);

    container.appendChild(valoracionGroup);

    // Initialize data and render items
    setTimeout(() => {
        renderOperacionesIntragrupoItems();
        renderOperacionesDetalleItems();
        updatePesoOOVVIndicators();
    }, 0);

    return container;
}

// Add a new operacion vinculada
function addOperacionVinculada() {
    const servicios = AppState.getListItems('servicios_vinculados');
    const newItem = {
        servicio_vinculado: '',
        entidades_vinculadas: []
    };
    AppState.addListItem('servicios_vinculados', newItem);
    renderOperacionesIntragrupoItems();
    renderOperacionesDetalleItems();
}

// Remove an operacion vinculada
function removeOperacionVinculada(index) {
    AppState.removeListItem('servicios_vinculados', index);
    renderOperacionesIntragrupoItems();
    renderOperacionesDetalleItems();
    updatePesoOOVVIndicators();
}

// Add an entity to a specific operation
function addEntidadToOperacion(servicioIndex) {
    const servicios = AppState.getListItems('servicios_vinculados');
    if (servicios[servicioIndex]) {
        if (!servicios[servicioIndex].entidades_vinculadas) {
            servicios[servicioIndex].entidades_vinculadas = [];
        }
        servicios[servicioIndex].entidades_vinculadas.push({
            entidad_vinculada: '',
            ingreso_entidad: 0,
            gasto_entidad: 0
        });
        renderOperacionesDetalleItems();
    }
}

// Remove an entity from a specific operation
function removeEntidadFromOperacion(servicioIndex, entidadIndex) {
    const servicios = AppState.getListItems('servicios_vinculados');
    if (servicios[servicioIndex] && servicios[servicioIndex].entidades_vinculadas) {
        servicios[servicioIndex].entidades_vinculadas.splice(entidadIndex, 1);
        renderOperacionesDetalleItems();
        updatePesoOOVVIndicators();
    }
}

// Render the Operaciones Intragrupo items list
function renderOperacionesIntragrupoItems() {
    const container = document.getElementById('operaciones-intragrupo-items');
    if (!container) return;

    container.innerHTML = '';
    const servicios = AppState.getListItems('servicios_vinculados');

    servicios.forEach((servicio, idx) => {
        const row = document.createElement('div');
        row.className = 'form-table-row operations-intragrupo-row';
        row.dataset.index = idx;

        // Number column
        const numCell = document.createElement('span');
        numCell.className = 'form-table-cell';
        numCell.style.flex = '0.1';
        numCell.innerHTML = `<strong>${idx + 1}</strong>`;

        // Operation name input
        const nameCell = document.createElement('span');
        nameCell.className = 'form-table-cell';
        nameCell.style.flex = '0.8';

        const nameInput = document.createElement('input');
        nameInput.type = 'text';
        nameInput.className = 'form-input';
        nameInput.placeholder = 'Tipo de operación vinculada';
        nameInput.value = servicio.servicio_vinculado || '';
        nameInput.addEventListener('input', (e) => {
            AppState.updateListItem('servicios_vinculados', idx, 'servicio_vinculado', e.target.value);
            // Update the detail section header for this operation
            renderOperacionesDetalleItems();
        });
        nameCell.appendChild(nameInput);

        // Remove button
        const removeCell = document.createElement('span');
        removeCell.className = 'form-table-cell';
        removeCell.style.flex = '0.1';
        removeCell.style.textAlign = 'right';

        const removeBtn = document.createElement('button');
        removeBtn.type = 'button';
        removeBtn.className = 'btn-remove';
        removeBtn.innerHTML = '✕';
        removeBtn.title = 'Eliminar operación';
        removeBtn.addEventListener('click', () => {
            removeOperacionVinculada(idx);
        });
        removeCell.appendChild(removeBtn);

        row.appendChild(numCell);
        row.appendChild(nameCell);
        row.appendChild(removeCell);
        container.appendChild(row);
    });
}

// Render the Detalle de Operaciones Vinculadas items (entities grouped by operation)
function renderOperacionesDetalleItems() {
    const container = document.getElementById('operaciones-detalle-items');
    if (!container) return;

    container.innerHTML = '';
    const servicios = AppState.getListItems('servicios_vinculados');

    if (servicios.length === 0) {
        const emptyMsg = document.createElement('p');
        emptyMsg.className = 'empty-message';
        emptyMsg.textContent = 'Primero añada operaciones en la sección anterior.';
        container.appendChild(emptyMsg);
        return;
    }

    servicios.forEach((servicio, servIdx) => {
        const servicioBlock = document.createElement('div');
        servicioBlock.className = 'operacion-block';
        servicioBlock.dataset.servicioIndex = servIdx;

        const servicioName = servicio.servicio_vinculado || `Operación ${servIdx + 1}`;
        let entidades = servicio.entidades_vinculadas || [];

        // Ensure at least one entity row exists for each operation
        if (entidades.length === 0) {
            entidades = [{ entidad_vinculada: '', ingreso_entidad: 0, gasto_entidad: 0 }];
            servicio.entidades_vinculadas = entidades;
        }

        // Render entity rows
        entidades.forEach((entidad, entIdx) => {
            const row = document.createElement('div');
            row.className = 'form-table-row operations-detail-row';
            row.dataset.servicioIndex = servIdx;
            row.dataset.entidadIndex = entIdx;

            // Operation name (only show on first entity row)
            const opCell = document.createElement('span');
            opCell.className = 'form-table-cell';
            opCell.style.flex = '0.25';
            if (entIdx === 0) {
                opCell.innerHTML = `<strong>${servicioName}</strong>`;
            }

            // Entity name input
            const entCell = document.createElement('span');
            entCell.className = 'form-table-cell';
            entCell.style.flex = '0.25';

            const entInput = document.createElement('input');
            entInput.type = 'text';
            entInput.className = 'form-input';
            entInput.placeholder = 'Nombre de entidad';
            entInput.value = entidad.entidad_vinculada || '';
            entInput.addEventListener('input', (e) => {
                if (servicio.entidades_vinculadas && servicio.entidades_vinculadas[entIdx]) {
                    servicio.entidades_vinculadas[entIdx].entidad_vinculada = e.target.value;
                }
            });
            entCell.appendChild(entInput);

            // Ingreso input
            const ingresoCell = document.createElement('span');
            ingresoCell.className = 'form-table-cell';
            ingresoCell.style.flex = '0.20';

            const ingresoInput = document.createElement('input');
            ingresoInput.type = 'number';
            ingresoInput.className = 'form-input currency-input';
            ingresoInput.step = '0.01';
            ingresoInput.placeholder = '0,00';
            ingresoInput.value = entidad.ingreso_entidad || 0;
            ingresoInput.addEventListener('input', (e) => {
                const value = parseFloat(e.target.value) || 0;
                if (servicio.entidades_vinculadas && servicio.entidades_vinculadas[entIdx]) {
                    servicio.entidades_vinculadas[entIdx].ingreso_entidad = value;
                }
                updatePesoOOVVIndicators();
            });
            ingresoCell.appendChild(ingresoInput);

            // Gasto input
            const gastoCell = document.createElement('span');
            gastoCell.className = 'form-table-cell';
            gastoCell.style.flex = '0.20';

            const gastoInput = document.createElement('input');
            gastoInput.type = 'number';
            gastoInput.className = 'form-input currency-input';
            gastoInput.step = '0.01';
            gastoInput.placeholder = '0,00';
            gastoInput.value = entidad.gasto_entidad || 0;
            gastoInput.addEventListener('input', (e) => {
                const value = parseFloat(e.target.value) || 0;
                if (servicio.entidades_vinculadas && servicio.entidades_vinculadas[entIdx]) {
                    servicio.entidades_vinculadas[entIdx].gasto_entidad = value;
                }
                updatePesoOOVVIndicators();
            });
            gastoCell.appendChild(gastoInput);

            // Remove entity button (only if more than one entity)
            const removeCell = document.createElement('span');
            removeCell.className = 'form-table-cell';
            removeCell.style.flex = '0.10';
            removeCell.style.textAlign = 'right';

            if (entidades.length > 1) {
                const removeBtn = document.createElement('button');
                removeBtn.type = 'button';
                removeBtn.className = 'btn-remove-small';
                removeBtn.innerHTML = '−';
                removeBtn.title = 'Eliminar entidad';
                removeBtn.addEventListener('click', () => {
                    removeEntidadFromOperacion(servIdx, entIdx);
                });
                removeCell.appendChild(removeBtn);
            }

            row.appendChild(opCell);
            row.appendChild(entCell);
            row.appendChild(ingresoCell);
            row.appendChild(gastoCell);
            row.appendChild(removeCell);
            servicioBlock.appendChild(row);
        });

        // Add entity button for this operation
        const addEntBtn = document.createElement('button');
        addEntBtn.type = 'button';
        addEntBtn.className = 'btn btn-outline btn-add-entity';
        addEntBtn.innerHTML = `Añadir entidad a '${servicioName}'`;
        addEntBtn.addEventListener('click', () => {
            addEntidadToOperacion(servIdx);
        });
        servicioBlock.appendChild(addEntBtn);

        // Divider between operations
        const divider = document.createElement('hr');
        divider.className = 'operation-divider';
        servicioBlock.appendChild(divider);

        container.appendChild(servicioBlock);
    });
}

function updatePesoOOVVIndicators() {
    // Get financial data for calculations
    const cifra_1 = AppState.getFormValue('cifra_1') || 0;
    const ebit_1 = AppState.getFormValue('ebit_1') || 0;
    const cost_1 = cifra_1 - ebit_1;

    // Calculate total ingreso and gasto from servicios_vinculados
    const servicios = AppState.getListItems('servicios_vinculados');
    let totalIngreso = 0;
    let totalGasto = 0;

    servicios.forEach(servicio => {
        const entidades = servicio.entidades_vinculadas || [];
        entidades.forEach(entidad => {
            totalIngreso += parseFloat(entidad.ingreso_entidad) || 0;
            totalGasto += parseFloat(entidad.gasto_entidad) || 0;
        });
    });

    // Update totals display
    const totalIngresoEl = document.getElementById('total-ingreso-oovv');
    const totalGastoEl = document.getElementById('total-gasto-oovv');

    const formatCurrency = (value) => {
        return value.toLocaleString('es-ES', {
            minimumFractionDigits: 2,
            maximumFractionDigits: 2
        }) + ' €';
    };

    if (totalIngresoEl) {
        totalIngresoEl.innerHTML = `<strong>${formatCurrency(totalIngreso)}</strong>`;
    }
    if (totalGastoEl) {
        totalGastoEl.innerHTML = `<strong>${formatCurrency(totalGasto)}</strong>`;
    }

    // Calculate peso indicators
    let pesoIncn = 'N/A';
    let pesoCostes = 'N/A';

    if (cifra_1 !== 0) {
        pesoIncn = ((totalIngreso / cifra_1) * 100).toLocaleString('es-ES', {
            minimumFractionDigits: 2,
            maximumFractionDigits: 2
        });
    }

    if (cost_1 !== 0) {
        pesoCostes = ((totalGasto / cost_1) * 100).toLocaleString('es-ES', {
            minimumFractionDigits: 2,
            maximumFractionDigits: 2
        });
    }

    // Update display
    const pesoIncnEl = document.getElementById('peso-incn-value');
    const pesoCostesEl = document.getElementById('peso-costes-value');

    if (pesoIncnEl) {
        pesoIncnEl.textContent = `${pesoIncn} %`;
    }
    if (pesoCostesEl) {
        pesoCostesEl.textContent = `${pesoCostes} %`;
    }
}

function createSelect(name, options, defaultValue = '') {
    const select = document.createElement('select');
    select.className = 'select-input';
    select.name = name;

    options.forEach(opt => {
        const option = document.createElement('option');
        option.value = opt;
        option.textContent = opt.charAt(0).toUpperCase() + opt.slice(1);
        if (opt === defaultValue) {
            option.selected = true;
        }
        select.appendChild(option);
    });

    select.addEventListener('change', (e) => {
        AppState.setFormValue(name, e.target.value);
        updateConditionalVisibility();
    });

    // Set default value in state
    AppState.setFormValue(name, defaultValue);

    return select;
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
        // Extract filename from path - handle both forward and backslashes
        let filename = 'document.docx';
        if (result.output_path) {
            const pathParts = result.output_path.replace(/\\/g, '/').split('/');
            filename = pathParts[pathParts.length - 1];
        }

        content.innerHTML = `
            <div class="result-success">
                <div class="success-icon">✓</div>
                <h4>Document Generated Successfully!</h4>
                <p>Your document has been created and is ready for download.</p>
                <button id="download-doc-btn" class="btn btn-primary download-btn" data-filename="${filename}">
                    <span class="btn-icon">📥</span>
                    Download Document
                </button>
                <div class="trace-info">
                    <p>Trace ID: <span class="trace-id">${result.trace_id || 'N/A'}</span></p>
                    <p>Duration: ${result.duration_ms || 0}ms</p>
                </div>
            </div>
            ${renderDecisionTrace(result.decision_traces)}
        `;

        // Add click event listener for download button
        const downloadBtn = document.getElementById('download-doc-btn');
        if (downloadBtn) {
            downloadBtn.addEventListener('click', async () => {
                const fname = downloadBtn.dataset.filename;
                await downloadDocument(fname);
            });
        }
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

async function downloadDocument(filename) {
    try {
        showLoading('Downloading document...');

        const response = await fetch(`${API_BASE}/download/${encodeURIComponent(filename)}`);

        if (!response.ok) {
            throw new Error(`Download failed: ${response.status} ${response.statusText}`);
        }

        // Get the blob from response
        const blob = await response.blob();

        // Create a download link and trigger it
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = filename;
        document.body.appendChild(a);
        a.click();

        // Cleanup
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);

        showNotification('success', 'Download Complete', `File "${filename}" has been downloaded.`);
    } catch (error) {
        console.error('Download error:', error);
        showNotification('error', 'Download Failed', error.message);
    } finally {
        hideLoading();
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

function importJson(file) {
    const reader = new FileReader();
    reader.onload = function (e) {
        try {
            const json = JSON.parse(e.target.result);
            loadJsonData(json);
            showNotification('success', 'Import Complete', 'Form data has been imported from JSON.');
        } catch (error) {
            showNotification('error', 'Import Failed', `Invalid JSON file: ${error.message}`);
        }
    };
    reader.onerror = function () {
        showNotification('error', 'Import Failed', 'Failed to read the file.');
    };
    reader.readAsText(file);
}

function loadJsonData(json) {
    if (!AppState.schema) {
        showNotification('warning', 'No Plugin Selected', 'Please select a plugin first before importing data.');
        return;
    }

    // Clear existing data
    AppState.clearAll();

    // Process all fields from JSON
    for (const [key, value] of Object.entries(json)) {
        // Skip internal keys (legacy support)
        if (key.startsWith('_')) {
            // Handle legacy _list_items format
            if (key === '_list_items' && typeof value === 'object') {
                for (const [listKey, listValue] of Object.entries(value)) {
                    if (Array.isArray(listValue)) {
                        AppState.listData[listKey] = listValue.map((item, idx) => {
                            if (typeof item === 'object') {
                                return { ...item, _id: Date.now() + idx };
                            }
                            return { value: item, _id: Date.now() + idx };
                        });
                    }
                }
            }
            continue;
        }

        if (Array.isArray(value)) {
            // Handle list fields
            AppState.listData[key] = value.map((item, idx) => {
                if (typeof item === 'object') {
                    return { ...item, _id: Date.now() + idx };
                }
                return { value: item, _id: Date.now() + idx };
            });
        } else {
            // Handle scalar fields
            AppState.setFormValue(key, value);
        }
    }

    // Update form inputs with imported data
    updateFormWithImportedData();

    // Update UI
    updateConditionalVisibility();
    updateDerivedValues();
}

function updateFormWithImportedData() {
    // Update all form inputs with data from AppState
    for (const [key, value] of Object.entries(AppState.formData)) {
        const input = document.querySelector(`[name="${key}"]`);
        if (input) {
            if (input.type === 'checkbox') {
                input.checked = Boolean(value);
            } else if (input.type === 'date' && value) {
                // Handle date fields
                input.value = value;
            } else {
                input.value = value !== null && value !== undefined ? value : '';
            }
        }
    }

    // Refresh list displays
    if (AppState.schema && AppState.schema.fields) {
        AppState.schema.fields.forEach(field => {
            if (field.type === 'list') {
                refreshListItems(field);
            }
        });
    }
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

        // Get schema and comentarios valorativos in parallel
        const [schema, comentarios] = await Promise.all([
            loadPluginSchema(pluginId),
            loadComentariosValorativos(pluginId),
        ]);

        if (schema) {
            AppState.setPlugin(pluginId);
            AppState.comentariosData = comentarios;  // Store before rendering
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

    // Import JSON functionality
    const importInput = document.getElementById('json-import-input');
    document.getElementById('btn-import-json').addEventListener('click', () => {
        importInput.click();
    });
    importInput.addEventListener('change', (e) => {
        if (e.target.files && e.target.files[0]) {
            importJson(e.target.files[0]);
            // Reset the input so the same file can be imported again
            e.target.value = '';
        }
    });

    // Modal close handlers
    document.querySelectorAll('.modal-close, .modal-cancel').forEach(btn => {
        btn.addEventListener('click', () => {
            document.getElementById('modal-backdrop').classList.add('hidden');
        });
    });

    // ── Navigation: Generator ↔ Template Admin ──
    const navGenerator = document.getElementById('nav-generator');
    const navTA = document.getElementById('nav-template-admin');
    const mainContainer = document.querySelector('.main-container');
    const taPanel = document.getElementById('template-admin-panel');

    navTA.addEventListener('click', (e) => {
        e.preventDefault();
        navTA.classList.add('active');
        navGenerator.classList.remove('active');
        mainContainer.style.display = 'none';
        taPanel.classList.remove('hidden');
        TemplateAdmin.onOpen();
    });

    navGenerator.addEventListener('click', (e) => {
        e.preventDefault();
        navGenerator.classList.add('active');
        navTA.classList.remove('active');
        mainContainer.style.display = '';
        taPanel.classList.add('hidden');
    });

    console.log('Document Generation Platform v3.0 initialized');
}

// Start the application
document.addEventListener('DOMContentLoaded', init);

// ============================================================================
// Template Admin Module
// ============================================================================

const TemplateAdmin = (() => {
    // ── State ──
    let _token = null;          // auth token (password echoed back)
    let _validationResult = null;
    let _selectedFile = null;
    let _plugins = [];

    // ── API helpers ──
    async function taApi(endpoint, options = {}) {
        const url = `${API_BASE}${endpoint}`;
        try {
            const response = await fetch(url, options);
            const data = await response.json();
            if (!response.ok) throw new Error(data.detail || data.error || 'API Error');
            return data;
        } catch (err) {
            console.error('TA API Error:', err);
            throw err;
        }
    }

    // ── Utility ──
    function show(id) { document.getElementById(id).classList.remove('hidden'); }
    function hide(id) { document.getElementById(id).classList.add('hidden'); }
    function setHtml(id, html) { document.getElementById(id).innerHTML = html; }
    function val(id) { return document.getElementById(id).value; }

    function populatePluginSelects(plugins) {
        _plugins = plugins;
        ['ta-plugin-select', 'ta-history-plugin'].forEach(selId => {
            const sel = document.getElementById(selId);
            sel.innerHTML = '';
            plugins.forEach(p => {
                const opt = document.createElement('option');
                opt.value = p.plugin_id;
                opt.textContent = p.name || p.plugin_id;
                sel.appendChild(opt);
            });
        });
    }

    // ── Auth ──
    async function doLogin() {
        const pwd = val('ta-password-input');
        if (!pwd) return;
        try {
            const res = await taApi('/template/auth', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ password: pwd }),
            });
            if (res.ok) {
                _token = pwd;
                hide('ta-login');
                show('ta-content');
                hide('ta-login-error');
                document.getElementById('ta-password-input').value = '';
            } else {
                show('ta-login-error');
            }
        } catch (_) {
            show('ta-login-error');
        }
    }

    function doLogout() {
        _token = null;
        _validationResult = null;
        _selectedFile = null;
        show('ta-login');
        hide('ta-content');
        hide('ta-login-error');
        // Reset form
        setHtml('ta-validation-result', '<p class="ta-muted">Upload and validate a template to see results here.</p>');
        hide('ta-publish-section');
        resetFileZone();
    }

    // ── File handling ──
    function resetFileZone() {
        _selectedFile = null;
        const drop = document.getElementById('ta-file-drop');
        drop.classList.remove('has-file');
        drop.querySelector('p').textContent = 'Click to select or drag & drop a .docx file';
        document.getElementById('ta-file-input').value = '';
        document.getElementById('ta-validate-btn').disabled = true;
    }

    function onFileSelected(file) {
        if (!file || !file.name.endsWith('.docx')) {
            alert('Please select a .docx file');
            return;
        }
        _selectedFile = file;
        _validationResult = null;
        const drop = document.getElementById('ta-file-drop');
        drop.classList.add('has-file');
        drop.querySelector('p').textContent = `📄 ${file.name}  (${(file.size / 1024).toFixed(1)} KB)`;
        document.getElementById('ta-validate-btn').disabled = false;
        // Clear previous validation
        setHtml('ta-validation-result', '<p class="ta-muted">Click "Validate Template" to run checks.</p>');
        hide('ta-publish-section');
    }

    // ── Validation ──
    async function doValidate() {
        if (!_selectedFile) return;
        const pluginId = val('ta-plugin-select');
        show('ta-validating');
        document.getElementById('ta-validate-btn').disabled = true;
        hide('ta-publish-section');

        try {
            const fd = new FormData();
            fd.append('file', _selectedFile, _selectedFile.name);
            fd.append('plugin_id', pluginId);
            fd.append('check_anchors', 'false');

            const res = await taApi('/template/validate', { method: 'POST', body: fd });
            _validationResult = res;
            renderValidationResult(res);

            // Fetch current version to compute next
            await refreshNextVersion();
            show('ta-publish-section');

            // Show warning acknowledgement checkbox if needed
            const hasWarnings = res.status === 'WARN';
            const warnRow = document.getElementById('ta-warn-confirm-row');
            const warnBox = document.getElementById('ta-publish-warning');
            if (hasWarnings) {
                warnRow.style.display = '';
                warnBox.classList.remove('hidden');
            } else {
                warnRow.style.display = 'none';
                warnBox.classList.add('hidden');
            }
            document.getElementById('ta-warn-confirm').checked = false;
            updatePublishBtn();

        } catch (err) {
            setHtml('ta-validation-result', `<p class="ta-error">Validation failed: ${err.message}</p>`);
        } finally {
            hide('ta-validating');
            document.getElementById('ta-validate-btn').disabled = false;
        }
    }

    function renderValidationResult(res) {
        const statusEmoji = res.status === 'PASS' ? '✅' : res.status === 'WARN' ? '⚠️' : '❌';
        const statusClass = res.status === 'PASS' ? 'ta-status-pass' : res.status === 'WARN' ? 'ta-status-warn' : 'ta-status-fail';

        let issuesHtml = '';
        if (res.issues && res.issues.length > 0) {
            issuesHtml = `
                <ul class="ta-issue-list">
                    ${res.issues.map(i => `
                        <li class="ta-issue-${i.severity.toLowerCase()}">
                            <span>${i.severity === 'ERROR' ? '✕' : i.severity === 'WARN' ? '⚠' : 'ℹ'}</span>
                            <span>[${i.check}] ${i.message}</span>
                        </li>
                    `).join('')}
                </ul>`;
        } else {
            issuesHtml = '<p style="color:var(--success); margin-top:8px;">No issues found.</p>';
        }

        const vars = (res.variables_found || []).slice(0, 12).join(', ');
        const moreVars = (res.variables_found || []).length > 12 ? ` … (+${res.variables_found.length - 12} more)` : '';

        const html = `
            <div class="ta-status-badge ${statusClass}">${statusEmoji} ${res.status}</div>
            ${issuesHtml}
            <div class="ta-meta-row">
                <div><span>Variables found: </span><strong>${(res.variables_found || []).length}</strong></div>
                <div><span>SHA-256: </span><span class="ta-sha">${(res.sha256 || '—').slice(0, 16)}…</span></div>
            </div>
            ${(res.variables_found || []).length > 0 ? `<p style="font-size:0.75rem;color:var(--gray-500);margin-top:8px;">${vars}${moreVars}</p>` : ''}
        `;
        setHtml('ta-validation-result', html);
    }

    // ── Next version preview ──
    async function refreshNextVersion() {
        const pluginId = val('ta-plugin-select');
        const bump = val('ta-version-bump');
        try {
            const res = await taApi(`/template/versions/${pluginId}`);
            const current = (res.versions && res.versions.length > 0)
                ? res.versions[res.versions.length - 1].version
                : '0.0.0';
            const [ma, mi, pa] = current.split('.').map(Number);
            let next;
            if (bump === 'major') next = `${ma + 1}.0.0`;
            else if (bump === 'minor') next = `${ma}.${mi + 1}.0`;
            else next = `${ma}.${mi}.${pa + 1}`;
            document.getElementById('ta-next-version').textContent = next;
        } catch (_) {
            document.getElementById('ta-next-version').textContent = '1.0.0';
        }
    }

    function updatePublishBtn() {
        const hasWarnings = _validationResult && _validationResult.status === 'WARN';
        const confirmed = document.getElementById('ta-warn-confirm').checked;
        const hasFail = _validationResult && _validationResult.status === 'FAIL';
        const btn = document.getElementById('ta-publish-btn');
        btn.disabled = hasFail || (hasWarnings && !confirmed);
    }

    // ── Publish ──
    async function doPublish() {
        if (!_selectedFile || !_validationResult) return;
        if (_validationResult.status === 'FAIL') {
            alert('Cannot publish a template that failed validation. Fix the errors first.');
            return;
        }

        const pluginId = val('ta-plugin-select');
        const bump = val('ta-version-bump');
        const author = val('ta-author') || 'Admin';
        const changelog = val('ta-changelog') || '(no description)';
        const tplName = val('ta-template-name') || 'template_final';

        const btn = document.getElementById('ta-publish-btn');
        btn.disabled = true;
        btn.textContent = '⏳ Publishing…';

        try {
            const fd = new FormData();
            fd.append('file', _selectedFile, _selectedFile.name);
            fd.append('plugin_id', pluginId);
            fd.append('admin_password', _token);
            fd.append('template_name', tplName);
            fd.append('version_bump', bump);
            fd.append('author', author);
            fd.append('changelog', changelog);

            const res = await taApi('/template/publish', { method: 'POST', body: fd });

            showNotification('success', '🚀 Published!',
                `Version ${res.version} published successfully for plugin "${pluginId}".`);

            // Refresh history if on that tab
            if (document.getElementById('ta-tab-history').classList.contains('active')) {
                await loadHistory();
            }
            resetFileZone();
            setHtml('ta-validation-result', '<p class="ta-muted">Upload and validate a template to see results here.</p>');
            hide('ta-publish-section');
            _validationResult = null;

        } catch (err) {
            showNotification('error', 'Publish failed', err.message);
        } finally {
            btn.disabled = false;
            btn.textContent = '🚀 Publish Template';
        }
    }

    // ── Version History ──
    async function loadHistory() {
        const pluginId = val('ta-history-plugin');
        const container = document.getElementById('ta-version-list');
        container.innerHTML = '<p class="ta-muted">Loading…</p>';
        try {
            const res = await taApi(`/template/versions/${pluginId}`);
            const versions = (res.versions || []).slice().reverse(); // newest first
            const activeVer = res.active_version;

            if (versions.length === 0) {
                container.innerHTML = '<p class="ta-muted">No published versions yet.</p>';
                return;
            }

            container.innerHTML = '';
            versions.forEach(v => {
                const isActive = v.version === activeVer;
                const item = document.createElement('div');
                item.className = `ta-version-item${isActive ? ' active-version' : ''}`;
                item.innerHTML = `
                    <div class="ta-version-info">
                        <div>
                            <span class="ta-version-num">v${v.version}</span>
                            ${isActive ? '<span class="ta-version-active-tag">● Active</span>' : ''}
                        </div>
                        <div class="ta-version-meta">
                            Published ${v.published_at ? new Date(v.published_at).toLocaleString() : '—'}
                            ${v.author ? '· by ' + v.author : ''}
                            · SHA: <span class="ta-sha">${(v.sha256 || '—').slice(0, 16)}…</span>
                        </div>
                        <div class="ta-version-changelog">${v.changelog || ''}</div>
                    </div>
                    <div class="ta-version-actions">
                        ${!isActive ? `<button class="btn btn-outline btn-rollback" data-version="${v.version}" data-plugin="${pluginId}">↩ Rollback</button>` : '<span style="color:var(--success);font-size:0.85rem;">✔ Current</span>'}
                    </div>
                `;
                container.appendChild(item);
            });

            // Wire rollback buttons
            container.querySelectorAll('.btn-rollback').forEach(btn => {
                btn.addEventListener('click', async () => {
                    const ver = btn.dataset.version;
                    const pid = btn.dataset.plugin;
                    if (!confirm(`Roll back to v${ver} for plugin "${pid}"?\nThis will set that version as active immediately.`)) return;
                    await doRollback(pid, ver);
                });
            });

        } catch (err) {
            container.innerHTML = `<p class="ta-error">Failed to load history: ${err.message}</p>`;
        }
    }

    async function doRollback(pluginId, version) {
        try {
            await taApi('/template/rollback', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ plugin_id: pluginId, version, admin_password: _token }),
            });
            showNotification('success', '↩ Rollback complete',
                `Plugin "${pluginId}" is now using template v${version}.`);
            await loadHistory();
        } catch (err) {
            showNotification('error', 'Rollback failed', err.message);
        }
    }

    // ── Public init ──
    function onOpen() {
        // Populate plugin lists from already-loaded plugins
        fetch(`${API_BASE}/plugins`)
            .then(r => r.json())
            .then(data => populatePluginSelects(data.plugins || []))
            .catch(() => { });
    }

    // ── Wire events (called once DOM is ready) ──
    function wireEvents() {
        // Login
        document.getElementById('ta-login-btn').addEventListener('click', doLogin);
        document.getElementById('ta-password-input').addEventListener('keydown', e => {
            if (e.key === 'Enter') doLogin();
        });

        // Logout
        document.getElementById('ta-logout-btn').addEventListener('click', doLogout);

        // Tabs
        document.querySelectorAll('.ta-tab[data-tab]').forEach(tab => {
            tab.addEventListener('click', () => {
                document.querySelectorAll('.ta-tab[data-tab]').forEach(t => t.classList.remove('active'));
                document.querySelectorAll('.ta-tab-content').forEach(c => c.classList.remove('active'));
                tab.classList.add('active');
                document.getElementById(`ta-tab-${tab.dataset.tab}`).classList.add('active');
                if (tab.dataset.tab === 'history') loadHistory();
            });
        });

        // File input
        document.getElementById('ta-file-input').addEventListener('change', e => {
            if (e.target.files && e.target.files[0]) onFileSelected(e.target.files[0]);
        });

        // Drag & drop
        const dropZone = document.getElementById('ta-file-drop');
        dropZone.addEventListener('dragover', e => { e.preventDefault(); dropZone.classList.add('drag-over'); });
        dropZone.addEventListener('dragleave', () => dropZone.classList.remove('drag-over'));
        dropZone.addEventListener('drop', e => {
            e.preventDefault();
            dropZone.classList.remove('drag-over');
            if (e.dataTransfer.files && e.dataTransfer.files[0]) onFileSelected(e.dataTransfer.files[0]);
        });

        // Validate button
        document.getElementById('ta-validate-btn').addEventListener('click', doValidate);

        // Version bump → update preview
        document.getElementById('ta-version-bump').addEventListener('change', () => {
            if (_validationResult) refreshNextVersion();
        });
        document.getElementById('ta-plugin-select').addEventListener('change', () => {
            if (_validationResult) refreshNextVersion();
        });

        // Warning confirm checkbox
        document.getElementById('ta-warn-confirm').addEventListener('change', updatePublishBtn);

        // Publish button
        document.getElementById('ta-publish-btn').addEventListener('click', doPublish);

        // History plugin / refresh
        document.getElementById('ta-history-plugin').addEventListener('change', loadHistory);
        document.getElementById('ta-refresh-history').addEventListener('click', loadHistory);
    }

    // Auto-wire on DOMContentLoaded
    document.addEventListener('DOMContentLoaded', wireEvents);

    return { onOpen };
})();
