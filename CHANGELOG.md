# Changelog

All notable changes to the Informe PT project are documented in this file.

---

## [v2.0] - 2026-01-03

### Added
- Author information section in API web UI sidebar
- Table-like form layouts in API matching Streamlit version
- Specialized renderers for Financial Data, Risk Assessment, Compliance tables
- Contacts section with card-based layout
- Version badge (v2.0) in footer
- Ubuntu deployment instructions (`ui/api/instruction.md`)

### Changed
- Consolidated changelog files into single CHANGELOG.md
- Cleaned up repository structure

---

## [v1.3] - 2026-01-03

### Fixed
- JSON import data loss for Informacion General, Datos Financieros, Anexo III, Contactos sections
- Widget state clearing mechanism for complete data import
- JSON export order alignment with UI sections

### Added
- Comprehensive widget key clearing patterns
- Deep copy handling for nested data structures

---

## [v1.2] - 2026-01-03

### Fixed
- Master File Resumen table UI display
- JSON import nested data structure handling
- Export field ordering by UI section

### Added
- `render_cumplimiento_resumen_master_table()` function
- Compliance summary table for Master File (Articulo 15)

---

## [v1.1] - 2026-01-03

### Changed
- Date format from `31-Ene-2025` to `01 de enero del 2025`
- Compliance summary colors: "no" now uses yellow (#FFFF00) instead of red

### Added
- Checkmark replacement for "si" values in compliance fields
- JSON import/export with version 2.0 format
- requirements.txt file

---

## [v1.0] - 2026-01-02

### Initial Release
- Enterprise Document Generation Platform
- Streamlit web UI
- FastAPI REST API
- Plugin-based architecture
- Transfer Pricing Review Report template
- YAML-based field definitions
- Conditional rendering
- Cell coloring for compliance status
- Audit logging

---

## Template Modifications Reference

### Pending Issues (Word Template)

| Priority | Issue | Status |
|----------|-------|--------|
| P0 | Add Gasto column to Table 2 | Pending |
| P1 | Fix `{{anyo_ejercicio}}` spacing | Pending |
| P1 | Fix double-space variables | Pending |

### Resolved Issues

- `anyo_ejecicio` typo corrected
- Variable case normalization (lowercase)
- Loop syntax with `{%tr %}` implemented
- Table numbering with `tabla_num.next()`
- Conditional blocks with `{% if master_file == 1 %}`
- Risk assessment variables (impacto_1 to impacto_12)

---

## Authors

- **Yihao Yu** - Consultor en Innovacion e Inteligencia Artificial
  - Forvis Mazars - Auditoria & Assurance - Sustainability
  - yihao.yu@mazars.es
