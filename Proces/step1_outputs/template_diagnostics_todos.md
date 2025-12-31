# Template Diagnostics TODOs

Generated: 2025-12-31 | Step 1 - Template Normalization
Source: Plantilla_1231.docx

---

## Overview

This document catalogs all issues, ambiguities, and required decisions identified during template analysis. Each item requires resolution before proceeding to Step 2 (YAML generation).

---

## 1. Malformed Placeholders

### DIAG_001: Missing Closing Brace

| Field | Value |
|-------|-------|
| ID | `DIAG_001` |
| Severity | **HIGH** |
| Location | Section 2, P110 (Heading 3) |
| Original Text | `{{titulo_servicio_oovv}` |
| Problem | Missing closing `}}` brace |
| Fix | `{{ titulo_servicio_oovv }}` |
| Impact | Template rendering will fail without fix |

### DIAG_002: Mixed Variable and Fixed Text in Heading

| Field | Value |
|-------|-------|
| ID | `DIAG_002` |
| Severity | **MEDIUM** |
| Location | Section 2, P129 (Heading 3) |
| Original Text | `{{titulo_texto_perspectiva forma}}Conclusiones desde una perspectiva formal` |
| Problem | Variable immediately followed by fixed text without separator |
| Fix | Separate or clarify: should heading be just the variable or fixed text? |
| Impact | Unclear intent - may cause rendering issues |

---

## 2. Illegal Variable Names (Spaces/Accents/Case)

### DIAG_003: Variable with Space

| Field | Value |
|-------|-------|
| ID | `DIAG_003` |
| Severity | **HIGH** |
| Locations | P129, P130, P133, P135, P139 |
| Original Tokens | `{{titulo_texto_perspectiva forma}}`, `{{texto_perspectiva forma_1}}`, `{{texto_perspectiva forma_2}}` |
| Problem | Space character in variable name |
| Fix | Replace with underscore: `titulo_texto_perspectiva_forma`, `texto_perspectiva_forma_1`, `texto_perspectiva_forma_2` |
| Impact | Variable resolution will fail |

### DIAG_004: Variable with Accent

| Field | Value |
|-------|-------|
| ID | `DIAG_004` |
| Severity | **MEDIUM** |
| Location | Section 2, P77 |
| Original Token | `{{Descripción_actividad}}` |
| Problem | Accented character 'ó' in variable name |
| Fix | `{{ descripcion_actividad }}` |
| Impact | May cause encoding issues |

### DIAG_005: Variable Typo

| Field | Value |
|-------|-------|
| ID | `DIAG_005` |
| Severity | **MEDIUM** |
| Locations | Multiple (P40, P66, P67, P95, P108, P183, P218, etc.) |
| Original Token | `{{anyo_ejecicio}}` |
| Problem | Typo - missing 'r' (should be "ejercicio") |
| Fix | `{{ anyo_ejercicio }}` |
| Impact | Inconsistent naming, may confuse users |

### DIAG_006: Variable Typo (Anterior Year)

| Field | Value |
|-------|-------|
| ID | `DIAG_006` |
| Severity | **MEDIUM** |
| Location | Table 2 header |
| Original Token | `{{anyo_ejecicio_ant}}` |
| Problem | Typo - missing 'r' |
| Fix | `{{ anyo_ejercicio_ant }}` |
| Impact | Inconsistent naming |

### DIAG_007: CamelCase Variables

| Field | Value |
|-------|-------|
| ID | `DIAG_007` |
| Severity | **LOW** |
| Locations | Multiple throughout document |
| Original Tokens | `{{Entidad_cliente}}`, `{{Cost_1}}`, `{{Metodo}}`, `{{Impacto_*}}`, `{{Contacto*}}`, etc. |
| Problem | CamelCase/PascalCase instead of snake_case |
| Fix | Convert all to lowercase snake_case |
| Impact | Inconsistent style, but functional |

---

## 3. Duplicate TEXT_BLOCK IDs

### DIAG_008: Duplicate texto_perspectiva_forma_1

| Field | Value |
|-------|-------|
| ID | `DIAG_008` |
| Severity | **CRITICAL** |
| Locations | P135-P138 (first instance), P139-P143 (second instance) |
| Original ID | `texto_perspectiva forma_1` (appears twice) |
| Problem | Duplicate block ID - will cause conflicts |
| Fix | Rename second instance to `texto_perspectiva_forma_2` |
| Impact | YAML generation will have ambiguous references |

---

## 4. Table Design Mismatches

### DIAG_009: Missing Gasto Column in Table 3

| Field | Value |
|-------|-------|
| ID | `DIAG_009` |
| Severity | **HIGH** |
| Location | Table 3 (Operaciones vinculadas) |
| Problem | AI_NOTE mentions "ingreso y gasto" per entity, but table only shows 3 columns (Tipo, Entidad, Ingreso) |
| Evidence | note_08: "Para cada entidad vinculada se deben introducir ingreso y gasto del ejercicio" |
| Fix Options | (A) Add Gasto column, or (B) Clarify that gasto is implicit/separate input |
| Impact | Derived field `total_gasto_oov` cannot be calculated from visible table data |

### DIAG_010: Empty Cumplimiento Cells in Summary Tables

| Field | Value |
|-------|-------|
| ID | `DIAG_010` |
| Severity | **MEDIUM** |
| Location | Table 5 (Local File summary), Table 6 (Master File summary) |
| Problem | Cumplimiento column cells are empty in original template |
| Question | Should these be user-input enums (si/no) or fixed values? |
| Impact | Unclear data collection requirements |

