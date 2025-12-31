# Tables Catalog

Generated: 2025-12-31 | Step 1 - Template Normalization
Source: Plantilla_1231.docx

---

## Overview

This catalog documents all tables in the template with their structure, variables, and repeat dimensions.

---

## Table 1: Operaciones Intragrupo

| Field | Value |
|-------|-------|
| table_id | `table_01_operaciones_intragrupo` |
| location | Section 1, after P67 |
| caption | "Tabla 1. Identificación de las operaciones intragrupo en el Ejercicio {{ anyo_ejercicio }}" |
| dimensions | 2 rows × 2 columns (header + 1 template row) |
| repeat_dimension | Row 1 repeats for each `servicio_vinculado` |

### Schema

| Row | Col 0 | Col 1 |
|-----|-------|-------|
| Header | # | Operaciones intragrupo |
| Template | `{{ index }}` | `{{ servicio_vinculado }}` |

### Variables

| canonical_name | original_token | type | scope | description |
|----------------|----------------|------|-------|-------------|
| index | `{{index}}` | int | per-item | Auto-generated row number (1, 2, 3...) |
| servicio_vinculado | `{{servicio_vinculado}}` | text | per-item | Name of linked service type |

### Repeat Logic

```
{% for item in servicios_vinculados %}
| {{ loop.index }} | {{ item.servicio_vinculado }} |
{% endfor %}
```

### Source Note

note_05 (P69-P73): "Esta fila representa una lista dinámica de servicios vinculados"

---

## Table 2: Situación de Negocio

| Field | Value |
|-------|-------|
| table_id | `table_02_situacion_negocio` |
| location | Section 2, after P82 |
| caption | "Tabla 2. Situación de negocio de la Compañía en los Ejercicios 2023, 2022" |
| dimensions | 9 rows × 4 columns |
| repeat_dimension | None (fixed structure) |

### Schema

| Row | Partidas Contables | Variación | Ejercicio Actual | Ejercicio Anterior |
|-----|-------------------|-----------|------------------|-------------------|
| Header | Partidas Contables | Variación {{ anyo_ejercicio_ant }}-{{ anyo_ejercicio }} (%) | Ejercicio {{ anyo_ejercicio }} (EUR) | Ejercicio {{ anyo_ejercicio_ant }} (EUR) |
| 1 | Cifra de negocios | {{ var_cifra }} % | {{ cifra_1 }} | {{ cifra_0 }} |
| 2 | Total costes operativos | {{ var_cost }} % | {{ cost_1 }} | {{ cost_0 }} |
| 3 | EBIT | {{ var_ebit }} % | {{ ebit_1 }} | {{ ebit_0 }} |
| 4 | Resultado Financiero | {{ var_resfin }} % | {{ resultado_fin_1 }} | {{ resultado_fin_0 }} |
| 5 | EBT | {{ var_ebt }} % | {{ ebt_1 }} | {{ ebt_0 }} |
| 6 | Resultado Neto | {{ var_resnet }} % | {{ resultado_net_1 }} | {{ resultado_net_0 }} |
| 7 | Operating Margin (OM) | {{ var_om }} % | {{ om_1 }} | {{ om_0 }} |
| 8 | Net Cost Plus (NCP) | {{ var_ncp }} % | {{ ncp_1 }} | {{ ncp_0 }} |

### Variables

