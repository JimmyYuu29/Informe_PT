# Enterprise Document Generation Platform

**Version 2.4**

A configuration-driven document generation system for creating professional reports from structured data and Word templates.

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
│   └── template_final.docx     # Document template
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
│   └── generate.py
├── ui/
│   ├── streamlit_app/          # Streamlit UI
│   │   ├── app.py
│   │   ├── form_renderer.py
│   │   ├── state_store.py
│   │   └── components.py
│   └── api/
│       ├── backend/            # FastAPI backend
│       │   ├── main.py
│       │   ├── schemas.py
│       │   └── deps.py
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
