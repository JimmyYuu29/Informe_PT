# Template Patch Plan (APPLIED)

Generated: 2025-12-31 | Step 1 - Template Normalization
Source: Plantilla_1231.docx
Status: **ALL PATCHES APPLIED** - Ready for Step 2

---

## Summary

All 17 patches have been applied to `normalized_template.txt`. The template is now ready for Step 2 YAML generation.

---

## Applied Patches

### ✅ PATCH_001: Fix Missing Closing Brace
- **Location**: Section 2, P110 (Heading 3 style)
- **Original**: `{{titulo_servicio_oovv}`
- **Applied**: `{{ servicio.titulo_servicio_oovv }}` (within loop context)
- **Status**: APPLIED

### ✅ PATCH_002: Rename TEXT_BLOCK ID (First Instance)
- **Location**: Section 2, P135-P138
- **Original**: `[TEXT_BLOCK: texto_perspectiva forma_1]`
- **Applied**: Converted to inline content (space removed)
- **Status**: APPLIED

### ✅ PATCH_003: Rename Duplicate TEXT_BLOCK ID (Second Instance)
- **Location**: Section 2, P139-P143
- **Original**: `[TEXT_BLOCK: texto_perspectiva forma_1]` (duplicate)
- **Applied**: Converted to `{% if master_file == 1 %}...{% endif %}` conditional block
- **Status**: APPLIED

### ✅ PATCH_004: Fix Variable with Space (heading)
- **Location**: Section 2, P129 (Heading 3)
- **Original**: `{{titulo_texto_perspectiva forma}}Conclusiones desde una perspectiva formal`
- **Applied**: Fixed text only: `Conclusiones desde una perspectiva formal`
- **Decision**: Variable was redundant; removed
- **Status**: APPLIED

### ✅ PATCH_005: Fix Variable with Space (texto_perspectiva_forma_1)
- **Location**: Section 2, P130
- **Original**: `{{texto_perspectiva forma_1}}`
- **Applied**: Converted to inline fixed content
- **Status**: APPLIED

### ✅ PATCH_006: Fix Variable with Space (texto_perspectiva_forma_2)
- **Location**: Section 2, P133
- **Original**: `{{texto_perspectiva forma_2}}`
- **Applied**: Converted to conditional inline content
- **Status**: APPLIED

### ✅ PATCH_007: Fix Variable Typo (anyo_ejecicio)
- **Locations**: P40, P66, P67, P95, P108, P183, P218, Table 2 header, Table 3 header
- **Original**: `{{anyo_ejecicio}}`
- **Applied**: `{{ anyo_ejercicio }}` (all 10+ occurrences)
- **Status**: APPLIED

### ✅ PATCH_008: Fix Variable Typo (anyo_ejecicio_ant)
- **Location**: Table 2 header
- **Original**: `{{anyo_ejecicio_ant}}`
- **Applied**: `{{ anyo_ejercicio_ant }}`
- **Status**: APPLIED

### ✅ PATCH_009: Fix Variable with Accent (Descripción_actividad)
- **Location**: Section 2, P77
- **Original**: `{{Descripción_actividad}}`
- **Applied**: `{{ descripcion_actividad }}`
- **Status**: APPLIED

### ✅ PATCH_010: Normalize CamelCase Variables
- **Locations**: Multiple throughout document
- **Applied**: All variables normalized to snake_case:
  - `entidad_cliente`, `cost_*`, `var_*`, `metodo`
  - `impacto_*`, `afectacion_*`, `cumplido_*`, `texto_cumplido_*`
  - `contacto*`, `cargo_contacto*`, `resultado_*`
- **Status**: APPLIED

### ✅ PATCH_011: Fix Hardcoded Company Name
- **Location**: Anexo III, P218
- **Original**: `...la política de precios de transferencia de UNIMA España...`
- **Applied**: `...la política de precios de transferencia de {{ entidad_cliente }}...`
- **Status**: APPLIED

### ✅ PATCH_012: Add Loop Syntax to Table 1
- **Location**: Table 1 (Operaciones intragrupo)
- **Applied**:
```jinja
{% for item in servicios_vinculados %}
| {{ loop.index }} | {{ item.servicio_vinculado }} |
{% endfor %}
```
- **Status**: APPLIED

### ✅ PATCH_013: Add Nested Loop Syntax to Table 3
- **Location**: Table 3 (Operaciones vinculadas)
- **Applied**:
```jinja
{% for servicio in servicios_vinculados %}
{% for entidad in servicio.entidades_vinculadas %}
| {{ servicio.servicio_vinculado }} | {{ entidad.entidad_vinculada }} | {{ entidad.ingreso_entidad }} | {{ entidad.gasto_entidad }} |
{% endfor %}
{% endfor %}
```
- **Status**: APPLIED

### ✅ PATCH_014: Add Service Block Loop
- **Location**: Section 2, Conclusions
- **Applied**:
```jinja
{% for servicio in servicios_oovv %}
{% if servicio.enabled %}
### {{ servicio.titulo_servicio_oovv }}
{{ servicio.texto_intro_servicio }}
{{ servicio.descripcion_tabla }}
[TABLE]
{{ servicio.texto_conclusion_servicio }}
{% endif %}
{% endfor %}
```
- **Status**: APPLIED

### ✅ PATCH_015: Add Gasto Column to Table 3
- **Location**: Table 3
- **Original**: 3 columns (Tipo, Entidad, Ingreso)
- **Applied**: 4 columns (Tipo, Entidad, Ingreso, Gasto)
- **Decision**: Added column per AI_NOTE specification
- **Status**: APPLIED

### ✅ PATCH_016: Remove AI_NOTE Annotations
- **Locations**: 12 AI_NOTE blocks throughout document
- **Applied**: All AI_NOTE content removed from template; preserved in author_notes_catalog.md
- **Status**: APPLIED

### ✅ PATCH_017: Convert TEXT_BLOCK to Jinja Conditionals
- **Locations**: 3 TEXT_BLOCK sections
- **Applied**:
  - `master_file_no_acceso`: `{% if master_file == 0 %}...{% endif %}`
  - `texto_perspectiva_forma_1`: Inline content (unconditional)
  - `texto_perspectiva_forma_2`: `{% if master_file == 1 %}...{% endif %}`
- **Status**: APPLIED

---

## Patch Summary

| Priority | Total | Applied |
|----------|-------|---------|
| P0 - CRITICAL | 3 | 3 ✅ |
| P1 - HIGH | 7 | 7 ✅ |
| P2 - MEDIUM | 4 | 4 ✅ |
| P3 - LOW | 3 | 3 ✅ |
| **TOTAL** | **17** | **17 ✅** |

---

## Decisions Made

| Decision ID | Question | Resolution |
|-------------|----------|------------|
| DEC_001 | Is `titulo_texto_perspectiva_forma` variable needed? | **Removed** - heading is fixed text |
| DEC_002 | Add Gasto column to Table 3? | **Added** - per AI_NOTE requirement |

---

## Template Ready for Step 2

The `normalized_template.txt` now contains:
- All variables in canonical snake_case format
- Proper Jinja2 loop syntax for repeating elements
- Conditional blocks using `{% if %}...{% endif %}`
- Table schemas with correct columns
- All fixed text preserved verbatim
- No AI_NOTE or TEXT_BLOCK markers (converted to actual syntax)

No further patches required before Step 2.