| canonical_name | type | input/derived | derivation_rule |
|----------------|------|---------------|-----------------|
| anyo_ejercicio | int | derived | YEAR(fecha_fin_fiscal) |
| anyo_ejercicio_ant | int | derived | anyo_ejercicio - 1 |
| cifra_1 | currency | input | - |
| cifra_0 | currency | input | - |
| var_cifra | decimal | derived | (cifra_1 - cifra_0) / cifra_0 * 100 |
| cost_1 | currency | derived | cifra_1 - ebit_1 |
| cost_0 | currency | derived | cifra_0 - ebit_0 |
| var_cost | decimal | derived | (cost_1 - cost_0) / cost_0 * 100 |
| ebit_1 | currency | input | - |
| ebit_0 | currency | input | - |
| var_ebit | decimal | derived | (ebit_1 - ebit_0) / ebit_0 * 100 |
| resultado_fin_1 | currency | input | - |
| resultado_fin_0 | currency | input | - |
| var_resfin | decimal | derived | (resultado_fin_1 - resultado_fin_0) / resultado_fin_0 * 100 |
| ebt_1 | currency | input | - |
| ebt_0 | currency | input | - |
| var_ebt | decimal | derived | (ebt_1 - ebt_0) / ebt_0 * 100 |
| resultado_net_1 | currency | input | - |
| resultado_net_0 | currency | input | - |
| var_resnet | decimal | derived | (resultado_net_1 - resultado_net_0) / resultado_net_0 * 100 |
| om_1 | decimal | derived | ebit_1 / cifra_1 |
| om_0 | decimal | derived | ebit_0 / cifra_0 |
| var_om | decimal | derived | om_1 - om_0 (percentage points) |
| ncp_1 | decimal | derived | ebit_1 / cost_1 |
| ncp_0 | decimal | derived | ebit_0 / cost_0 |
| var_ncp | decimal | derived | ncp_1 - ncp_0 (percentage points) |

### Source Note

note_07 (P83-P93): Explains derived variable relationships

---

## Table 3: Operaciones Vinculadas

| Field | Value |
|-------|-------|
| table_id | `table_03_operaciones_vinculadas` |
| location | Section 2, after P95 |
| caption | "Tabla 3. Operaciones vinculadas llevadas a cabo durante el Ejercicio {{ anyo_ejercicio }}" |
| dimensions | 6 rows × 3 columns (header + template row + 4 aggregate rows) |
| repeat_dimension | **Nested**: Row 1 repeats for each (servicio_vinculado, entidad_vinculada) pair |

### Schema

| Row | Tipo de operación vinculada | Entidad vinculada | Ingreso FY |
|-----|----------------------------|-------------------|------------|
| Header | Tipo de operación vinculada | Entidad vinculada | Ingreso FY {{ anyo_ejercicio }} |
| Template | {{ servicio_vinculado }} | {{ entidad_vinculada }} | {{ ingreso_entidad }} |
| Aggregate 1 | Total ingreso oovv | | {{ total_ingreso_oov }} |
| Aggregate 2 | Total gasto oovv | | {{ total_gasto_oov }} |
| Aggregate 3 | Peso oovv sobre INCN | | {{ peso_oov_sobre_incn }} % |
| Aggregate 4 | Peso oovv sobre total costes | | {{ peso_oov_sobre_costes }} % |

### Variables

| canonical_name | type | scope | input/derived | derivation_rule |
|----------------|------|-------|---------------|-----------------|
| servicio_vinculado | text | per-item | input | - |
| entidad_vinculada | text | per-item | input | - |
| ingreso_entidad | currency | per-item | input | - |
| gasto_entidad | currency | per-item | input | (implied, for expense calculation) |
| total_ingreso_oov | currency | global | derived | SUM(ingreso_entidad) |
| total_gasto_oov | currency | global | derived | SUM(gasto_entidad) |
| peso_oov_sobre_incn | decimal | global | derived | total_ingreso_oov / cifra_1 * 100 |
| peso_oov_sobre_costes | decimal | global | derived | total_gasto_oov / cost_1 * 100 |

### Nested Repeat Structure

```
Level 1: servicio_vinculado (e.g., "Servicios de gestión", "Servicios de IT")
  Level 2: entidades_vinculadas[] (e.g., "Entidad A", "Entidad B" for each service)
    Fields: ingreso_entidad, gasto_entidad
```

### Source Note

note_08 (P96-P107): Explains nested structure and aggregate calculations

### TODO

- **TABLE_TODO_001**: Original table only shows 3 columns, but AI_NOTE mentions "gasto" (expense) which is not visible. Clarify whether a Gasto column should be added or if gasto_entidad is implicit.

---

## Table 4: Análisis de Servicio (per-service)

| Field | Value |
|-------|-------|
| table_id | `table_04_analisis_servicio` |
| location | Section 2, Conclusions subsection |
| caption | Variable: `{{ descripcion_tabla }}` |
| dimensions | 2 rows × 6 columns |
| repeat_dimension | Entire table repeats per enabled service |
| condition | Only included if `servicio.enabled == true` |

