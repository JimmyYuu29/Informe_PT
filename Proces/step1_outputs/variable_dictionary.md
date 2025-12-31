# Variable Dictionary

Generated: 2025-12-31 | Step 1 - Template Normalization
Source: Plantilla_1231.docx

---

## Variable Naming Convention

- **Canonical names**: snake_case, lowercase, ASCII only, no spaces
- **Original tokens**: preserved exactly as found in template (for patch plan reference)

---

## Global Variables (Single-Value Inputs)

| canonical_name | original_tokens | type | required | scope | appears_in | validation_hints | formatting | derivation_rule |
|----------------|-----------------|------|----------|-------|------------|------------------|------------|-----------------|
| fecha_fin_fiscal | `{{fecha_fin_fiscal}}` | date | Y | global | COVER_TITLE, headers | ISO date input | Spanish long date format (e.g., "31 de diciembre de 2025") | - |
| entidad_cliente | `{{Entidad_cliente}}` | text | Y | global | COVER_SUBTITLE_01, SEC1_INTRO_PARA | Non-empty string | - | - |
| descripcion_actividad | `{{Descripción_actividad}}` | text | Y | global | SEC2_PARA_01 | Free text, multi-paragraph allowed | - | - |
| master_file | - (implied) | enum | Y | global | Conditions | Values: 0, 1 | - | 0 = no access, 1 = access |
| texto_anexo3 | `{{Texto_anexo3}}` | text | N | global | ANEXO3_LIST_03 | Free text | - | - |
| anyo_ejercicio | `{{anyo_ejecicio}}` | int | N | global | Multiple paragraphs and tables | 4-digit year | - | **DERIVED**: `year(fecha_fin_fiscal)` |
| anyo_ejercicio_ant | `{{anyo_ejecicio_ant}}` | int | N | global | TABLE_02 headers | 4-digit year | - | **DERIVED**: `anyo_ejercicio - 1` |

---

## Contact Variables

| canonical_name | original_tokens | type | required | scope | appears_in | validation_hints |
|----------------|-----------------|------|----------|-------|------------|------------------|
| contacto1 | `{{Contacto1}}` | text | Y | global | CONTACTS_BLOCK | Person name |
| cargo_contacto1 | `{{Cargo_contacto1}}` | text | Y | global | CONTACTS_BLOCK | Job title |
| correo_contacto1 | `{{correo_contacto1}}` | text | Y | global | CONTACTS_BLOCK | Email format |
| contacto2 | `{{Contacto2}}` | text | Y | global | CONTACTS_BLOCK | Person name |
| cargo_contacto2 | `{{Cargo_contacto2}}` | text | Y | global | CONTACTS_BLOCK | Job title |
| correo_contacto2 | `{{correo_contacto2}}` | text | Y | global | CONTACTS_BLOCK | Email format |
| contacto3 | `{{Contacto3}}` | text | Y | global | CONTACTS_BLOCK | Person name |
| cargo_contacto3 | `{{Cargo_contacto3}}` | text | Y | global | CONTACTS_BLOCK | Job title |
| correo_contacto3 | `{{correo_contacto3}}` | text | Y | global | CONTACTS_BLOCK | Email format |

---

## List Variables (Dynamic Repeating)

### documentacion_facilitada
| Field | Details |
|-------|---------|
| canonical_name | `documentacion_facilitada` |
| original_tokens | `{{documentacion_facilitada}}` |
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
| original_tokens | `{{servicio_vinculado}}` |
| type | list[object] |
| required | Y |
| scope | global |
| appears_in | TABLE_01, TABLE_03 |
| item_fields | `index` (int, auto), `servicio_vinculado` (text) |

### servicios_oovv (Service Analysis Block Repeat)
| Field | Details |
|-------|---------|
| canonical_name | `servicios_oovv` |
| original_tokens | Multiple variables per service |
| type | list[object] |
| required | N |
| scope | global |
| appears_in | SEC2_SERVICE_* blocks |
| item_fields | See service_oovv_item below |

**service_oovv_item fields:**
| field | original_token | type | required | description |
|-------|----------------|------|----------|-------------|
| enabled | - | bool | Y | Whether to include this service block |
| titulo_servicio_oovv | `{{titulo_servicio_oovv}` (MALFORMED) | text | Y | Service title heading |
| texto_intro_servicio | `{{texto_intro_servicio}}` | text | Y | Introduction paragraph |
| descripcion_tabla | `{{Descripcion_tabla}}` | text | Y | Table description |
| tabla_analisis_servicio | `{{tabla_analisis_servicio}}` | table | Y | Analysis table data |
| texto_conclusion_servicio | `{{texto_conclusion_servicio}}` | text | Y | Conclusion paragraph |

---

