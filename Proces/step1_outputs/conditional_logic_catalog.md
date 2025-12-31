# Conditional Logic Catalog (PATCHED)

Generated: 2025-12-31 | Step 1 - Template Normalization
Source: Plantilla_1231.docx
Status: All conditions implemented with proper Jinja2 syntax in normalized_template.txt

---

## Overview

This catalog documents all conditional logic identified in the template, extracted from AI_NOTE annotations and implicit document structure.

---

## Condition Registry

### COND_001: Master File No Access Block

| Field | Value |
|-------|-------|
| condition_id | `COND_001` |
| name | `master_file_no_access` |
| structured_statement | `IF master_file == 0 THEN INCLUDE TEXT_BLOCK "master_file_no_acceso"` |
| variables_involved | `master_file` |
| affected_blocks | `SEC1_TEXTBLOCK_01` (source_block_id) |
| text_block_id | `master_file_no_acceso` |
| source_note | note_02 (P32-P39) |
| precedence | 1 (evaluated early, affects Section 1 content) |

**AI_NOTE Verbatim:**
> - Este bloque de texto es condicional.
> - Solo debe incluirse cuando Master_file == 0 (no hay acceso al Master File).
> - Cuando Master_file != 0, este bloque NO debe mostrarse.

---

### COND_002: Master File Access Block (Formal Perspective)

| Field | Value |
|-------|-------|
| condition_id | `COND_002` |
| name | `master_file_access_formal` |
| structured_statement | `IF master_file == 1 THEN INCLUDE TEXT_BLOCK "texto_perspectiva_forma_2" AND TABLE "table_06_master_file_resumen"` |
| variables_involved | `master_file` |
| affected_blocks | `SEC2_TEXTBLOCK_03`, `SEC2_TABLE_06` |
| text_block_id | `texto_perspectiva_forma_2` |
| source_note | note_10 (P145-P157) |
| precedence | 2 |

**AI_NOTE Verbatim:**
> - Este bloque de texto es condicional.
> - Solo debe incluirse cuando Master_file == 1 (hay acceso al Master File).

---

### COND_003: Master File Table in Anexo II

| Field | Value |
|-------|-------|
| condition_id | `COND_003` |
| name | `master_file_detailed_table` |
| structured_statement | `IF master_file == 1 THEN INCLUDE TABLE "table_09_cumplimiento_master_file"` |
| variables_involved | `master_file` |
| affected_blocks | `ANEXO2_TABLE_09` |
| source_note | note_12 (P198-P202) |
| precedence | 3 |

**AI_NOTE Verbatim:**
> - La segunda tabla esta condicionado a que master_file==1, en caso contrario no se aparece.

---

### COND_004: Service Block Activation

| Field | Value |
|-------|-------|
| condition_id | `COND_004` |
| name | `service_block_activation` |
| structured_statement | `FOR EACH servicio IN servicios_oovv: IF servicio.enabled == true THEN INCLUDE service analysis block` |
| variables_involved | `servicios_oovv[].enabled` |
| affected_blocks | `SEC2_SERVICE_TITLE`, `SEC2_SERVICE_INTRO`, `SEC2_TABLE_CAPTION_04`, `SEC2_TABLE_04`, `SEC2_SERVICE_CONCLUSION` |
| source_note | note_09 (P115-P127) |
| precedence | 4 (per-service evaluation) |

**AI_NOTE Verbatim:**
> - Este bloque corresponde al análisis de un servicio OOVV concreto.
> - El usuario podrá decidir si este servicio debe analizarse o no.
> - Si el servicio está activado:
>   - deberá introducir texto libre en los campos:
>     - texto_intro_servicio
>     - Descripcion de tabla
>     - dato de la tabla, aquí esta el diseño de la tabla y sus variables asociados.
>     - texto_conclusion_servicio
> - Si el servicio NO está activado, el bloque completo no debe aparecer en el informe.
> - La activación del bloque se gestionará en logic.yaml mediante un flag por servicio.

---

### COND_005: Compliance Comment Required

| Field | Value |
|-------|-------|
| condition_id | `COND_005` |
| name | `compliance_comment_required` |
| structured_statement | `FOR EACH cumplido_* variable: IF value IN (no, parcial) THEN REQUIRE texto_cumplido_* to be non-empty` |
| variables_involved | `cumplido_local_*`, `cumplido_mast_*`, `texto_cumplido_local_*`, `texto_cumplido_mast_*` |
| affected_blocks | `ANEXO2_TABLE_08`, `ANEXO2_TABLE_09` |
| source_note | note_12 (P198-P202) |
| precedence | 5 (validation rule) |

**AI_NOTE Verbatim:**
> - si la variable cumplido es no o parcial, es obligatorio rellenar texto cumplido

---

## Derived Variable Rules

### DERIV_001: anyo_ejercicio

| Field | Value |
|-------|-------|
| derived_id | `DERIV_001` |
| target_variable | `anyo_ejercicio` |
| rule | `anyo_ejercicio = YEAR(fecha_fin_fiscal)` |
| source_variables | `fecha_fin_fiscal` |
| source_note | note_03 (P41-P46) |

**AI_NOTE Verbatim:**
> - La variable {{anyo_ejecicio}} no es un dato introducido manualmente.
> - Su valor debe calcularse automáticamente a partir de la variable fecha_fin_fiscal.
> - Regla: anyo_ejecicio = año(fecha_fin_fiscal).
> - Este vínculo debe reflejarse en logic.yaml como un campo derivado.

---

### DERIV_002: anyo_ejercicio_ant

| Field | Value |
|-------|-------|
| derived_id | `DERIV_002` |
| target_variable | `anyo_ejercicio_ant` |
| rule | `anyo_ejercicio_ant = anyo_ejercicio - 1` |
| source_variables | `anyo_ejercicio` |
| source_note | note_07 (P83-P93) |

