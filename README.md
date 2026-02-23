# Enterprise Document Generation Platform

**Version 3.0**

A configuration-driven document generation system for creating professional reports from structured data and Word templates.

**Last Updated:** 2026-02-23

---

## Author

**Yihao Yu**
Consultor en Innovacion e Inteligencia Artificial

Forvis Mazars - Auditoria & Assurance - Sustainability
C/ Diputacio, 260
08007 Barcelona

Email: yihao.yu@mazars.es

---

## Overview

This platform generates DOCX documents by combining:
- **Input data** (JSON) validated by Pydantic contracts
- **Configuration** (YAML plugin packs) defining fields, logic, texts, and tables
- **Templates** (DOCX files with docxtpl placeholders)

The system supports multiple plugin packs, each representing a different document type with its own schema, rules, and template.

## Features

- **Plugin-based architecture**: Add new document types without code changes
- **Controlled DSL**: Safe rule evaluation with allowlisted operators only
- **Dual UI**: Streamlit web app + FastAPI backend
- **Traceability**: Full audit trail of decisions and rule evaluations
- **CI-ready validation**: Validate plugin integrity before deployment
- **Conditional evaluative comments**: 17 si/no toggles for including predefined text blocks
- **Automatic peso OOVV calculation**: Displays peso indicators in Operaciones Vinculadas section
- **Valoración OOVV text field**: User input field for peso-based valuation commentary
- **Template Admin & Versioning**: Upload, validate, publish, and rollback DOCX templates with SemVer versioning and SharePoint integration via Power Automate

## Project Structure

```
project_root/
├── config/
│   ├── yamls/
│   │   └── pt_review/          # Plugin pack
│   │       ├── manifest.yaml
│   │       ├── config.yaml
│   │       ├── fields.yaml
│   │       ├── texts.yaml
│   │       ├── tables.yaml
│   │       ├── logic.yaml
│   │       └── ...
│   └── template_final.docx     # Default document template
├── data/                        # Runtime data (gitignored)
│   ├── template_registry.json   # Template version registry
│   └── templates_cache/         # Cached template versions
│       └── <plugin_id>/
│           └── <version>.docx
├── modules/                     # Core engine
│   ├── plugin_loader.py
│   ├── dsl_allowlist.py
│   ├── contract_models.py
│   ├── contract_validator.py
│   ├── rule_engine.py
│   ├── context_builder.py
│   ├── renderer_docx.py
│   ├── audit_logger.py
│   ├── validate_plugin.py
│   ├── comentarios_valorativos.py  # Conditional evaluative comments
│   ├── template_validator.py    # Template upload validation
│   ├── template_registry.py    # Template versioning & registry
│   ├── sharepoint_publisher.py  # Power Automate SharePoint publisher
│   └── generate.py
├── ui/
│   ├── streamlit_app/          # Streamlit UI
│   │   ├── app.py
│   │   ├── form_renderer.py
│   │   ├── state_store.py
│   │   ├── components.py
│   │   └── template_admin.py   # Template Admin page (⚙️)
│   └── api/
│       ├── backend/            # FastAPI backend
│       │   ├── main.py
│       │   ├── schemas.py
│       │   ├── deps.py
│       │   └── template_admin_routes.py  # Template Admin API
│       ├── ui/                 # Web UI (HTML/CSS/JS)
│       │   ├── index.html
│       │   ├── app.js
│       │   └── styles.css
│       └── instruction.md      # Ubuntu deployment guide
├── scripts/                    # CLI utilities
│   ├── run_validate.py
│   └── run_generate.py
├── tests/                      # Test suite
│   ├── test_validator.py
│   ├── test_rule_engine.py
│   ├── test_golden.py
│   ├── test_template_validator.py  # Template validation tests
│   └── golden/
├── CHANGELOG.md                # Version history
├── requirements.txt            # Python dependencies
└── README.md
```

## Quick Start

### Prerequisites

