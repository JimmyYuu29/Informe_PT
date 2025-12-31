# HTML UI Integration Prompt for Document Generation Platform

> This file is a copy-paste prompt for instructing an AI (or developer) to build an HTML/JS frontend that integrates with the Document Generation API.

---

## Overview

You are building an HTML/JavaScript frontend for a document generation platform. The backend is a FastAPI service that exposes endpoints for listing plugins, retrieving schemas, validating input, and generating documents.

---

## API Base URL

```
http://localhost:8000
```

For production, replace with the actual deployment URL.

---

## Authentication

**Current Strategy: NONE**

The API does not currently require authentication. All endpoints are publicly accessible. For production deployment, consider implementing:
- API Key header (`X-API-Key`)
- JWT Bearer token
- OAuth 2.0

---

## CORS Configuration

The API allows all origins (`*`) in development. For production:
- Configure specific allowed origins
- Set `credentials: true` only when needed
- Restrict methods to those actually used

---

## API Endpoints

### 1. Health Check

```http
GET /health
```

**Response:**
```json
{
  "status": "healthy",
  "version": "1.0.0"
}
```

---

### 2. List Plugins

```http
GET /plugins
```

**Response:**
```json
{
  "plugins": [
    {
      "plugin_id": "pt_review",
      "name": "Transfer Pricing Review Report",
      "description": "Generates a comprehensive transfer pricing audit review report...",
      "version": "1.0.0",
      "language": "es"
    }
  ],
  "count": 1
}
```

**Frontend Action:** Display a plugin selector dropdown.

---

### 3. Get Plugin Schema

```http
GET /plugins/{plugin_id}/schema
```

**Response:**
```json
{
  "plugin_id": "pt_review",
  "fields": [
    {
      "name": "fecha_fin_fiscal",
      "type": "date",
      "label": "Fecha fin del ejercicio fiscal",
      "required": true,
      "description": "Fecha de cierre del ejercicio fiscal auditado",
      "multiline": false,
      "condition": null,
      "values": null,
      "validation": {"min_year": 2000, "max_year": 2099},
      "item_schema": null
    },
    {
      "name": "master_file",
      "type": "enum",
      "label": "Acceso al Master File",
      "required": true,
      "values": [
        {"value": 0, "label": "No hay acceso"},
        {"value": 1, "label": "Hay acceso"}
      ]
    },
    {
      "name": "documentacion_facilitada",
      "type": "list",
      "label": "Documentación facilitada",
      "item_schema": null
    }
  ],
  "ui_sections": [
    {
      "id": "sec_general",
      "label": "Información General",
      "fields": ["fecha_fin_fiscal", "entidad_cliente", "master_file", "descripcion_actividad"]
    }
  ]
}
```

**Field Types:**
- `text` - Single-line or multi-line text input
- `date` - Date picker (ISO format: YYYY-MM-DD)
- `currency` - Numeric input for money values (EUR)
- `int` / `decimal` - Numeric inputs
- `enum` - Select/dropdown with predefined values
- `bool` - Checkbox/toggle
- `list` - Dynamic array of items (add/remove rows)

**Conditional Fields:**
Some fields have a `condition` property (e.g., `"master_file == 1"`). Only show/require these fields when the condition is met.

**Frontend Action:** Dynamically render a form based on the schema. Group fields by `ui_sections` if provided.

---

### 4. Validate Input

```http
POST /plugins/{plugin_id}/validate
Content-Type: application/json

{
  "data": {
    "fecha_fin_fiscal": "2025-12-31",
    "entidad_cliente": "Example Company S.L.",
    "master_file": 1,
    ...
  }
}
```

**Response:**
```json
{
  "is_valid": true,
  "errors": [],
  "warnings": ["Field 'texto_anexo3' is empty"]
}
```

**Frontend Action:** Display validation errors/warnings before allowing generation.

---

### 5. Generate Document

```http
POST /plugins/{plugin_id}/generate
Content-Type: application/json

{
  "data": {
    "fecha_fin_fiscal": "2025-12-31",
    "entidad_cliente": "Example Company S.L.",
    "master_file": 1,
    ...
  },
  "validate": true,
  "strict_validation": false,
  "apply_cell_colors": true
}
```