### Schema

| Row | Método Elegido | Min | LQ | Med | UQ | Max |
|-----|---------------|-----|-----|-----|-----|-----|
| Header | Método Elegido | Min | LQ | Med | UQ | Max |
| Data | {{ metodo }} | {{ min }} % | {{ lq }} % | {{ med }} % | {{ uq }} % | {{ max }} % |

### Variables (per service)

| canonical_name | type | description |
|----------------|------|-------------|
| metodo | text | Selected method name |
| min | decimal | Minimum percentage |
| lq | decimal | Lower quartile percentage |
| med | decimal | Median percentage |
| uq | decimal | Upper quartile percentage |
| max | decimal | Maximum percentage |

### Source Note

note_09 (P115-P127): Explains service block activation

---

## Table 5: Local File Resumen (Summary)

| Field | Value |
|-------|-------|
| table_id | `table_05_local_file_resumen` |
| location | Section 2, Formal Perspective subsection |
| caption | "Tabla 7. Grado de cumplimiento formal tras la revisión realizada (Local File)" |
| dimensions | 4 rows × 3 columns |
| repeat_dimension | None (fixed structure) |

### Schema

| # | Secciones (Artículo 16 del Reglamento) | Cumplimiento |
|---|----------------------------------------|--------------|
| 1 | Información del contribuyente | (enum: si/no) |
| 2 | Información de las operaciones vinculadas | (enum: si/no) |
| 3 | Información económico-financiera del contribuyente | (enum: si/no) |

### Variables

| canonical_name | type | enum_values | formatting |
|----------------|------|-------------|------------|
| cumplimiento_resumen_local_1 | enum | si, no | si=green, no=yellow |
| cumplimiento_resumen_local_2 | enum | si, no | si=green, no=yellow |
| cumplimiento_resumen_local_3 | enum | si, no | si=green, no=yellow |

### TODO

- **TABLE_TODO_002**: Original table has empty Cumplimiento cells. Clarify if these should be user-selectable enum values.

---

## Table 6: Master File Resumen (Summary)

| Field | Value |
|-------|-------|
| table_id | `table_06_master_file_resumen` |
| location | Section 2, Formal Perspective subsection |
| caption | "Tabla 8. Grado de cumplimiento formal tras la revisión realizada (Master File)" |
| dimensions | 5 rows × 3 columns |
| repeat_dimension | None (fixed structure) |
| condition | Only included if `master_file == 1` |

### Schema

| # | Secciones (Artículo 15 del Reglamento) | Cumplimiento |
|---|----------------------------------------|--------------|
| 1 | Información relativa a la estructura y actividades del Grupo | (enum) |
| 2 | Información relativa a los activos intangibles del Grupo | (enum) |
| 3 | Información relativa a la actividad financiera | (enum) |
| 4 | Situación financiera y fiscal del Grupo | (enum) |

### Variables

| canonical_name | type | enum_values | formatting |
|----------------|------|-------------|------------|
| cumplimiento_resumen_mast_1 | enum | si, no | si=green, no=yellow |
| cumplimiento_resumen_mast_2 | enum | si, no | si=green, no=yellow |
| cumplimiento_resumen_mast_3 | enum | si, no | si=green, no=yellow |
| cumplimiento_resumen_mast_4 | enum | si, no | si=green, no=yellow |

---

## Table 7: Revisión de Riesgos

| Field | Value |
|-------|-------|
| table_id | `table_07_revision_riesgos` |
| location | Anexo I, after P183 |
| caption | "Tabla 9. Revisión de elementos identificados como categorías de riesgo en materia de precios de transferencia por parte de la Administración" |
| dimensions | 13 rows × 6 columns (header + 12 data rows) |
| repeat_dimension | None (fixed 12 risk elements) |

### Schema

