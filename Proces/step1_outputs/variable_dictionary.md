# Variable Dictionary (PATCHED)

Generated: 2025-12-31 | Step 1 - Template Normalization
Source: Plantilla_1231.docx
Status: All variable names normalized to canonical snake_case format

---

## Variable Naming Convention

- **Canonical names**: snake_case, lowercase, ASCII only, no spaces
- All variables in this dictionary use the CORRECTED canonical format

---

## Global Variables (Single-Value Inputs)

| canonical_name | type | required | scope | appears_in | validation_hints | formatting | derivation_rule |
|----------------|------|----------|-------|------------|------------------|------------|-----------------|
| fecha_fin_fiscal | date | Y | global | COVER_TITLE, headers | ISO date input | Spanish long date format (e.g., "31 de diciembre de 2025") | - |
| entidad_cliente | text | Y | global | COVER_SUBTITLE_01, SEC1_INTRO_PARA, ANEXO3 | Non-empty string | - | - |
| descripcion_actividad | text | Y | global | SEC2_PARA_01 | Free text, multi-paragraph allowed | - | - |
| master_file | enum | Y | global | Conditions | Values: 0, 1 | - | 0 = no access, 1 = access |
| texto_anexo3 | text | N | global | ANEXO3_LIST_03 | Free text | - | - |
| anyo_ejercicio | int | N | global | Multiple paragraphs and tables | 4-digit year | - | **DERIVED**: `year(fecha_fin_fiscal)` |
| anyo_ejercicio_ant | int | N | global | TABLE_02 headers | 4-digit year | - | **DERIVED**: `anyo_ejercicio - 1` |

---

## Contact Variables

| canonical_name | type | required | scope | appears_in | validation_hints |
|----------------|------|----------|-------|------------|------------------|
| contacto1 | text | Y | global | CONTACTS_BLOCK | Person name |
| cargo_contacto1 | text | Y | global | CONTACTS_BLOCK | Job title |
| correo_contacto1 | text | Y | global | CONTACTS_BLOCK | Email format |
| contacto2 | text | Y | global | CONTACTS_BLOCK | Person name |
| cargo_contacto2 | text | Y | global | CONTACTS_BLOCK | Job title |
| correo_contacto2 | text | Y | global | CONTACTS_BLOCK | Email format |
| contacto3 | text | Y | global | CONTACTS_BLOCK | Person name |
| cargo_contacto3 | text | Y | global | CONTACTS_BLOCK | Job title |
| correo_contacto3 | text | Y | global | CONTACTS_BLOCK | Email format |

---

## List Variables (Dynamic Repeating)

### documentacion_facilitada
| Field | Details |
|-------|---------|
| canonical_name | `documentacion_facilitada` |
| type | list[text] |
| required | Y |
| scope | global |
| appears_in | SEC1_LIST_DOC |
| validation_hints | At least 1 item; each item is a document description |
| formatting | Bullet list, semicolons between items, "y" before last item |
| example | "Documentación de contribuyente en materia de precios de transferencia o Local File de la Compañía relativo al ejercicio finalizado el 31 de diciembre de 2023" |

### servicios_vinculados (Table 1 & Table 3 repeat dimension)
| Field | Details |
|-------|---------|
| canonical_name | `servicios_vinculados` |
| type | list[object] |
| required | Y |
| scope | global |
| appears_in | TABLE_01, TABLE_03 |
| item_fields | See below |

**servicios_vinculados item fields:**
| field | type | required | description |
|-------|------|----------|-------------|
| servicio_vinculado | text | Y | Name of linked service type |
| entidades_vinculadas | list[object] | Y | List of linked entities for this service |

**entidades_vinculadas item fields:**
| field | type | required | description |
|-------|------|----------|-------------|
| entidad_vinculada | text | Y | Name of linked entity |
| ingreso_entidad | currency | Y | Income from this entity |
| gasto_entidad | currency | Y | Expense to this entity |

### servicios_oovv (Service Analysis Block Repeat)
| Field | Details |
|-------|---------|
| canonical_name | `servicios_oovv` |
| type | list[object] |
| required | N |
| scope | global |
| appears_in | SEC2_SERVICE_* blocks |
| item_fields | See below |

