# Template Diagnostics TODOs (RESOLVED)

Generated: 2025-12-31 | Step 1 - Template Normalization
Source: Plantilla_1231.docx
Status: **ALL ISSUES RESOLVED** - Ready for Step 2

---

## Summary

All 18 issues identified during template analysis have been resolved in `normalized_template.txt`.

---

## 1. Malformed Placeholders - ✅ RESOLVED

### ~~DIAG_001: Missing Closing Brace~~ ✅ FIXED
- **Original**: `{{titulo_servicio_oovv}`
- **Fixed**: `{{ servicio.titulo_servicio_oovv }}` (within loop)
- **Status**: Applied in normalized_template.txt

### ~~DIAG_002: Mixed Variable and Fixed Text in Heading~~ ✅ FIXED
- **Original**: `{{titulo_texto_perspectiva forma}}Conclusiones desde una perspectiva formal`
- **Fixed**: Removed redundant variable; heading is now fixed text only
- **Status**: Applied in normalized_template.txt

---

## 2. Illegal Variable Names - ✅ RESOLVED

### ~~DIAG_003: Variable with Space~~ ✅ FIXED
- **Original**: `{{texto_perspectiva forma_1}}`, `{{texto_perspectiva forma_2}}`
- **Fixed**: Converted to Jinja conditionals with proper content
- **Status**: Applied in normalized_template.txt

### ~~DIAG_004: Variable with Accent~~ ✅ FIXED
- **Original**: `{{Descripción_actividad}}`
- **Fixed**: `{{ descripcion_actividad }}`
- **Status**: Applied in normalized_template.txt

### ~~DIAG_005: Variable Typo (anyo_ejecicio)~~ ✅ FIXED
- **Original**: `{{anyo_ejecicio}}`
- **Fixed**: `{{ anyo_ejercicio }}`
- **Status**: Applied in all occurrences in normalized_template.txt

### ~~DIAG_006: Variable Typo (anyo_ejecicio_ant)~~ ✅ FIXED
- **Original**: `{{anyo_ejecicio_ant}}`
- **Fixed**: `{{ anyo_ejercicio_ant }}`
- **Status**: Applied in normalized_template.txt

### ~~DIAG_007: CamelCase Variables~~ ✅ FIXED
- **Original**: Multiple CamelCase variables
- **Fixed**: All converted to snake_case
- **Status**: Applied in normalized_template.txt

---

## 3. Duplicate TEXT_BLOCK IDs - ✅ RESOLVED

### ~~DIAG_008: Duplicate texto_perspectiva_forma_1~~ ✅ FIXED
- **Original**: Same ID used twice
- **Fixed**: First block → `texto_perspectiva_forma_1`, Second block → `texto_perspectiva_forma_2`
- **Note**: Both blocks converted to inline Jinja conditionals
- **Status**: Applied in normalized_template.txt

---

## 4. Table Design - ✅ RESOLVED

### ~~DIAG_009: Missing Gasto Column in Table 3~~ ✅ FIXED
- **Original**: 3 columns only
- **Fixed**: Added 4th column for `gasto_entidad`
- **Status**: Applied in normalized_template.txt

### ~~DIAG_010: Empty Cumplimiento Cells~~ ✅ CLARIFIED
- **Resolution**: These are user-input enum values (si/no)
- **Status**: Documented in variable_dictionary.md

---

## 5. Ambiguities - ✅ RESOLVED

### ~~DIAG_011: Conflicting AI_NOTE Condition~~ ✅ FIXED
- **Original**: Contradictory condition statements in note_10
- **Fixed**: Using `master_file == 1` for showing Master File content
- **Status**: Applied in normalized_template.txt with `{% if master_file == 1 %}`

### ~~DIAG_012: Anexo III Placeholder Sections~~ ✅ KEPT AS-IS
- **Resolution**: These are structural placeholders for user content
- **Status**: No change needed; documented as template structure

### ~~DIAG_013: Service Block Table Variable~~ ✅ CLARIFIED
- **Resolution**: Table variables are per-service inline data
- **Status**: Applied in normalized_template.txt with service loop

### ~~DIAG_014: UNIMA España Hardcoded Reference~~ ✅ FIXED
- **Original**: "UNIMA España" hardcoded
- **Fixed**: Replaced with `{{ entidad_cliente }}`
- **Status**: Applied in normalized_template.txt

---

## 6. Missing Syntax - ✅ RESOLVED

### ~~DIAG_015: Missing Loop Syntax for Tables~~ ✅ FIXED
- **Fixed**: Added `{% for item in servicios_vinculados %}` to Table 1
- **Fixed**: Added nested loops to Table 3
- **Status**: Applied in normalized_template.txt

### ~~DIAG_016: Missing Service Block Loop~~ ✅ FIXED
- **Fixed**: Added `{% for servicio in servicios_oovv %}{% if servicio.enabled %}...{% endif %}{% endfor %}`
- **Status**: Applied in normalized_template.txt

---

## 7. Formatting - ✅ DOCUMENTED

### ~~DIAG_017: Date Format Specification~~ ✅ DOCUMENTED
- **Resolution**: Spanish long date format documented in variable_dictionary.md
- **Status**: Ready for Step 2 formatting rules

### ~~DIAG_018: Currency Format Not Specified~~ ✅ DOCUMENTED
- **Resolution**: To be specified in Step 2 formatting.yaml
- **Status**: Ready for Step 2

---

## Resolution Summary

| Severity | Total | Resolved |
|----------|-------|----------|
| CRITICAL | 1 | 1 ✅ |
| HIGH | 5 | 5 ✅ |
| MEDIUM | 8 | 8 ✅ |
| LOW | 4 | 4 ✅ |
| **TOTAL** | **18** | **18 ✅** |

---

## Next Steps

All diagnostics have been resolved. The template is ready for Step 2 (YAML Pack Generation).

No remaining TODOs require user input before proceeding.
