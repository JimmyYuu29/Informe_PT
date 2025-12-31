# Template Patch Plan

Generated: 2025-12-31 | Step 1 - Template Normalization
Source: Plantilla_1231.docx

---

## Overview

This document provides a detailed patch plan for all modifications required to transform `Plantilla_1231.docx` into a valid docxtpl template (`template_final.docx`). Each patch includes the exact location, original text, target replacement, and reason for change.

**IMPORTANT**: These patches must be applied manually to the Word document before placing it at `config/templates/<plugin_id>/template_final.docx` for Step 2.

---

## Patch Registry

### PATCH_001: Fix Missing Closing Brace

| Field | Value |
|-------|-------|
| patch_id | `PATCH_001` |
| priority | **P0 - CRITICAL** |
| location | Section 2, P110 (Heading 3 style) |
| source_block_id | SEC2_SERVICE_TITLE |
| original_text | `{{titulo_servicio_oovv}` |
| target_text | `{{ titulo_servicio_oovv }}` |
| reason | Missing closing `}}` will cause template parsing error |
| impacted_variables | `titulo_servicio_oovv` |
| impacted_tables | None |
| impacted_conditions | COND_004 (service block activation) |

---

### PATCH_002: Rename Duplicate TEXT_BLOCK ID (First Instance)

| Field | Value |
|-------|-------|
| patch_id | `PATCH_002` |
| priority | **P0 - CRITICAL** |
| location | Section 2, P135-P138 |
| source_block_id | SEC2_TEXTBLOCK_02 |
| original_text | `[TEXT_BLOCK: texto_perspectiva forma_1]` |
| target_text | `[TEXT_BLOCK: texto_perspectiva_forma_1]` |
| reason | Remove space in ID for valid identifier; keep as first instance |
| impacted_variables | None |
| impacted_tables | None |
| impacted_conditions | None |

---

### PATCH_003: Rename Duplicate TEXT_BLOCK ID (Second Instance)

| Field | Value |
|-------|-------|
| patch_id | `PATCH_003` |
| priority | **P0 - CRITICAL** |
| location | Section 2, P139-P143 |
| source_block_id | SEC2_TEXTBLOCK_03 |
| original_text | `[TEXT_BLOCK: texto_perspectiva forma_1]` |
| target_text | `[TEXT_BLOCK: texto_perspectiva_forma_2]` |
| reason | Duplicate ID causes conflict; rename to unique ID and remove space |
| impacted_variables | None |
| impacted_tables | None |
| impacted_conditions | COND_002 (master_file access) |

---

### PATCH_004: Fix Variable with Space (titulo_texto_perspectiva)

| Field | Value |
|-------|-------|
| patch_id | `PATCH_004` |
| priority | **P1 - HIGH** |
| location | Section 2, P129 (Heading 3) |
| source_block_id | SEC2_SUBHEAD_03 |
| original_text | `{{titulo_texto_perspectiva forma}}Conclusiones desde una perspectiva formal` |
| target_text | `Conclusiones desde una perspectiva formal` |
| reason | Variable appears unused/redundant; heading should be fixed text only. If variable IS needed, use `{{ titulo_texto_perspectiva_forma }}` separately |
| impacted_variables | `titulo_texto_perspectiva_forma` (remove or keep as separate) |
| impacted_tables | None |
| impacted_conditions | None |
| decision_required | YES - Confirm if variable is needed or heading is fixed |

---

### PATCH_005: Fix Variable with Space (texto_perspectiva_forma_1)

| Field | Value |
|-------|-------|
| patch_id | `PATCH_005` |
| priority | **P1 - HIGH** |
| location | Section 2, P130 |
| source_block_id | SEC2_TEXTBLOCK_02 content |
| original_text | `{{texto_perspectiva forma_1}}` |
| target_text | `{{ texto_perspectiva_forma_1 }}` |
| reason | Space in variable name is invalid |
| impacted_variables | `texto_perspectiva_forma_1` |
| impacted_tables | None |
| impacted_conditions | None |

---

### PATCH_006: Fix Variable with Space (texto_perspectiva_forma_2)

| Field | Value |
|-------|-------|
| patch_id | `PATCH_006` |
| priority | **P1 - HIGH** |
| location | Section 2, P133 |
| source_block_id | SEC2_TEXTBLOCK_03 content |
| original_text | `{{texto_perspectiva forma_2}}` |
| target_text | `{{ texto_perspectiva_forma_2 }}` |
| reason | Space in variable name is invalid |
| impacted_variables | `texto_perspectiva_forma_2` |
| impacted_tables | None |
| impacted_conditions | None |

---

### PATCH_007: Fix Variable Typo (anyo_ejecicio → anyo_ejercicio)

