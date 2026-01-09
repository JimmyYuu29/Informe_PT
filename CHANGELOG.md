# Changelog

All notable changes to the Informe PT project are documented in this file.

---

## [v2.6] - 2026-01-09

### Changed
- **Word Subdoc Formatting**: Replaced RichText with Subdoc for comentarios valorativos
  - Full Word paragraph formatting now preserved (indentation, list numbering, paragraph spacing)
  - Empty paragraphs/spacing between titles and body text maintained
  - Deep copy of paragraph XML elements ensures exact formatting replication

### Technical
- New `create_comentarios_subdocs(tpl: DocxTemplate)` function in `word_text_extractor.py`
- Cached paragraph elements for performance (Subdocs created fresh per render)
- API change: `build_comentarios_context(data, defs)` → `build_comentarios_context(data, defs, tpl)`
- `context_builder.build_context(data)` → `build_context(data, tpl)` with optional template
- Template loaded before context building in `renderer_docx.py`
- Backwards compatible: falls back to RichText if no template provided
- Updated plugin version to 1.3.0

---

## [v2.5] - 2026-01-09

### Added
- **Word Text Extractor Module** (`modules/word_text_extractor.py`): New module to extract formatted comentarios valorativos from Word document library
  - Preserves formatting (bold, italic, bullet lists) using docxtpl RichText
  - Caches extracted texts for performance optimization
  - Provides both RichText (for document generation) and plain text (for UI preview)

### Changed
- **Comentarios Valorativos**: Now extracted from `config/Text_comentario valorativo.docx` instead of YAML
  - Text content delimited by `{{COMENTARIO_TEXTO_i_START}}` and `{{COMENTARIO_TEXTO_i_END}}` markers
  - YAML config (`comentarios_valorativos.yaml`) now only contains questions/titles
  - Supports 16 conditional evaluative comments
- Updated `modules/comentarios_valorativos.py` to use Word text extraction
- Updated plugin version to 1.2.0

### Technical
- RichText objects preserve Word formatting (bold, italic, bullets) in generated documents
- Text library loaded once per session (cached) for optimal I/O performance
- UI preview continues to show first 3 lines of plain text

---

## [v2.4] - 2026-01-08

### Fixed
- **Streamlit TypeError**: Fixed `TypeError: unsupported operand type(s) for /: 'float' and 'decimal.Decimal'` in peso OOVV calculations by converting float totals to Decimal before division
- **API Operaciones Vinculadas Logic**: Refactored to proper hierarchical structure matching Streamlit version:
  - First add operaciones vinculadas (operation types)
  - Then add entidades vinculadas (linked entities) per operation
  - Each entity has ingreso and gasto fields
  - Totals and peso indicators update automatically

### Changed
- Improved API UI for Operaciones Vinculadas section with clear two-table layout
- Added "Operaciones Intragrupo" table for operation type management
- Added "Detalle de Operaciones Vinculadas" table for entity/amount breakdown
- Enhanced CSS styling for new hierarchical structure

---

## [v2.3] - 2026-01-08

### Added
- Comprehensive deployment guide (`analisi.md`) with Ubuntu/nginx/systemd instructions
- JSON import functionality in API web UI
- Improved layout for tables and forms in API web UI

### Changed
- Simplified JSON export format (removed `_metadata` and `_list_items` wrapper)
- Simplified JSON import to handle flat structure with backwards compatibility
- Reorganized sidebar sections in both Streamlit and API versions
- Updated Data Management UI section (Import/Export/Clear)
- Optimized CSS for full-width table layouts
- Updated API version to 1.1.0

### Fixed
- Left-aligned table layout issues in API web UI
- Text truncation in compliance and risk tables
- Responsive layout for financial data tables

---

## [v2.2] - 2026-01-08

### Added
- Peso OOVV indicators display in Operaciones Vinculadas section:
  - Peso OOVV sobre INCN (automatically calculated)
  - Peso OOVV sobre total costes (automatically calculated)
- New `valoracion_oovv` text field for peso-based valuation commentary
- Comentarios Valorativos section with 16 conditional si/no toggles
- Text preview feature for comentarios valorativos (shows first 3 lines when "si" selected)
- New `comentarios_valorativos.yaml` configuration file
- New `comentarios_valorativos.py` module for processing logic
- API endpoint for comentarios valorativos: `/plugins/{id}/comentarios-valorativos`

### Changed
- Updated plugin version to 1.1.0
- Updated API frontend version to v2.2
- Enhanced Operaciones Vinculadas UI with peso calculation display
- Updated README.md with new features documentation

---

## [v2.1] - 2026-01-05

### Added
- Improved sidebar layout in Streamlit app
- Fixed table layout issues

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