**AI_NOTE Verbatim:**
> - variable año ejercicio ant se da automáticamente año ejercicio-1

---

### DERIV_003: total_costes_op (Cost_1 / Cost_0)

| Field | Value |
|-------|-------|
| derived_id | `DERIV_003` |
| target_variable | `cost_1`, `cost_0` |
| rule | `total_costes_op = cifra_de_negocio - EBIT` |
| source_variables | `cifra_1`, `ebit_1`, `cifra_0`, `ebit_0` |
| source_note | note_07 (P83-P93) |

---

### DERIV_004: Operating Margin (OM)

| Field | Value |
|-------|-------|
| derived_id | `DERIV_004` |
| target_variable | `om_1`, `om_0` |
| rule | `operating_margin = EBIT / cifra_de_negocio` |
| source_variables | `ebit_1`, `cifra_1`, `ebit_0`, `cifra_0` |
| source_note | note_07 (P83-P93) |

---

### DERIV_005: Net Cost Plus (NCP)

| Field | Value |
|-------|-------|
| derived_id | `DERIV_005` |
| target_variable | `ncp_1`, `ncp_0` |
| rule | `net_cost_plus = EBIT / total_costes_op` |
| source_variables | `ebit_1`, `cost_1`, `ebit_0`, `cost_0` |
| source_note | note_07 (P83-P93) |

---

### DERIV_006: Peso OOVV sobre INCN

| Field | Value |
|-------|-------|
| derived_id | `DERIV_006` |
| target_variable | `peso_oov_sobre_incn` |
| rule | `peso_oov_sobre_incn = total_ingreso_oov / cifra_1 * 100` |
| source_variables | `total_ingreso_oov`, `cifra_1` |
| source_note | note_08 (P96-P107) |

**AI_NOTE Verbatim:**
> - Peso oovv sobre INCN se calcula: total ingreso oovv/cifra de negocio del ejercicio

---

### DERIV_007: Peso OOVV sobre Total Costes

| Field | Value |
|-------|-------|
| derived_id | `DERIV_007` |
| target_variable | `peso_oov_sobre_costes` |
| rule | `peso_oov_sobre_costes = total_gasto_oov / cost_1 * 100` |
| source_variables | `total_gasto_oov`, `cost_1` |
| source_note | note_08 (P96-P107) |

**AI_NOTE Verbatim:**
> - Peso oovv sobre total costes se calcula: total gasto oovv/total costes operativos del ejercicio

---

### DERIV_008: Total Ingreso OOVV

| Field | Value |
|-------|-------|
| derived_id | `DERIV_008` |
| target_variable | `total_ingreso_oov` |
| rule | `total_ingreso_oov = SUM(ingreso_entidad) for all linked entities` |
| source_variables | `servicios_vinculados[].entidades[].ingreso_entidad` |
| source_note | note_08 (P96-P107) |

---

### DERIV_009: Total Gasto OOVV

| Field | Value |
|-------|-------|
| derived_id | `DERIV_009` |
| target_variable | `total_gasto_oov` |
| rule | `total_gasto_oov = SUM(gasto_entidad) for all linked entities` |
| source_variables | `servicios_vinculados[].entidades[].gasto_entidad` |
| source_note | note_08 (P96-P107) |

---

### DERIV_010: Variation Percentages

| Field | Value |
|-------|-------|
| derived_id | `DERIV_010` |
| target_variables | `var_cifra`, `var_cost`, `var_ebit`, `var_resfin`, `var_ebt`, `var_resnet`, `var_om`, `var_ncp` |
| rule | `variation = (value_1 - value_0) / value_0 * 100` (for financial values); `variation = value_1 - value_0` (for OM/NCP percentage points) |
| source_note | Implicit from table structure |

---

## Formatting Rules (Color Coding)

### FORMAT_001: Impacto Enum Colors

| Value | Cell Background |
|-------|-----------------|
| si | (no special color) |
| no | (no special color) |
| posible | (no special color) |

*Note: AI_NOTE does not specify colors for impacto values*

---

### FORMAT_002: Afectacion Enum Colors

| Value | Cell Background |
|-------|-----------------|
| bajo | Green |
| medio | Yellow |
| alto | Red |

Source: note_11 (P185-P188)

---

### FORMAT_003: Cumplido Enum Colors

| Value | Cell Background |
|-------|-----------------|
| si | Green |
| parcial | Yellow |
| no | Red |

Source: note_12 (P198-P202)

---

## Condition Evaluation Order

1. `master_file` value determines:
   - COND_001: Show/hide "no access" block
   - COND_002: Show/hide formal perspective block
   - COND_003: Show/hide Master File compliance table

2. Per-service evaluation:
   - COND_004: For each service, show/hide analysis block

3. Derived values (computed before rendering):
   - DERIV_001 through DERIV_010

4. Validation rules:
   - COND_005: Ensure comments when compliance is partial/no

---

## Ambiguities / TODOs - ✅ ALL RESOLVED

| TODO_ID | Issue | Location | Impact | Resolution | Status |
|---------|-------|----------|--------|------------|--------|
| LOGIC_TODO_001 | Conflicting AI_NOTE for note_10 | P148 | Medium | Using `master_file == 1` for access | ✅ FIXED |
| LOGIC_TODO_002 | Duplicate TEXT_BLOCK ID | P135, P139 | High | Assigned unique IDs: `texto_perspectiva_forma_1` and `texto_perspectiva_forma_2` | ✅ FIXED |
| LOGIC_TODO_003 | Malformed placeholder in service block | P110 | High | Fixed: `{{ servicio.titulo_servicio_oovv }}` | ✅ FIXED |

All logic issues have been resolved in `normalized_template.txt`.
