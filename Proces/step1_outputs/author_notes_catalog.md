# Author Notes Catalog (PATCHED)

Generated: 2025-12-31 | Step 1 - Template Normalization
Source: Plantilla_1231.docx
Status: All AI_NOTE content extracted; TEXT_BLOCK IDs fixed and converted to Jinja conditionals

---

## Overview

This catalog extracts all `[AI_NOTE]...[/AI_NOTE]` and `[TEXT_BLOCK: id]...[/TEXT_BLOCK]` annotations from the template, preserving the verbatim text and documenting their location and referenced elements.

---

## AI_NOTE Annotations

### note_01: Cover Page Variables

| Field | Value |
|-------|-------|
| note_id | `note_01` |
| location | Cover page, P5-P12 |
| source_block_id | COVER_NOTE_01 |
| referenced_vars | `fecha_fin_fiscal`, `Entidad_cliente` |
| referenced_blocks | COVER_TITLE, COVER_SUBTITLE_01 |

**Extracted Text (Verbatim):**
```
[AI_NOTE]
- {{fecha_fin_fiscal}} es una fecha mostrada en formato largo.
Ejemplo: "31 de diciembre de 2025".
- {{Entidad_cliente}} corresponde al nombre legal de la compañía.
Ejemplo: "UNIMA Distribución de Productos Congelados, S.A.U."
- Los ejemplos son ilustrativos y no deben convertirse en valores fijos.
- El formato de fecha largo deberá definirse en logic.yaml / formatting rules.
[/AI_NOTE]
```

**Key Information:**
- `fecha_fin_fiscal`: Date displayed in Spanish long format (e.g., "31 de diciembre de 2025")
- `Entidad_cliente`: Legal company name
- Examples are illustrative only
- Date formatting should be defined in logic.yaml

---

### note_02: Master File No Access Condition

| Field | Value |
|-------|-------|
| note_id | `note_02` |
| location | Section 1, P32-P39 |
| source_block_id | SEC1_NOTE_02 |
| referenced_vars | `Master_file` |
| referenced_blocks | SEC1_TEXTBLOCK_01 (master_file_no_acceso) |

**Extracted Text (Verbatim):**
```
[AI_NOTE]
- Este bloque de texto es condicional.
- Solo debe incluirse cuando Master_file == 0 (no hay acceso al Master File).
- Cuando Master_file != 0, este bloque NO debe mostrarse.
- Durante la fase de generación, este texto debe exportarse a texts.yaml
con el identificador: master_file_no_acceso
y vincularse mediante logic.yaml a la condición Master_file == 0.
[/AI_NOTE]
```

**Key Information:**
- Conditional block: show only when `master_file == 0`
- Export to texts.yaml with ID `master_file_no_acceso`
- Link via logic.yaml

---

### note_03: Derived Variable anyo_ejercicio

| Field | Value |
|-------|-------|
| note_id | `note_03` |
| location | Section 1, P41-P46 |
| source_block_id | SEC1_NOTE_03 |
| referenced_vars | `anyo_ejecicio`, `fecha_fin_fiscal` |
| referenced_blocks | SEC1_PARA_02 |

**Extracted Text (Verbatim):**
```
[AI_NOTE]
- La variable {{anyo_ejecicio}} no es un dato introducido manualmente.
- Su valor debe calcularse automáticamente a partir de la variable fecha_fin_fiscal.
- Regla: anyo_ejecicio = año(fecha_fin_fiscal).
- Este vínculo debe reflejarse en logic.yaml como un campo derivado.
[/AI_NOTE]
```

**Key Information:**
- `anyo_ejecicio` (typo: should be `anyo_ejercicio`) is NOT user input
- Derived: `anyo_ejercicio = YEAR(fecha_fin_fiscal)`
- Must be reflected in logic.yaml as derived field

---

### note_04: documentacion_facilitada List

| Field | Value |
|-------|-------|
| note_id | `note_04` |
| location | Section 1, P56-P65 |
| source_block_id | SEC1_NOTE_04 |
| referenced_vars | `documentacion_facilitada` |
| referenced_blocks | SEC1_LIST_DOC |

**Extracted Text (Verbatim):**
```
[AI_NOTE]
- La viñeta {{documentacion_facilitada}} representa una lista dinámica de documentos.
- En la UI se pedirá al usuario introducir una lista "documentaciones"
(conceptualmente: doc_1, doc_2, doc_3, ...).
- En la plantilla definitiva, esta viñeta debe repetirse una vez por cada elemento de dicha lista.
- Ejemplo de un elemento de la lista:
"Documentación de contribuyente en materia de precios de transferencia o Local File de la Compañía relativo al ejercicio finalizado el 31 de diciembre de 2023".
- La lógica para generar el texto final con separadores ";", "y" en el último elemento
se implementará en la fase de generación (YAML + plantilla Jinja), no en este borrador.
[/AI_NOTE]
```