| Field | Value |
|-------|-------|
| patch_id | `PATCH_007` |
| priority | **P2 - MEDIUM** |
| location | Multiple (P40, P66, P67, P95, P108, P183, P218, Table 2 header, Table 3 header) |
| source_block_id | Multiple |
| original_text | `{{anyo_ejecicio}}` |
| target_text | `{{ anyo_ejercicio }}` |
| reason | Typo - missing 'r' in "ejercicio" |
| impacted_variables | `anyo_ejercicio` (derived from fecha_fin_fiscal) |
| impacted_tables | table_02, table_03 |
| impacted_conditions | None |

**All occurrences to patch:**
1. P40: "...llevadas a cabo durante el Ejercicio {{anyo_ejecicio}}..."
2. P47: "...documentación del Ejercicio {{anyo_ejecicio}}..." (x2)
3. P66: "...tuvieron lugar en el Ejercicio {{anyo_ejecicio}}."
4. P67: "Tabla 1. Identificación de las operaciones intragrupo en el Ejercicio {{anyo_ejecicio}}"
5. P95: "Tabla 3. Operaciones vinculadas llevadas a cabo durante el Ejercicio {{anyo_ejecicio}}"
6. P108: "En el Ejercicio {{anyo_ejecicio}}, los gastos vinculados..."
7. Table 2 header: "Ejercicio {{anyo_ejecicio}} (EUR)"
8. Table 3 header: "Ingreso FY {{anyo_ejecicio}}"
9. P183: "Impacto en Compañía Ejercicio {{anyo_ejecicio}}"
10. P218: "...documentación del Ejercicio {{anyo_ejecicio}}..." (x2)

---

### PATCH_008: Fix Variable Typo (anyo_ejecicio_ant → anyo_ejercicio_ant)

| Field | Value |
|-------|-------|
| patch_id | `PATCH_008` |
| priority | **P2 - MEDIUM** |
| location | Table 2 header |
| source_block_id | SEC2_TABLE_02 |
| original_text | `{{anyo_ejecicio_ant}}` |
| target_text | `{{ anyo_ejercicio_ant }}` |
| reason | Typo - missing 'r' in "ejercicio" |
| impacted_variables | `anyo_ejercicio_ant` (derived) |
| impacted_tables | table_02 |
| impacted_conditions | None |

**Occurrences to patch:**
1. Table 2 header col 2: "Variación {{anyo_ejecicio_ant}}-{{anyo_ejecicio}} (%)"
2. Table 2 header col 4: "Ejercicio {{anyo_ejecicio_ant}} (EUR)"

---

### PATCH_009: Fix Variable with Accent (Descripción_actividad)

| Field | Value |
|-------|-------|
| patch_id | `PATCH_009` |
| priority | **P2 - MEDIUM** |
| location | Section 2, P77 |
| source_block_id | SEC2_PARA_01 |
| original_text | `{{Descripción_actividad}}` |
| target_text | `{{ descripcion_actividad }}` |
| reason | Accented 'ó' and CamelCase; normalize to ASCII snake_case |
| impacted_variables | `descripcion_actividad` |
| impacted_tables | None |
| impacted_conditions | None |

---

### PATCH_010: Normalize CamelCase Variables

| Field | Value |
|-------|-------|
| patch_id | `PATCH_010` |
| priority | **P3 - LOW** |
| location | Multiple throughout document |
| reason | Standardize all variables to lowercase snake_case |
| impacted_variables | Multiple |

**Replacements:**

| Original | Target | Locations |
|----------|--------|-----------|
| `{{Entidad_cliente}}` | `{{ entidad_cliente }}` | P4, P27 |
| `{{Cost_1}}`, `{{Cost_0}}` | `{{ cost_1 }}`, `{{ cost_0 }}` | Table 2 |
| `{{Metodo}}` | `{{ metodo }}` | Table 4 |
| `{{Min}}`, `{{LQ}}`, `{{Med}}`, `{{UQ}}`, `{{Max}}` | `{{ min }}`, `{{ lq }}`, `{{ med }}`, `{{ uq }}`, `{{ max }}` | Table 4 |
| `{{Var_cifra}}`, `{{Var_cost}}`, etc. | `{{ var_cifra }}`, `{{ var_cost }}`, etc. | Table 2 |
| `{{Resultado_fin_*}}` | `{{ resultado_fin_* }}` | Table 2 |
| `{{Resultado_net_*}}` | `{{ resultado_net_* }}` | Table 2 |
| `{{OM_*}}`, `{{NCP_*}}` | `{{ om_* }}`, `{{ ncp_* }}` | Table 2 |
| `{{Impacto_*}}` | `{{ impacto_* }}` | Table 7 |
| `{{Afectacion_Pre_*}}`, `{{Afectacion_final_*}}` | `{{ afectacion_pre_* }}`, `{{ afectacion_final_* }}` | Table 7 |
| `{{Cumplido_Local_*}}`, `{{Cumplido_Mast_*}}` | `{{ cumplido_local_* }}`, `{{ cumplido_mast_* }}` | Tables 8, 9 |
| `{{Texto_Cumplido_*}}` | `{{ texto_cumplido_* }}` | Tables 8, 9 |
| `{{Contacto*}}` | `{{ contacto* }}` | Contacts |
| `{{Cargo_contacto*}}` | `{{ cargo_contacto* }}` | Contacts |
| `{{Descripcion_tabla}}` | `{{ descripcion_tabla }}` | P112 |
| `{{Texto_anexo3}}` | `{{ texto_anexo3 }}` | P217 |