| # | Elementos de riesgo | Impacto | Nivel Afectación Preliminar | Mitigadores | Nivel Afectación Final |
|---|---------------------|---------|----------------------------|-------------|----------------------|
| 1 | Restructuraciones empresariales | {{ impacto_1 }} | {{ afectacion_pre_1 }} | {{ texto_mitigacion_1 }} | {{ afectacion_final_1 }} |
| 2 | Valoración de transmisiones... | {{ impacto_2 }} | {{ afectacion_pre_2 }} | {{ texto_mitigacion_2 }} | {{ afectacion_final_2 }} |
| ... | ... | ... | ... | ... | ... |
| 12 | Peso de las operaciones vinculadas relevante | {{ impacto_12 }} | {{ afectacion_pre_12 }} | {{ texto_mitigacion_12 }} | {{ afectacion_final_12 }} |

### Fixed Risk Elements (Column 2)

1. Restructuraciones empresariales
2. Valoración de transmisiones intragrupo de distintos activos intangibles
3. Pagos por cánones derivados de la cesión de intangibles
4. Pagos por servicios intragrupo
5. Existencia de pérdidas reiteradas
6. Operaciones financieras entre partes vinculadas
7. Estructuras funcionales de bajo riesgo, tanto en el ámbito de la fabricación como de la distribución
8. Falta de declaración de ingresos intragrupo por las prestaciones de servicios o de cesiones de activos intangibles no repercutidos
9. Erosión de bases imponibles causada por el establecimiento de estructuras en el exterior en las que se remanses beneficios que deben tributar en España
10. Revisión de las formas societarias utilizadas para el desempeño de la actividad económica...
11. Operaciones con establecimientos permanentes
12. Peso de las operaciones vinculadas relevante

### Variables (per row i = 1 to 12)

| canonical_name | type | enum_values | formatting |
|----------------|------|-------------|------------|
| impacto_{i} | enum | si, no, posible | - |
| afectacion_pre_{i} | enum | bajo, medio, alto | bajo=green, medio=yellow, alto=red |
| texto_mitigacion_{i} | text | - | Free text |
| afectacion_final_{i} | enum | bajo, medio, alto | bajo=green, medio=yellow, alto=red |

### Source Note

note_11 (P185-P188): Explains enum values and color formatting

---

## Table 8: Cumplimiento Local File (Detailed)

| Field | Value |
|-------|-------|
| table_id | `table_08_cumplimiento_local_file` |
| location | Anexo II, after P194 |
| caption | "Tabla 10. Grado de cumplimiento formal tras la revisión realizada – Local File" |
| dimensions | 15 rows × 4 columns (header + 14 data rows) |
| repeat_dimension | None (fixed structure based on Artículo 16) |

### Schema

| # | Secciones (Artículo 16 del Reglamento) | Cumplimiento | Comentario |
|---|----------------------------------------|--------------|------------|
| 1 | Estructura de dirección, organigrama... | {{ cumplido_local_1 }} | {{ texto_cumplido_local_1 }} |
| ... | ... | ... | ... |
| 14 | Si, para determinar el valor de mercado... | {{ cumplido_local_14 }} | {{ texto_cumplido_local_14 }} |

### Fixed Section Names (Column 2)

1. Estructura de dirección, organigrama y personas o entidades destinatarias de los informes...
2. Descripción de las actividades del contribuyente, de su estrategia de negocio...
3. Principales competidores
4. Descripción detallada de la naturaleza, características e importe de las operaciones vinculadas
5. Nombre y apellidos o razón social o denominación completa, domicilio fiscal...
6. Análisis de comparabilidad detallado...
7. Explicación relativa a la selección del método de valoración elegido...
8. En su caso, criterios de reparto de gastos en concepto de servicios prestados conjuntamente...
9. Copia de los acuerdos previos de valoración vigentes...
10. Cualquier otra información relevante...
11. Estados financieros anuales del contribuyente
12. Conciliación entre los datos utilizados para aplicar los métodos de precios de transferencia...
13. Datos financieros de los comparables utilizados y fuente de la que proceden
14. Si, para determinar el valor de mercado, se utilizan otros métodos y técnicas de valoración...

### Variables (per row i = 1 to 14)

| canonical_name | type | enum_values | formatting | validation |
|----------------|------|-------------|------------|------------|
| cumplido_local_{i} | enum | si, no, parcial | si=green, parcial=yellow, no=red | - |
| texto_cumplido_local_{i} | text | - | - | Required if cumplido_local_{i} in (no, parcial) |

### Source Note