**Key Information:**
- Dynamic list of documents
- UI collects list items
- Template repeats bullet for each item
- Separators (";", "y" before last) handled in generation phase

---

### note_05: servicios_vinculados List (Table 1)

| Field | Value |
|-------|-------|
| note_id | `note_05` |
| location | Section 1, P69-P73 |
| source_block_id | SEC1_NOTE_05 |
| referenced_vars | `servicio_vinculado` |
| referenced_tables | table_01_operaciones_intragrupo |

**Extracted Text (Verbatim):**
```
[AI_NOTE]
- Esta fila representa una lista dinámica de servicios vinculados
- La fila se repite según el número de servicios introducidos por el usuario
- Cada elemento corresponde conceptualmente a: servicio_vinculante_1, servicio_vinculante_2, ...
[/AI_NOTE]
```

**Key Information:**
- Dynamic row repeat for linked services
- User inputs number of services

---

### note_06: descripcion_actividad Variable

| Field | Value |
|-------|-------|
| note_id | `note_06` |
| location | Section 2, P78-P80 |
| source_block_id | SEC2_NOTE_06 |
| referenced_vars | `Descripción_actividad` |
| referenced_blocks | SEC2_PARA_01 |

**Extracted Text (Verbatim):**
```
[AI_NOTE]
Descripción actividad es una variable simple de tipo texto libre.
[/AI_NOTE]
```

**Key Information:**
- `descripcion_actividad` is free-text input

---

### note_07: Table 2 Derived Variables

| Field | Value |
|-------|-------|
| note_id | `note_07` |
| location | Section 2, P83-P93 |
| source_block_id | SEC2_NOTE_07 |
| referenced_vars | `anyo_ejercicio_ant`, `total_costes_op`, `OM`, `NCP`, `EBIT`, `cifra_de_negocio` |
| referenced_tables | table_02_situacion_negocio |

**Extracted Text (Verbatim):**
```
[AI_NOTE]
- Algunas partidas de la tabla no son datos introducidos por el usuario,
sino variables derivadas que deben calcularse automáticamente.
-variable año ejercicio ant se da automáticamente año ejercicio-1
-Las relaciones son:
- total_costes_op = cifra_de_negocio − EBIT
- operating_margin (OM) = EBIT / cifra_de_negocio
- net_cost_plus (NCP) = EBIT / total_costes_op
- Estas fórmulas se implementarán en logic.yaml,
y los valores mostrados en la tabla deben ser el resultado de dichos cálculos.
[/AI_NOTE]
```

**Key Information:**
- `anyo_ejercicio_ant = anyo_ejercicio - 1`
- `total_costes_op = cifra_de_negocio - EBIT`
- `OM = EBIT / cifra_de_negocio`
- `NCP = EBIT / total_costes_op`
- Formulas in logic.yaml

---

### note_08: Table 3 Nested Structure

| Field | Value |
|-------|-------|
| note_id | `note_08` |
| location | Section 2, P96-P107 |
| source_block_id | SEC2_NOTE_08 |
| referenced_vars | `servicio_vinculado`, `entidad_vinculada`, `ingreso`, `gasto`, `total_ingreso_oov`, `total_gasto_oov`, `peso_oov_sobre_incn`, `peso_oov_sobre_costes` |
| referenced_tables | table_03_operaciones_vinculadas |

**Extracted Text (Verbatim):**
```
[AI_NOTE]
- Esta tabla reutiliza los mismos servicios que la tabla anterior.
- Nivel 1: servicio_vinculado.
- Nivel 2: cada servicio puede tener una o varias entidades vinculadas.
- Para cada entidad vinculada se deben introducir ingreso y gasto del ejercicio.
- Cada fila pertenece a un servicio y una entidad concreto.
- Los totales y pesos son agregados globales (sobre todos los servicios y entidades).
- Se calculan a partir de todos los ingresos y gastos introducidos en esta tabla.
-Peso oovv sobre INCN se calcula: total ingreso oovv/cifra de negocio del ejercicio
-Peso oovv sobre total costes se calcula: total gasto oovv/total costes operativos del ejercicio
[/AI_NOTE]
```

**Key Information:**
- Nested structure: Service → Entities
- Per entity: ingreso + gasto
- Aggregates: total_ingreso_oov, total_gasto_oov
- `peso_oov_sobre_incn = total_ingreso_oov / cifra_1`
- `peso_oov_sobre_costes = total_gasto_oov / cost_1`