---

### PATCH_011: Fix Hardcoded Company Name

| Field | Value |
|-------|-------|
| patch_id | `PATCH_011` |
| priority | **P3 - LOW** |
| location | Anexo III, P218 |
| source_block_id | ANEXO3_LIST_04 |
| original_text | `...la política de precios de transferencia de UNIMA España, las conclusiones...` |
| target_text | `...la política de precios de transferencia de {{ entidad_cliente }}, las conclusiones...` |
| reason | Company name should use variable, not hardcoded |
| impacted_variables | `entidad_cliente` |
| impacted_tables | None |
| impacted_conditions | None |

---

### PATCH_012: Add Loop Syntax to Table 1

| Field | Value |
|-------|-------|
| patch_id | `PATCH_012` |
| priority | **P1 - HIGH** |
| location | Table 1 (Table 0 in document) |
| source_block_id | SEC1_TABLE_01 |
| original_text | Template row: `{{index}}` \| `{{servicio_vinculado}}` |
| target_text | Add Jinja loop wrapper |
| reason | Rows must repeat for each service |
| target_structure | See normalized_template.txt for loop syntax |
| impacted_variables | `servicios_vinculados[]` |
| impacted_tables | table_01 |
| impacted_conditions | None |

**Target structure:**
```
{% for item in servicios_vinculados %}
| {{ loop.index }} | {{ item.servicio_vinculado }} |
{% endfor %}
```

---

### PATCH_013: Add Loop Syntax to Table 3

| Field | Value |
|-------|-------|
| patch_id | `PATCH_013` |
| priority | **P1 - HIGH** |
| location | Table 3 (Table 2 in document) |
| source_block_id | SEC2_TABLE_03 |
| original_text | Template row: `{{servicio_vinculado}}` \| `{{entidad_vinculada}}` \| `{{ingreso_entidad}}` |
| target_text | Add Jinja nested loop wrapper |
| reason | Rows must repeat for each service × entity combination |
| impacted_variables | `servicios_vinculados[]`, `entidades_vinculadas[]` |
| impacted_tables | table_03 |
| impacted_conditions | None |

**Target structure:**
```
{% for servicio in servicios_vinculados %}
{% for entidad in servicio.entidades_vinculadas %}
| {{ servicio.servicio_vinculado }} | {{ entidad.entidad_vinculada }} | {{ entidad.ingreso_entidad }} |
{% endfor %}
{% endfor %}
```

---

### PATCH_014: Add Service Block Loop

| Field | Value |
|-------|-------|
| patch_id | `PATCH_014` |
| priority | **P1 - HIGH** |
| location | Section 2, Conclusions (P110-P127) |
| source_block_id | SEC2_SERVICE_* |
| original_text | Single service block with variables |
| target_text | Wrap in Jinja for loop with conditional |
| reason | Block must repeat for each enabled service |
| impacted_variables | `servicios_oovv[]` |
| impacted_tables | table_04 |
| impacted_conditions | COND_004 |

**Target structure:**
```
{% for servicio in servicios_oovv %}
{% if servicio.enabled %}
### {{ servicio.titulo_servicio_oovv }}
{{ servicio.texto_intro_servicio }}
{{ servicio.descripcion_tabla }}
[TABLE: table_04_analisis_servicio_{{ loop.index }}]
{{ servicio.texto_conclusion_servicio }}
{% endif %}
{% endfor %}
```

---

### PATCH_015: Add Gasto Column to Table 3 (DECISION REQUIRED)