**Response:**
```json
{
  "success": true,
  "output_path": "/path/to/output/PT_Review_Example_Company_20251231_143022.docx",
  "trace_id": "550e8400-e29b-41d4-a716-446655440000",
  "trace_file": "/path/to/logs/trace_550e8400-e29b-41d4-a716-446655440000.json",
  "validation": {
    "is_valid": true,
    "errors": [],
    "warnings": []
  },
  "decision_traces": [
    {
      "decision_id": "d1_master_file_access",
      "decision_name": "Master File Access Decision",
      "rule_hits": [
        {
          "rule_id": "r001",
          "rule_name": "Show Master File No Access Block",
          "condition_met": false,
          "action_type": "include_text",
          "source_block_ids": ["SEC1_TEXTBLOCK_01"]
        }
      ]
    }
  ],
  "error": null,
  "duration_ms": 1234
}
```

**Frontend Action:**
1. Show success/error message
2. Provide download link using the filename from `output_path`
3. Optionally display decision trace for debugging

---

### 6. Download Document

```http
GET /download/{filename}
```

**Response:** Binary file download (DOCX)

**Frontend Action:** Create a download link/button:
```javascript
const filename = result.output_path.split('/').pop();
window.location.href = `${API_BASE}/download/${filename}`;
```

---

## Frontend Implementation Guide

### 1. Form Rendering

```javascript
async function renderForm(pluginId) {
  const response = await fetch(`${API_BASE}/plugins/${pluginId}/schema`);
  const schema = await response.json();

  const form = document.getElementById('form-container');
  form.innerHTML = '';

  // Group by sections if available
  if (schema.ui_sections.length > 0) {
    for (const section of schema.ui_sections) {
      const sectionEl = createSection(section.label);
      for (const fieldName of section.fields) {
        const field = schema.fields.find(f => f.name === fieldName);
        if (field) {
          sectionEl.appendChild(createFieldInput(field));
        }
      }
      form.appendChild(sectionEl);
    }
  } else {
    // Render all fields flat
    for (const field of schema.fields) {
      form.appendChild(createFieldInput(field));
    }
  }
}

function createFieldInput(field) {
  // Handle different field types
  switch (field.type) {
    case 'text':
      return field.multiline ? createTextarea(field) : createInput(field);
    case 'date':
      return createDatePicker(field);
    case 'enum':
      return createSelect(field);
    case 'currency':
    case 'decimal':
    case 'int':
      return createNumberInput(field);
    case 'bool':
      return createCheckbox(field);
    case 'list':
      return createDynamicList(field);
    default:
      return createInput(field);
  }
}
```

### 2. Dynamic List Fields

For `list` type fields, implement add/remove row functionality:

```javascript
function createDynamicList(field) {
  const container = document.createElement('div');
  container.className = 'list-field';
  container.dataset.fieldName = field.name;

  const addButton = document.createElement('button');
  addButton.textContent = '+ Add Item';
  addButton.onclick = () => addListItem(container, field);

  container.appendChild(addButton);
  return container;
}

function addListItem(container, field) {
  const item = document.createElement('div');
  item.className = 'list-item';

  if (field.item_schema) {
    // Complex object with subfields
    for (const [subName, subDef] of Object.entries(field.item_schema)) {
      item.appendChild(createFieldInput({
        name: subName,
        ...subDef
      }));
    }
  } else {
    // Simple string list
    const input = document.createElement('input');
    input.type = 'text';
    item.appendChild(input);
  }

  const removeBtn = document.createElement('button');
  removeBtn.textContent = 'X';
  removeBtn.onclick = () => item.remove();
  item.appendChild(removeBtn);

  container.insertBefore(item, container.lastChild);
}
```

### 3. Conditional Fields

Handle conditional visibility:

```javascript
function evaluateCondition(condition, formData) {
  if (!condition) return true;

  // Parse simple conditions like "master_file == 1"
  const match = condition.match(/(\w+)\s*==\s*(\d+|true|false|"[^"]*")/);
  if (match) {
    const [, field, value] = match;
    const actualValue = formData[field];
    const expectedValue = JSON.parse(value);
    return actualValue === expectedValue;
  }
  return true;
}

function updateFieldVisibility(formData) {
  document.querySelectorAll('[data-condition]').forEach(el => {
    const condition = el.dataset.condition;
    el.style.display = evaluateCondition(condition, formData) ? '' : 'none';
  });
}
```