## Table 2: Situación de Negocio Variables (Financial Data)

### Current Year (suffix _1)
| canonical_name | original_tokens | type | required | derivation_rule |
|----------------|-----------------|------|----------|-----------------|
| cifra_1 | `{{cifra_1}}` | currency | Y | User input |
| cost_1 | `{{Cost_1}}` | currency | N | **DERIVED**: `cifra_1 - ebit_1` |
| ebit_1 | `{{EBIT_1}}` | currency | Y | User input |
| resultado_fin_1 | `{{Resultado_fin_1}}` | currency | Y | User input |
| ebt_1 | `{{EBT_1}}` | currency | Y | User input |
| resultado_net_1 | `{{Resultado_net_1}}` | currency | Y | User input |
| om_1 | `{{OM_1}}` | decimal | N | **DERIVED**: `ebit_1 / cifra_1` (as %) |
| ncp_1 | `{{NCP_1}}` | decimal | N | **DERIVED**: `ebit_1 / cost_1` (as %) |

### Prior Year (suffix _0)
| canonical_name | original_tokens | type | required | derivation_rule |
|----------------|-----------------|------|----------|-----------------|
| cifra_0 | `{{cifra_0}}` | currency | Y | User input |
| cost_0 | `{{Cost_0}}` | currency | N | **DERIVED**: `cifra_0 - ebit_0` |
| ebit_0 | `{{EBIT_0}}` | currency | Y | User input |
| resultado_fin_0 | `{{Resultado_fin_0}}` | currency | Y | User input |
| ebt_0 | `{{EBT_0}}` | currency | Y | User input |
| resultado_net_0 | `{{Resultado_net_0}}` | currency | Y | User input |
| om_0 | `{{OM_0}}` | decimal | N | **DERIVED**: `ebit_0 / cifra_0` (as %) |
| ncp_0 | `{{NCP_0}}` | decimal | N | **DERIVED**: `ebit_0 / cost_0` (as %) |

### Variation Variables (suffix Var_)
| canonical_name | original_tokens | type | derivation_rule |
|----------------|-----------------|------|-----------------|
| var_cifra | `{{Var_cifra}}` | decimal | **DERIVED**: `(cifra_1 - cifra_0) / cifra_0 * 100` |
| var_cost | `{{Var_cost}}` | decimal | **DERIVED**: `(cost_1 - cost_0) / cost_0 * 100` |
| var_ebit | `{{Var_EBIT}}` | decimal | **DERIVED**: `(ebit_1 - ebit_0) / ebit_0 * 100` |
| var_resfin | `{{Var_ResFin}}` | decimal | **DERIVED**: `(resultado_fin_1 - resultado_fin_0) / resultado_fin_0 * 100` |
| var_ebt | `{{Var_EBT}}` | decimal | **DERIVED**: `(ebt_1 - ebt_0) / ebt_0 * 100` |
| var_resnet | `{{Var_ResNet}}` | decimal | **DERIVED**: `(resultado_net_1 - resultado_net_0) / resultado_net_0 * 100` |
| var_om | `{{Var_OM}}` | decimal | **DERIVED**: `om_1 - om_0` (percentage points) |
| var_ncp | `{{Var_NCP}}` | decimal | **DERIVED**: `ncp_1 - ncp_0` (percentage points) |

---

## Table 3: Operaciones Vinculadas Variables (Nested List)

### Per-Entity Row Variables
| canonical_name | original_tokens | type | scope | description |
|----------------|-----------------|------|-------|-------------|
| servicio_vinculado | `{{servicio_vinculado}}` | text | per-item | Service type name |
| entidad_vinculada | `{{entidad_vinculada}}` | text | per-item | Linked entity name |
| ingreso_entidad | `{{ingreso_entidad}}` | currency | per-item | Income from entity |
| gasto_entidad | - (implied) | currency | per-item | Expense to entity (if applicable) |

### Aggregate Variables
| canonical_name | original_tokens | type | derivation_rule |
|----------------|-----------------|------|-----------------|
| total_ingreso_oov | `{{total_ingreso_oov}}` | currency | **DERIVED**: `SUM(ingreso_entidad)` for all entities |
| total_gasto_oov | `{{total_gasto_oov}}` | currency | **DERIVED**: `SUM(gasto_entidad)` for all entities |
| peso_oov_sobre_incn | `{{peso_oov_sobre_incn}}` | decimal | **DERIVED**: `total_ingreso_oov / cifra_1 * 100` |
| peso_oov_sobre_costes | `{{peso_oov_sobre_costes}}` | decimal | **DERIVED**: `total_gasto_oov / cost_1 * 100` |

---

## Table 4: Service Analysis Table Variables