```bash
# Python 3.10+
pip install -r requirements.txt
```

Or install packages individually:

```bash
pip install pyyaml pydantic docxtpl python-docx streamlit fastapi uvicorn pytest
```

### Run Streamlit UI

```bash
streamlit run ui/streamlit_app/app.py
```

Open http://localhost:8501 in your browser.

### Run FastAPI Backend

```bash
uvicorn ui.api.backend.main:app --reload
```

API available at http://localhost:8000. Docs at http://localhost:8000/docs.

### Validate a Plugin

```bash
python scripts/run_validate.py pt_review

# Validate all plugins
python scripts/run_validate.py --all

# Output as JSON
python scripts/run_validate.py pt_review --json
```

### Generate a Document

```bash
python scripts/run_generate.py pt_review --input tests/golden/sample_input.json

# With custom output path
python scripts/run_generate.py pt_review --input data.json --output report.docx
```

### Run Tests

```bash
pytest tests/ -v
```

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/plugins` | GET | List all available plugins |
| `/plugins/{id}/schema` | GET | Get plugin input schema |
| `/plugins/{id}/validate` | POST | Validate input data |
| `/plugins/{id}/generate` | POST | Generate document |
| `/download/{filename}` | GET | Download generated document |
| `/template/auth` | POST | Authenticate as template admin |
| `/template/validate` | POST | Validate uploaded template (multipart) |
| `/template/publish` | POST | Publish validated template (multipart) |
| `/template/versions/{id}` | GET | List template versions for a plugin |
| `/template/rollback` | POST | Rollback to a specific template version |
| `/template/fields/{id}` | GET | List available template fields |

## Plugin Development

### Creating a New Plugin

1. Create a directory under `config/yamls/<plugin_id>/`
2. Add required YAML files:
   - `manifest.yaml` - Plugin metadata
   - `config.yaml` - UI configuration
   - `fields.yaml` - Input field definitions
   - `texts.yaml` - Fixed text blocks
   - `tables.yaml` - Table schemas
   - `logic.yaml` - Conditional rules
   - `derived.yaml` - Calculated fields
   - `formatting.yaml` - Display formatting
   - `decision_map.yaml` - Governance documentation
   - `refs.yaml` - Traceability index

3. Place template at `config/templates/<plugin_id>/template_final.docx`

4. Validate:
   ```bash
   python scripts/run_validate.py <plugin_id>
   ```

### YAML DSL Operators

Only these operators are allowed in `logic.yaml`:

**Logical:** `and`, `or`, `not`

**Comparison:** `equals`, `not_equals`, `gt`, `gte`, `lt`, `lte`

**Membership:** `in`, `not_in`

**Existence:** `exists`, `not_exists`, `is_empty`, `not_empty`

**String:** `contains`, `not_contains`, `starts_with`, `ends_with`

Maximum nesting depth: 3

### Template Constraints

- Use only `{{ variable }}` placeholders
- Use only single-level loops: `{% for item in list %} ... {% endfor %}`
- No inline conditionals in template - all logic in YAML

## Configuration Reference

### fields.yaml

```yaml
fields:
  field_name:
    type: text|date|enum|currency|int|decimal|bool|list
    required: true|false
    label: "Display label"
    description: "Help text"
    condition: "other_field == 1"  # Conditional requirement
    values: [...]  # For enum type
    item_schema: {...}  # For list type
    validation:
      min_length: 1
      max_length: 500
```

### logic.yaml

```yaml
rules:
  r001:
    rule_id: r001
    name: "Rule description"
    condition:
      operator: equals
      field: some_field
      value: expected_value
    action:
      type: include_text|include_table|require_field
      text_key: text_block_key