**servicios_oovv item fields:**
| field | type | required | description |
|-------|------|----------|-------------|
| enabled | bool | Y | Whether to include this service block |
| titulo_servicio_oovv | text | Y | Service title heading |
| texto_intro_servicio | text | Y | Introduction paragraph |
| descripcion_tabla | text | Y | Table description |
| metodo | text | Y | Selected method name |
| min | decimal | Y | Minimum percentage |
| lq | decimal | Y | Lower quartile percentage |
| med | decimal | Y | Median percentage |
| uq | decimal | Y | Upper quartile percentage |
| max | decimal | Y | Maximum percentage |
| texto_conclusion_servicio | text | Y | Conclusion paragraph |

---

## Table 2: Situación de Negocio Variables (Financial Data)

### Current Year (suffix _1)
| canonical_name | type | required | derivation_rule |
|----------------|------|----------|-----------------|
| cifra_1 | currency | Y | User input |
| cost_1 | currency | N | **DERIVED**: `cifra_1 - ebit_1` |
| ebit_1 | currency | Y | User input |
| resultado_fin_1 | currency | Y | User input |
| ebt_1 | currency | Y | User input |
| resultado_net_1 | currency | Y | User input |
| om_1 | decimal | N | **DERIVED**: `ebit_1 / cifra_1` (as %) |
| ncp_1 | decimal | N | **DERIVED**: `ebit_1 / cost_1` (as %) |

### Prior Year (suffix _0)
| canonical_name | type | required | derivation_rule |
|----------------|------|----------|-----------------|
| cifra_0 | currency | Y | User input |
| cost_0 | currency | N | **DERIVED**: `cifra_0 - ebit_0` |
| ebit_0 | currency | Y | User input |
| resultado_fin_0 | currency | Y | User input |
| ebt_0 | currency | Y | User input |
| resultado_net_0 | currency | Y | User input |
| om_0 | decimal | N | **DERIVED**: `ebit_0 / cifra_0` (as %) |
| ncp_0 | decimal | N | **DERIVED**: `ebit_0 / cost_0` (as %) |

### Variation Variables
| canonical_name | type | derivation_rule |
|----------------|------|-----------------|
| var_cifra | decimal | **DERIVED**: `(cifra_1 - cifra_0) / cifra_0 * 100` |
| var_cost | decimal | **DERIVED**: `(cost_1 - cost_0) / cost_0 * 100` |
| var_ebit | decimal | **DERIVED**: `(ebit_1 - ebit_0) / ebit_0 * 100` |
| var_resfin | decimal | **DERIVED**: `(resultado_fin_1 - resultado_fin_0) / resultado_fin_0 * 100` |
| var_ebt | decimal | **DERIVED**: `(ebt_1 - ebt_0) / ebt_0 * 100` |
| var_resnet | decimal | **DERIVED**: `(resultado_net_1 - resultado_net_0) / resultado_net_0 * 100` |
| var_om | decimal | **DERIVED**: `om_1 - om_0` (percentage points) |
| var_ncp | decimal | **DERIVED**: `ncp_1 - ncp_0` (percentage points) |

---

## Table 3: Operaciones Vinculadas Aggregate Variables

| canonical_name | type | derivation_rule |
|----------------|------|-----------------|
| total_ingreso_oov | currency | **DERIVED**: `SUM(ingreso_entidad)` for all entities |
| total_gasto_oov | currency | **DERIVED**: `SUM(gasto_entidad)` for all entities |
| peso_oov_sobre_incn | decimal | **DERIVED**: `total_ingreso_oov / cifra_1 * 100` |
| peso_oov_sobre_costes | decimal | **DERIVED**: `total_gasto_oov / cost_1 * 100` |

---

## Table 5 & 6: Summary Compliance Variables

### Local File Summary (3 rows)
| canonical_name | type | enum_values | formatting |
|----------------|------|-------------|------------|
| cumplimiento_resumen_local_1 | enum | si, no | si=green, no=yellow |
| cumplimiento_resumen_local_2 | enum | si, no | si=green, no=yellow |
| cumplimiento_resumen_local_3 | enum | si, no | si=green, no=yellow |