note_12 (P198-P202): Explains enum values and comment requirement

---

## Table 9: Cumplimiento Master File (Detailed)

| Field | Value |
|-------|-------|
| table_id | `table_09_cumplimiento_master_file` |
| location | Anexo II, after P196 |
| caption | "Tabla 11. Grado de cumplimiento formal tras la revisión realizada – Master File" |
| dimensions | 18 rows × 4 columns (header + 17 data rows) |
| repeat_dimension | None (fixed structure based on Artículo 15) |
| condition | Only included if `master_file == 1` |

### Schema

| # | Secciones (Artículo 15 del Reglamento) | Cumplimiento | Comentario |
|---|----------------------------------------|--------------|------------|
| 1 | Descripción general de la estructura organizativa... | {{ cumplido_mast_1 }} | {{ texto_cumplido_mast_1 }} |
| ... | ... | ... | ... |
| 17 | Relación y breve descripción de los acuerdos previos de valoración vigentes... | {{ cumplido_mast_17 }} | {{ texto_cumplido_mast_17 }} |

### Fixed Section Names (Column 2)

1. Descripción general de la estructura organizativa, jurídica y operativa del grupo...
2. Identificación de las distintas entidades que formen parte del grupo
3. Actividades principales del grupo, así como descripción de los principales mercados geográficos...
4. Descripción general de las funciones ejercidas, riesgos asumidos y principales activos utilizados...
5. Descripción de la política del grupo en materia de precios de transferencia...
6. Relación y breve descripción de los acuerdos de reparto de costes...
7. Descripción de las operaciones de reorganización y de adquisición o cesión de activos relevantes...
8. Descripción general de la estrategia global del grupo en relación al desarrollo, propiedad y explotación de los activos intangibles...
9. Relación de los activos intangibles del grupo relevantes a efectos de precios de transferencia...
10. Importe de las contraprestaciones correspondientes a las operaciones vinculadas del grupo...
11. Relación de acuerdos entre las entidades del grupo relativos a intangibles...
12. Descripción general de cualquier transferencia relevante sobre activos intangibles...
13. Descripción general de la forma de financiación del grupo...
14. Identificación de las entidades del grupo que realicen las principales funciones de financiación...
15. Descripción general de la política de precios de transferencia relativa a los acuerdos de financiación...
16. Estados financieros anuales consolidados del grupo...
17. Relación y breve descripción de los acuerdos previos de valoración vigentes...

### Variables (per row i = 1 to 17)

| canonical_name | type | enum_values | formatting | validation |
|----------------|------|-------------|------------|------------|
| cumplido_mast_{i} | enum | si, no, parcial | si=green, parcial=yellow, no=red | - |
| texto_cumplido_mast_{i} | text | - | - | Required if cumplido_mast_{i} in (no, parcial) |

### Source Note

note_12 (P198-P202): Explains condition and enum values

---

## Summary

| table_id | Location | Rows | Cols | Repeating | Conditional |
|----------|----------|------|------|-----------|-------------|
| table_01 | Section 1 | 2+ | 2 | Yes (rows) | No |
| table_02 | Section 2 | 9 | 4 | No | No |
| table_03 | Section 2 | 6+ | 3 | Yes (nested) | No |
| table_04 | Section 2 | 2 | 6 | Yes (per service) | Yes (per service) |
| table_05 | Section 2 | 4 | 3 | No | No |
| table_06 | Section 2 | 5 | 3 | No | Yes (master_file==1) |
| table_07 | Anexo I | 13 | 6 | No | No |
| table_08 | Anexo II | 15 | 4 | No | No |
| table_09 | Anexo II | 18 | 4 | No | Yes (master_file==1) |

---

## Table TODOs

| TODO_ID | Table | Issue | Impact | Suggested Resolution |
|---------|-------|-------|--------|----------------------|
| TABLE_TODO_001 | table_03 | Missing Gasto column in original | High | Add gasto_entidad column or clarify if implicit |
| TABLE_TODO_002 | table_05/06 | Empty Cumplimiento cells | Medium | Confirm enum input (si/no) vs fixed values |
| TABLE_TODO_003 | table_04 | Caption uses variable `descripcion_tabla` | Low | Ensure variable is input per service |