| Field | Value |
|-------|-------|
| patch_id | `PATCH_015` |
| priority | **P2 - MEDIUM** |
| location | Table 3 (Table 2 in document) |
| source_block_id | SEC2_TABLE_03 |
| original_text | 3 columns: Tipo \| Entidad \| Ingreso |
| target_text | **OPTION A**: 4 columns: Tipo \| Entidad \| Ingreso \| Gasto |
| reason | AI_NOTE mentions both ingreso and gasto, but table only shows ingreso |
| decision_required | YES - Confirm whether to add Gasto column |
| impacted_variables | `gasto_entidad` (new) |
| impacted_tables | table_03 |
| impacted_conditions | None |

**Options:**
- **A**: Add visible Gasto column
- **B**: Keep 3 columns; collect gasto as hidden input for calculations only

---

### PATCH_016: Remove AI_NOTE Annotations

| Field | Value |
|-------|-------|
| patch_id | `PATCH_016` |
| priority | **P1 - HIGH** |
| location | All [AI_NOTE]...[/AI_NOTE] blocks |
| source_block_id | Multiple (note_01 through note_12) |
| original_text | All AI_NOTE content |
| target_text | Remove entirely (already extracted to author_notes_catalog.md) |
| reason | AI_NOTEs are documentation, not template content |
| impacted_variables | None |
| impacted_tables | None |
| impacted_conditions | None |

**Locations to remove:**
1. P5-P12 (note_01)
2. P32-P39 (note_02)
3. P41-P46 (note_03)
4. P56-P65 (note_04)
5. P69-P73 (note_05)
6. P78-P80 (note_06)
7. P83-P93 (note_07)
8. P96-P107 (note_08)
9. P115-P127 (note_09)
10. P145-P157 (note_10)
11. P185-P188 (note_11)
12. P198-P202 (note_12)

---

### PATCH_017: Convert TEXT_BLOCK to Conditional Include

| Field | Value |
|-------|-------|
| patch_id | `PATCH_017` |
| priority | **P1 - HIGH** |
| location | All [TEXT_BLOCK]...[/TEXT_BLOCK] blocks |
| source_block_id | Multiple |
| original_text | TEXT_BLOCK markers and content |
| target_text | Jinja conditional blocks or direct content |
| reason | TEXT_BLOCK is documentation format; final template uses Jinja conditionals |
| impacted_conditions | COND_001, COND_002 |

**Transformations:**

1. `[TEXT_BLOCK: master_file_no_acceso]`:
```jinja
{% if master_file == 0 %}
Cabe destacar que la Compañía tiene obligación...
{% endif %}
```

2. `[TEXT_BLOCK: texto_perspectiva_forma_1]`:
```jinja
Tras realizar la revisión de la Documentación Facilitada...
```
(unconditional - always included)

3. `[TEXT_BLOCK: texto_perspectiva_forma_2]`:
```jinja
{% if master_file == 1 %}
Tabla 8. Grado de cumplimiento formal...
Para mayor desglose del cumplimiento...
{% endif %}
```

---

## Summary

| Priority | Count | Patch IDs |
|----------|-------|-----------|
| P0 - CRITICAL | 3 | PATCH_001, PATCH_002, PATCH_003 |
| P1 - HIGH | 7 | PATCH_004, PATCH_005, PATCH_006, PATCH_012, PATCH_013, PATCH_014, PATCH_016, PATCH_017 |
| P2 - MEDIUM | 4 | PATCH_007, PATCH_008, PATCH_009, PATCH_015 |
| P3 - LOW | 2 | PATCH_010, PATCH_011 |

**Total Patches: 17**

---

## Application Order

1. **Phase 1 - Critical Fixes** (Must complete before Step 2):
   - PATCH_001: Fix missing closing brace
   - PATCH_002: Rename first TEXT_BLOCK ID
   - PATCH_003: Rename second TEXT_BLOCK ID (resolve duplicate)

2. **Phase 2 - High Priority** (Should complete before Step 2):
   - PATCH_004-006: Fix variables with spaces
   - PATCH_012-014: Add loop syntax
   - PATCH_016: Remove AI_NOTE annotations
   - PATCH_017: Convert TEXT_BLOCK to Jinja

3. **Phase 3 - Medium Priority** (Can complete during Step 2):
   - PATCH_007-009: Fix typos and accents
   - PATCH_015: Add Gasto column (pending decision)

4. **Phase 4 - Low Priority** (Optional cleanup):
   - PATCH_010: Normalize CamelCase
   - PATCH_011: Fix hardcoded company name

---

## Decisions Required Before Proceeding

| Decision ID | Patch | Question | Options | Default |
|-------------|-------|----------|---------|---------|
| DEC_001 | PATCH_004 | Is `titulo_texto_perspectiva_forma` variable needed? | A: Remove variable, B: Keep as separate variable | A: Remove (heading is fixed) |
| DEC_002 | PATCH_015 | Add Gasto column to Table 3? | A: Add visible column, B: Hidden input only | A: Add column (DEFAULT) |