### Master File Summary (4 rows) - conditional on master_file == 1
| canonical_name | type | enum_values | formatting |
|----------------|------|-------------|------------|
| cumplimiento_resumen_mast_1 | enum | si, no | si=green, no=yellow |
| cumplimiento_resumen_mast_2 | enum | si, no | si=green, no=yellow |
| cumplimiento_resumen_mast_3 | enum | si, no | si=green, no=yellow |
| cumplimiento_resumen_mast_4 | enum | si, no | si=green, no=yellow |

---

## Table 7: Risk Elements Variables (12 Rows)

For each risk element (i = 1 to 12):

| canonical_name | type | enum_values | formatting |
|----------------|------|-------------|------------|
| impacto_{i} | enum | si, no, posible | - |
| afectacion_pre_{i} | enum | bajo, medio, alto | bajo=green, medio=yellow, alto=red |
| texto_mitigacion_{i} | text | - | Free text |
| afectacion_final_{i} | enum | bajo, medio, alto | bajo=green, medio=yellow, alto=red |

---

## Table 8: Local File Detailed Compliance (14 Rows)

For each row (i = 1 to 14):

| canonical_name | type | enum_values | formatting | validation |
|----------------|------|-------------|------------|------------|
| cumplido_local_{i} | enum | si, no, parcial | si=green, parcial=yellow, no=red | - |
| texto_cumplido_local_{i} | text | - | - | Required if cumplido_local_{i} in (no, parcial) |

---

## Table 9: Master File Detailed Compliance (17 Rows)

Conditional on `master_file == 1`. For each row (i = 1 to 17):

| canonical_name | type | enum_values | formatting | validation |
|----------------|------|-------------|------------|------------|
| cumplido_mast_{i} | enum | si, no, parcial | si=green, parcial=yellow, no=red | - |
| texto_cumplido_mast_{i} | text | - | - | Required if cumplido_mast_{i} in (no, parcial) |

---

## Variable Naming Corrections Applied

The following corrections were applied from the original template:

| Original Token | Canonical Name | Issue Fixed |
|----------------|----------------|-------------|
| `{{Entidad_cliente}}` | `entidad_cliente` | CamelCase → snake_case |
| `{{Descripción_actividad}}` | `descripcion_actividad` | Accent + CamelCase |
| `{{anyo_ejecicio}}` | `anyo_ejercicio` | Typo (missing 'r') |
| `{{anyo_ejecicio_ant}}` | `anyo_ejercicio_ant` | Typo (missing 'r') |
| `{{titulo_servicio_oovv}` | `titulo_servicio_oovv` | Missing closing brace |
| `{{titulo_texto_perspectiva forma}}` | (removed) | Redundant variable |
| `{{texto_perspectiva forma_1}}` | `texto_perspectiva_forma_1` | Space in name |
| `{{texto_perspectiva forma_2}}` | `texto_perspectiva_forma_2` | Space in name |
| `{{Descripcion_tabla}}` | `descripcion_tabla` | CamelCase |
| `{{Texto_anexo3}}` | `texto_anexo3` | CamelCase |
| `{{Cost_*}}` | `cost_*` | CamelCase |
| `{{Var_*}}` | `var_*` | CamelCase |
| `{{Metodo}}` | `metodo` | CamelCase |
| `{{Impacto_*}}` | `impacto_*` | CamelCase |
| `{{Afectacion_*}}` | `afectacion_*` | CamelCase |
| `{{Cumplido_*}}` | `cumplido_*` | CamelCase |
| `{{Texto_Cumplido_*}}` | `texto_cumplido_*` | CamelCase |
| `{{Contacto*}}` | `contacto*` | CamelCase |
| `{{Cargo_contacto*}}` | `cargo_contacto*` | CamelCase |
| `{{Resultado_*}}` | `resultado_*` | CamelCase |
| `UNIMA España` (hardcoded) | `{{ entidad_cliente }}` | Hardcoded → variable |

All variable names in `normalized_template.txt` now use canonical format.