---

### note_09: Service Analysis Block

| Field | Value |
|-------|-------|
| note_id | `note_09` |
| location | Section 2, P115-P127 |
| source_block_id | SEC2_NOTE_09 |
| referenced_vars | `texto_intro_servicio`, `Descripcion_tabla`, `texto_conclusion_servicio` |
| referenced_blocks | SEC2_SERVICE_TITLE, SEC2_SERVICE_INTRO, etc. |
| referenced_tables | table_04_analisis_servicio |

**Extracted Text (Verbatim):**
```
[AI_NOTE]
- Este bloque corresponde al análisis de un servicio OOVV concreto.
- El usuario podrá decidir si este servicio debe analizarse o no.
- Si el servicio está activado:
- deberá introducir texto libre en los campos:
- texto_intro_servicio
- Descripcion de tabla
- dato de la tabla, aquí esta el diseño de la tabla y sus variables asociados.

- texto_conclusion_servicio
- Si el servicio NO está activado, el bloque completo no debe aparecer en el informe.
- La activación del bloque se gestionará en logic.yaml mediante un flag por servicio.
[/AI_NOTE]
```

**Key Information:**
- Per-service conditional block
- User decides activation via flag
- If activated: requires texto_intro_servicio, descripcion_tabla, table data, texto_conclusion_servicio
- Managed via logic.yaml flag

---

### note_10: Master File Access Condition (Formal Perspective)

| Field | Value |
|-------|-------|
| note_id | `note_10` |
| location | Section 2, P145-P157 |
| source_block_id | SEC2_NOTE_10 |
| referenced_vars | `Master_file`, `tabla_local_file`, `tabla_master_file` |
| referenced_blocks | SEC2_TEXTBLOCK_02, SEC2_TEXTBLOCK_03 |
| referenced_tables | table_05, table_06 |

**Extracted Text (Verbatim):**
```
[AI_NOTE]
- Este bloque de texto es condicional.
- Solo debe incluirse cuando Master_file == 1 (hay acceso al Master File).
- Cuando Master_file != 0, este bloque NO debe mostrarse.
- Durante la fase de generación, este texto debe exportarse a texts.yaml
con el identificador: master_file_no_acceso
y vincularse mediante logic.yaml a la condición Master_file == 0.
- Modelo de las dos tablas, los contenidos son fijos, excepto la columna de ¨cumplimiento¨, se puede elegir entre ¨si¨ y ¨no¨, en caso de si, la casilla es verde, en caso no es una casilla amarilla.
{{tabla_local_file}}

{{tabla_master_file}}

[/AI_NOTE]
```

**Key Information:**
- **INCONSISTENCY**: Says "Master_file == 1" but then "Master_file != 0, este bloque NO debe mostrarse" - contradictory
- Correct interpretation: Show when `master_file == 1`
- Table cumplimiento column: si=green, no=yellow

---

### note_11: Risk Table Enum Values

| Field | Value |
|-------|-------|
| note_id | `note_11` |
| location | Anexo I, P185-P188 |
| source_block_id | ANEXO1_NOTE_11 |
| referenced_vars | `impacto_*`, `afectacion_pre_*`, `afectacion_final_*` |
| referenced_tables | table_07_revision_riesgos |

**Extracted Text (Verbatim):**
```
[AI_NOTE]
- variables "impacto" pueden tomar valores si, no y posible.
- Variables afectación pre y afectación final pueden tomar valores bajo, medio y alto. Si es bajo llena la casilla fondo verde, si es media amariilo, y alto rojo
[/AI_NOTE]
```

**Key Information:**
- `impacto`: enum (si, no, posible)
- `afectacion_pre`, `afectacion_final`: enum (bajo, medio, alto)
- Color coding: bajo=green, medio=yellow, alto=red

---

### note_12: Compliance Tables Enum and Condition

| Field | Value |
|-------|-------|
| note_id | `note_12` |
| location | Anexo II, P198-P202 |
| source_block_id | ANEXO2_NOTE_12 |
| referenced_vars | `cumplido_*`, `texto_cumplido_*`, `master_file` |
| referenced_tables | table_08_cumplimiento_local_file, table_09_cumplimiento_master_file |

**Extracted Text (Verbatim):**
```
[AI_NOTE]
- variables cumplido puede tomar valor si, no o parcial, si es si rellenar el fondo de casilla en verde, posible amarillo, no rojo.
- si la variable cumplido es no o parcial, es obligatorio rellenar texto cumplido
- La segunda tabla esta condicionado a que master_file==1, en caso contrario no se aparece.
[/AI_NOTE]
```