### 4. Form Submission

```javascript
async function submitForm(pluginId) {
  const formData = collectFormData();

  // Validate first
  const validateResponse = await fetch(`${API_BASE}/plugins/${pluginId}/validate`, {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({data: formData})
  });
  const validation = await validateResponse.json();

  if (!validation.is_valid) {
    showErrors(validation.errors);
    return;
  }

  // Generate
  const generateResponse = await fetch(`${API_BASE}/plugins/${pluginId}/generate`, {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({
      data: formData,
      validate: true,
      strict_validation: false,
      apply_cell_colors: true
    })
  });
  const result = await generateResponse.json();

  if (result.success) {
    showSuccess(result);
    offerDownload(result.output_path);
  } else {
    showError(result.error);
  }
}
```

---

## Data Format Requirements

### Date Fields
Format: `YYYY-MM-DD` (ISO 8601)
```javascript
const date = "2025-12-31";
```

### Currency Fields
Send as numeric values (not formatted strings):
```javascript
const amount = 1500000.00;  // Not "1.500.000,00 €"
```

### Enum Fields
Send the value, not the label:
```javascript
const masterFile = 1;  // Not "Hay acceso"
```

### List Fields
Send as arrays:
```javascript
const documentos = [
  {"value": "Local File 2024"},
  {"value": "Financial Statements 2024"}
];
```

---

## Error Handling

```javascript
async function apiCall(url, options = {}) {
  try {
    const response = await fetch(url, options);
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.error || 'API Error');
    }
    return await response.json();
  } catch (error) {
    console.error('API Error:', error);
    showNotification(error.message, 'error');
    throw error;
  }
}
```

---

## File Upload Rules

Currently, the API does not support file uploads. All data is sent as JSON. Template files are managed server-side.

---

## Recommended UI Components

1. **Plugin Selector** - Dropdown to select active plugin
2. **Dynamic Form** - Rendered from schema with sections
3. **Validation Panel** - Show errors/warnings
4. **Generate Button** - Trigger document generation
5. **Download Section** - Link to download generated document
6. **Trace Viewer** - Optional debug panel showing decision trace

---

## Example HTML Structure

```html
<!DOCTYPE html>
<html>
<head>
  <title>Document Generator</title>
  <style>
    .section { border: 1px solid #ccc; padding: 1rem; margin: 1rem 0; }
    .field { margin: 0.5rem 0; }
    .field label { display: block; font-weight: bold; }
    .field input, .field select, .field textarea { width: 100%; }
    .required label::after { content: " *"; color: red; }
    .error { color: red; padding: 0.5rem; background: #fee; }
    .success { color: green; padding: 0.5rem; background: #efe; }
    .list-item { display: flex; gap: 0.5rem; margin: 0.25rem 0; }
  </style>
</head>
<body>
  <h1>Document Generator</h1>

  <div id="plugin-selector">
    <label>Select Plugin:</label>
    <select id="plugin-select" onchange="loadPlugin(this.value)"></select>
  </div>

  <div id="form-container"></div>

  <div id="actions">
    <button onclick="validateForm()">Validate</button>
    <button onclick="generateDocument()">Generate Document</button>
  </div>

  <div id="validation-panel"></div>
  <div id="result-panel"></div>

  <script src="app.js"></script>
</body>
</html>
```

---

## Testing

Test the API endpoints using curl:

```bash
# List plugins
curl http://localhost:8000/plugins

# Get schema
curl http://localhost:8000/plugins/pt_review/schema

# Validate
curl -X POST http://localhost:8000/plugins/pt_review/validate \
  -H "Content-Type: application/json" \
  -d '{"data": {"entidad_cliente": "Test Corp"}}'

# Generate
curl -X POST http://localhost:8000/plugins/pt_review/generate \
  -H "Content-Type: application/json" \
  -d '{"data": {...}, "validate": true}'
```

---

## Summary Checklist

- [ ] Fetch and display plugin list
- [ ] Dynamically render form from schema
- [ ] Handle all field types (text, date, enum, currency, list, bool)
- [ ] Implement conditional field visibility
- [ ] Implement dynamic list add/remove
- [ ] Validate before generation
- [ ] Display validation errors/warnings
- [ ] Generate document and show result
- [ ] Provide download link
- [ ] Handle API errors gracefully