```

## Governance

- All inputs validated against Pydantic contracts
- All rules use allowlisted DSL operators
- Full traceability via `refs.yaml` and `decision_map.yaml`
- Audit logs with trace IDs for each generation
- Sensitive fields masked in logs
- Template versioning with SHA-256 integrity hashes
- Password-protected Template Admin access

## Template Admin & Versioning

### Overview

The Template Admin module (v3.0) provides a complete workflow for managing DOCX templates:

1. **Upload** — Upload a new DOCX template for a plugin
2. **Validate** — Automated validation (syntax, variables, rendering, anchors)
3. **Publish** — Version and publish to SharePoint via Power Automate
4. **Rollback** — Revert to any previously published version

### Access

- **Streamlit**: Select "⚙️ Template Admin" from the Navigation dropdown in the sidebar
- **API**: Use the `/template/*` endpoints (see API Endpoints table)
- **Password**: Set via `TEMPLATE_ADMIN_PASSWORD` env var (default: `admin123`)

### Template Resolution Order

When generating documents, templates are resolved in this order:
1. Active version from template registry (local cache)
2. Plugin-specific template (`config/templates/<plugin_id>/template_final.docx`)
3. Legacy fallback (`config/template_final.docx`)

### Validation Checks

| Check | Type | Description |
|-------|------|-------------|
| Jinja2/docxtpl syntax | FAIL | Template must parse without errors |
| Variable consistency | WARN | All template variables must exist in plugin fields |
| Smoke-test rendering | FAIL | Template must render with sample data |
| Residual markers | WARN | Output must not contain `{{` or `{%` |
| Anchor keywords | WARN/FAIL | Required structural keywords must be present |

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `TEMPLATE_ADMIN_PASSWORD` | `admin123` | Admin page access password |
| `POWER_AUTOMATE_TEMPLATE_PUBLISH_URL` | *(required)* | Power Automate HTTP trigger URL |
| `SHAREPOINT_TARGET_ROOT` | `/Templates/Released/` | SharePoint target folder |
| `TEMPLATE_REGISTRY_PATH` | `data/template_registry.json` | Local registry file path |
| `TEMPLATE_CACHE_DIR` | `data/templates_cache/` | Local template cache directory |
| `ALLOW_PUBLISH_WITH_WARNINGS` | `false` | Allow publishing templates with warnings |

### Power Automate Integration

Template publishing uses Power Automate HTTP triggers (no SharePoint App Registration required).

**Request** (API → Power Automate):
```json
{
  "plugin_id": "pt_review",
  "template_name": "template_final",
  "version": "1.2.0",
  "target_folder": "/Templates/Released/pt_review/",
  "files": [
    {"filename": "template_final__1.2.0.docx", "content_base64": "...", "content_type": "application/vnd.openxmlformats-officedocument.wordprocessingml.document"},
    {"filename": "metadata__1.2.0.json", "content_base64": "...", "content_type": "application/json"},
    {"filename": "validation_report__1.2.0.json", "content_base64": "...", "content_type": "application/json"}
  ]
}
```

**Response** (Power Automate → API):
```json
{
  "ok": true,
  "sharepoint": {
    "folder": "/Templates/Released/pt_review/",
    "template_file_url": "https://...",
    "metadata_file_url": "https://...",
    "validation_file_url": "https://...",
    "item_ids": {}
  }
}
```

## Deployment

For production deployment on Ubuntu servers with nginx and systemd, see the comprehensive guide:

```
analisi.md        # Detailed deployment guide with two deployment schemes
ui/api/instruction.md  # Quick reference instructions
```

The `analisi.md` file includes:
- Step-by-step deployment instructions for beginners
- Two deployment schemes (standard and Docker)
- Nginx reverse proxy configuration
- Systemd service configuration
- Performance analysis and capacity planning
- Troubleshooting guide

## License

Proprietary - Forvis Mazars Tax & Legal, S.L.P.

## Support

For issues and feature requests, please contact:

**Yihao Yu** - yihao.yu@mazars.es
Consultor en Innovacion e Inteligencia Artificial
Forvis Mazars - Auditoria & Assurance - Sustainability