**Key Information:**
- `cumplido`: enum (si, no, parcial)
- Colors: si=green, parcial=yellow, no=red
- Validation: if cumplido in (no, parcial) → texto_cumplido required
- table_09 conditional on `master_file == 1`

---

## TEXT_BLOCK Annotations

### TEXT_BLOCK: master_file_no_acceso

| Field | Value |
|-------|-------|
| text_block_id | `master_file_no_acceso` |
| location | Section 1, P28-P30 |
| source_block_id | SEC1_TEXTBLOCK_01 |
| condition | `master_file == 0` |
| referenced_vars | None in block text |

**Extracted Text (Verbatim):**
```
[TEXT_BLOCK: master_file_no_acceso]
Cabe destacar que la Compañía tiene obligación en el ejercicio auditado, de mantener a disposición de la Administración Tributaria el Master File , a pesar de ello, el Departamento de Precios de Transferencia no ha tenido acceso al mismo y por lo tanto no ha podido realizar su revisión. En el caso de que la Administración solicitase dicha documentación, la Compañía debería estar en disposición de entregarla en el plazo de 10 días (con una extensión adicional de 5 días a petición del contribuyente). En el caso de que la Compañía no proporcionara el Masterfile del Grupo, la Administración podría interponer las sanciones establecidas en el artículo 18.13 de la LIS.
[/TEXT_BLOCK]
```

---

### TEXT_BLOCK: texto_perspectiva_forma_1 (First Instance)

| Field | Value |
|-------|-------|
| text_block_id | `texto_perspectiva_forma_1` |
| location | Section 2, P135-P138 |
| source_block_id | SEC2_TEXTBLOCK_02 |
| condition | Unconditional (always shown) |

**Extracted Text (Verbatim):**
```
[TEXT_BLOCK: texto_perspectiva forma_1]
Tras realizar la revisión de la Documentación Facilitada, en cuanto a su adecuación al cumplimiento de los requisitos establecidos en el Reglamento, el departamento de precios de precios de transferencia de Forvis Mazars concluye que cumple con gran parte de los requisitos formales que el Reglamento prescribe, siguiendo lo dispuesto por el artículo 18.13 de la LIS.
El grado de cumplimiento se encuentra recogido en la siguiente tabla:
Tabla 7. Grado de cumplimiento formal tras la revisión realizada (Local File) [/TEXT_BLOCK]
```

**Issues:**
- **ISSUE**: ID contains space: `texto_perspectiva forma_1` → should be `texto_perspectiva_forma_1`
- Block content includes table caption which may need separation

---

### TEXT_BLOCK: texto_perspectiva_forma_1 (Second Instance - DUPLICATE ID)

| Field | Value |
|-------|-------|
| text_block_id | `texto_perspectiva_forma_1` (DUPLICATE) |
| location | Section 2, P139-P143 |
| source_block_id | SEC2_TEXTBLOCK_03 |
| condition | `master_file == 1` |

**Extracted Text (Verbatim):**
```
[TEXT_BLOCK: texto_perspectiva forma_1]
Tabla 8. Grado de cumplimiento formal tras la revisión realizada (Master File)
Para mayor desglose del cumplimiento por requerimiento acudir a los apéndices.
Por lo tanto, tras la revisión realizada se puede concluir que la Compañía cumple con los requisitos formales establecidos por la normativa en cuanto a la documentación de precios de transferencia.
[/TEXT_BLOCK]
```

**Issues:**
- **CRITICAL**: Duplicate ID `texto_perspectiva forma_1`
- Should be renamed to `texto_perspectiva_forma_2`
- ID contains space
- This block appears to be conditional on `master_file == 1`

---

## Summary

| Type | Count | IDs |
|------|-------|-----|
| AI_NOTE | 12 | note_01 through note_12 |
| TEXT_BLOCK | 3 | master_file_no_acceso, texto_perspectiva_forma_1 (x2 DUPLICATE) |

---

## Issues - ✅ ALL RESOLVED

| Issue ID | Type | Location | Problem | Resolution | Status |
|----------|------|----------|---------|------------|--------|
| NOTE_ISSUE_001 | TEXT_BLOCK | P135, P139 | Duplicate ID `texto_perspectiva forma_1` | Renamed second to `texto_perspectiva_forma_2` | ✅ FIXED |
| NOTE_ISSUE_002 | TEXT_BLOCK | All | Space in ID names | Replaced spaces with underscores | ✅ FIXED |
| NOTE_ISSUE_003 | AI_NOTE | note_10 | Contradictory condition statement | Using `master_file == 1` for showing | ✅ FIXED |

All issues have been resolved in `normalized_template.txt`.