---

## 5. Ambiguities Requiring User Decision

### DIAG_011: Conflicting AI_NOTE Condition

| Field | Value |
|-------|-------|
| ID | `DIAG_011` |
| Severity | **HIGH** |
| Location | note_10 (P145-P157) |
| Problem | AI_NOTE states both "Master_file == 1" and "Master_file != 0, este bloque NO debe mostrarse" |
| Interpretation | These are contradictory - second statement appears to be a copy-paste error |
| Recommended Fix | Use `master_file == 1` to show the block (Master File accessible) |
| Impact | Incorrect condition will show/hide wrong content |

### DIAG_012: Anexo III Placeholder Sections

| Field | Value |
|-------|-------|
| ID | `DIAG_012` |
| Severity | **MEDIUM** |
| Location | Anexo III, P220-P227 |
| Original Text | "Comentarios valorativos", "Documentación en otro idioma", "Texto del comentario", "Servicios intragrupo", "Texto del comentario", "ETC" |
| Problem | These appear to be placeholder section headers, not actual content |
| Question | Should these be (A) removed, (B) converted to variables, or (C) kept as fixed structure? |
| Impact | Unclear document structure |

### DIAG_013: Service Block Table Variable

| Field | Value |
|-------|-------|
| ID | `DIAG_013` |
| Severity | **LOW** |
| Location | Section 2, P112-P113 |
| Original Tokens | `{{Descripcion_tabla}}`, `{{tabla_analisis_servicio}}` |
| Problem | P112 and P113 both use Tablas style but one is caption, one is table reference |
| Question | Is `tabla_analisis_servicio` meant to be a table reference or inline table data? |
| Impact | Unclear rendering approach |

### DIAG_014: UNIMA España Hardcoded Reference

| Field | Value |
|-------|-------|
| ID | `DIAG_014` |
| Severity | **LOW** |
| Location | Anexo III, P218 |
| Original Text | "...cambios significativos en la política de precios de transferencia de UNIMA España..." |
| Problem | Company name "UNIMA España" is hardcoded instead of using `{{ entidad_cliente }}` |
| Fix | Replace with `{{ entidad_cliente }}` |
| Impact | Incorrect company name in generated document |

---

## 6. Missing Placeholder Detection

### DIAG_015: Missing Loop Syntax for Repeating Rows

| Field | Value |
|-------|-------|
| ID | `DIAG_015` |
| Severity | **MEDIUM** |
| Locations | Table 1, Table 3 template rows |
| Problem | Template shows single row with variables but no Jinja loop syntax |
| Expected | `{% for item in servicios_vinculados %}...{% endfor %}` |
| Impact | Rows won't repeat without explicit loop |

### DIAG_016: Missing Service Block Loop

| Field | Value |
|-------|-------|
| ID | `DIAG_016` |
| Severity | **MEDIUM** |
| Location | Section 2, Conclusions subsection (P110-P127) |
| Problem | Service analysis block needs loop wrapper for multiple services |
| Expected | `{% for servicio in servicios_oovv %}...{% endfor %}` |
| Impact | Only one service will render |

---

## 7. Formatting Specifications

### DIAG_017: Date Format Specification

| Field | Value |
|-------|-------|
| ID | `DIAG_017` |
| Severity | **LOW** |
| Location | Cover page, `fecha_fin_fiscal` |
| Note | note_01 specifies "formato largo" (e.g., "31 de diciembre de 2025") |
| Action | Ensure formatting rule is captured in Step 2 |
| Impact | Incorrect date display if not formatted |

### DIAG_018: Currency Format Not Specified

| Field | Value |
|-------|-------|
| ID | `DIAG_018` |
| Severity | **LOW** |
| Locations | Table 2, Table 3 (financial values) |
| Problem | No explicit formatting rules for currency (EUR) values |
| Question | Should values include thousands separator? Decimal places? € symbol? |
| Impact | Inconsistent currency display |

---

## Summary by Severity

| Severity | Count | IDs |
|----------|-------|-----|
| CRITICAL | 1 | DIAG_008 |
| HIGH | 5 | DIAG_001, DIAG_003, DIAG_009, DIAG_011, DIAG_015 |
| MEDIUM | 8 | DIAG_002, DIAG_004, DIAG_005, DIAG_006, DIAG_010, DIAG_012, DIAG_016, DIAG_018 |
| LOW | 4 | DIAG_007, DIAG_013, DIAG_014, DIAG_017 |

**Total Issues: 18**

---

## Resolution Priority

1. **CRITICAL** - Must fix before Step 2:
   - DIAG_008: Rename duplicate TEXT_BLOCK ID

2. **HIGH** - Should fix before Step 2:
   - DIAG_001: Add missing closing brace
   - DIAG_003: Replace spaces in variable names
   - DIAG_009: Clarify Gasto column requirement
   - DIAG_011: Correct condition logic
   - DIAG_015: Add loop syntax

3. **MEDIUM** - Fix during Step 2:
   - DIAG_002, DIAG_004, DIAG_005, DIAG_006: Variable naming cleanup
   - DIAG_010: Clarify summary table inputs
   - DIAG_012: Decide on Anexo III structure
   - DIAG_016: Add service block loop
   - DIAG_018: Define currency format

4. **LOW** - Can address during implementation:
   - DIAG_007: CamelCase normalization
   - DIAG_013, DIAG_014, DIAG_017: Minor corrections