| canonical_name | original_tokens | type | scope | description |
|----------------|-----------------|------|-------|-------------|
| metodo | `{{Metodo}}` | text | per-service | Selected method name |
| min | `{{Min}}` | decimal | per-service | Minimum percentage |
| lq | `{{LQ}}` | decimal | per-service | Lower quartile percentage |
| med | `{{Med}}` | decimal | per-service | Median percentage |
| uq | `{{UQ}}` | decimal | per-service | Upper quartile percentage |
| max | `{{Max}}` | decimal | per-service | Maximum percentage |

---

## Table 7: Risk Elements Variables (12 Rows)

For each risk element (i = 1 to 12):

| canonical_name | original_tokens | type | enum_values | formatting |
|----------------|-----------------|------|-------------|------------|
| impacto_{i} | `{{Impacto_{i}}}` | enum | si, no, posible | - |
| afectacion_pre_{i} | `{{Afectacion_Pre_{i}}}` | enum | bajo, medio, alto | Cell color: bajo=green, medio=yellow, alto=red |
| texto_mitigacion_{i} | `{{texto_mitigacion_{i}}}` | text | - | Free text |
| afectacion_final_{i} | `{{Afectacion_final_{i}}}` | enum | bajo, medio, alto | Cell color: bajo=green, medio=yellow, alto=red |

---

## Table 8 & 9: Compliance Variables

### Local File (14 rows, i = 1 to 14)
| canonical_name | original_tokens | type | enum_values | formatting |
|----------------|-----------------|------|-------------|------------|
| cumplido_local_{i} | `{{Cumplido_Local_{i}}}` | enum | si, no, parcial | si=green, parcial=yellow, no=red |
| texto_cumplido_local_{i} | `{{Texto_Cumplido_Local_{i}}}` | text | - | Required if cumplido_local_{i} in (no, parcial) |

### Master File (17 rows, i = 1 to 17)
| canonical_name | original_tokens | type | enum_values | formatting | condition |
|----------------|-----------------|------|-------------|------------|-----------|
| cumplido_mast_{i} | `{{Cumplido_Mast_{i}}}` | enum | si, no, parcial | si=green, parcial=yellow, no=red | Only when master_file == 1 |
| texto_cumplido_mast_{i} | `{{Texto_Cumplido_Mast_{i}}}` | text | - | Required if cumplido_mast_{i} in (no, parcial) | Only when master_file == 1 |

---

## Issues Detected (See template_patch_plan.md)

| Issue ID | Original Token | Problem | Canonical Replacement |
|----------|----------------|---------|----------------------|
| VAR_001 | `{{Entidad_cliente}}` | CamelCase | `entidad_cliente` |
| VAR_002 | `{{Descripción_actividad}}` | Accented character | `descripcion_actividad` |
| VAR_003 | `{{anyo_ejecicio}}` | Typo (missing 'r') | `anyo_ejercicio` |
| VAR_004 | `{{anyo_ejecicio_ant}}` | Typo (missing 'r') | `anyo_ejercicio_ant` |
| VAR_005 | `{{titulo_servicio_oovv}` | Missing closing brace | `titulo_servicio_oovv` |
| VAR_006 | `{{titulo_texto_perspectiva forma}}` | Space in name | `titulo_texto_perspectiva_forma` |
| VAR_007 | `{{texto_perspectiva forma_1}}` | Space in name | `texto_perspectiva_forma_1` |
| VAR_008 | `{{texto_perspectiva forma_2}}` | Space in name | `texto_perspectiva_forma_2` |
| VAR_009 | `{{Descripcion_tabla}}` | CamelCase | `descripcion_tabla` |
| VAR_010 | `{{Texto_anexo3}}` | CamelCase | `texto_anexo3` |
| VAR_011 | `{{Cost_1}}`, `{{Cost_0}}` | CamelCase | `cost_1`, `cost_0` |
| VAR_012 | `{{Resultado_fin_*}}` | CamelCase | `resultado_fin_*` |
| VAR_013 | `{{Resultado_net_*}}` | CamelCase | `resultado_net_*` |
| VAR_014 | `{{Var_*}}` | CamelCase | `var_*` |
| VAR_015 | `{{Metodo}}` | CamelCase | `metodo` |
| VAR_016 | `{{Impacto_*}}` | CamelCase | `impacto_*` |
| VAR_017 | `{{Afectacion_*}}` | CamelCase | `afectacion_*` |
| VAR_018 | `{{Cumplido_*}}` | CamelCase | `cumplido_*` |
| VAR_019 | `{{Texto_Cumplido_*}}` | CamelCase | `texto_cumplido_*` |
| VAR_020 | `{{Contacto*}}` | CamelCase | `contacto*` |
| VAR_021 | `{{Cargo_contacto*}}` | CamelCase | `cargo_contacto*` |
