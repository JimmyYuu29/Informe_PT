# Coverage Matrix

**Plugin ID:** pt_review
**Generated:** 2025-12-31 | Step 2 - YAML Pack Generation

---

## Overview

This matrix maps all Step 1 source blocks to their corresponding YAML pack elements, ensuring complete coverage and traceability.

---

## Document Structure Coverage

| Source Block ID | Block Type | YAML Coverage | Files |
|-----------------|------------|---------------|-------|
| HEADER_01 | header | texts.yaml: s_header_main | texts, refs |
| FOOTER_01 | footer | fields.yaml: page_number | fields |
| COVER_TITLE | heading | fields.yaml: fecha_fin_fiscal | fields, refs |
| COVER_SUBTITLE_01 | heading | fields.yaml: entidad_cliente | fields, refs |
| COVER_SUBTITLE_02 | heading | texts.yaml: fixed | texts |
| TOC_SECTION | paragraph | Fixed structure | - |
| TOC_ENTRY_* | paragraph | Fixed structure | - |

---

## Section 1 Coverage

| Source Block ID | Block Type | YAML Coverage | Files |
|-----------------|------------|---------------|-------|
| SEC1_HEADING | heading | Fixed text | texts |
| SEC1_INTRO_PARA | paragraph | texts.yaml: s1_intro_main | texts, refs |
| SEC1_TEXTBLOCK_01 | text_block | texts.yaml: s1_master_file_no_access, logic.yaml: r001 | texts, logic, refs |
| SEC1_PARA_02 | paragraph | texts.yaml: s1_transactions_ref | texts, refs |
| SEC1_PARA_03 | paragraph | texts.yaml: s1_documentation_analysis | texts, refs |
| SEC1_PARA_04-09 | paragraph | texts.yaml: s1_economic_analysis, etc. | texts |
| SEC1_PARA_10 | paragraph | texts.yaml: s1_doc_access_intro | texts |
| SEC1_LIST_DOC | list | fields.yaml: documentacion_facilitada | fields, refs |
| SEC1_PARA_11 | paragraph | texts.yaml: s1_operations_intro | texts |
| SEC1_TABLE_01 | table | tables.yaml: t1_operaciones_intragrupo | tables, refs |

---

## Section 2 Coverage

| Source Block ID | Block Type | YAML Coverage | Files |
|-----------------|------------|---------------|-------|
| SEC2_HEADING | heading | Fixed text | - |
| SEC2_SUBHEAD_01 | heading | Fixed: "Situación general" | - |
| SEC2_PARA_01 | paragraph | fields.yaml: descripcion_actividad | fields, refs |
| SEC2_PARA_02 | paragraph | texts.yaml: s2_business_intro | texts |
| SEC2_TABLE_02 | table | tables.yaml: t2_situacion_negocio | tables, derived, refs |
| SEC2_TABLE_03 | table | tables.yaml: t3_operaciones_vinculadas | tables, derived, refs |
| SEC2_PARA_03 | paragraph | texts.yaml: s2_linked_expenses_summary | texts |
| SEC2_SUBHEAD_02 | heading | Fixed: "Conclusiones" | - |
| SEC2_SERVICE_* | service block | fields.yaml: servicios_oovv, logic.yaml: r005 | fields, tables, logic, refs |
| SEC2_TABLE_04 | table | tables.yaml: t4_analisis_servicio | tables, refs |
| SEC2_SUBHEAD_03 | heading | Fixed: "Conclusiones desde una perspectiva formal" | - |
| SEC2_TEXTBLOCK_02 | text_block | texts.yaml: s2_formal_perspective_intro | texts |
| SEC2_TABLE_05 | table | tables.yaml: t5_local_file_resumen | tables, refs |
| SEC2_TABLE_06 | table | tables.yaml: t6_master_file_resumen, logic.yaml: r003 | tables, logic, refs |
| SEC2_TEXTBLOCK_03 | text_block | texts.yaml: s2_formal_perspective_conclusion, logic.yaml: r002 | texts, logic, refs |

---

## Anexo I Coverage

| Source Block ID | Block Type | YAML Coverage | Files |
|-----------------|------------|---------------|-------|
| ANEXO1_HEADING | heading | Fixed text | - |
| ANEXO1_PARA_01-09 | paragraph | texts.yaml: s_anexo1_* | texts, refs |
| ANEXO1_LIST_RISKS | list | texts.yaml: fixed_lists.risk_categories | texts |
| ANEXO1_TABLE_07 | table | tables.yaml: t7_revision_riesgos | tables, fields, refs |

---

## Anexo II Coverage

| Source Block ID | Block Type | YAML Coverage | Files |
|-----------------|------------|---------------|-------|
| ANEXO2_HEADING | heading | Fixed text | - |
| ANEXO2_TABLE_08 | table | tables.yaml: t8_cumplimiento_local_file | tables, fields, refs |
| ANEXO2_TABLE_09 | table | tables.yaml: t9_cumplimiento_master_file, logic.yaml: r004 | tables, fields, logic, refs |

---

## Anexo III Coverage

| Source Block ID | Block Type | YAML Coverage | Files |
|-----------------|------------|---------------|-------|
| ANEXO3_HEADING | heading | Fixed text | - |
| ANEXO3_PARA_01-02 | paragraph | texts.yaml: s_anexo3_* | texts |
| ANEXO3_LIST_01-05 | list | texts.yaml: s_anexo3_* | texts |
| ANEXO3_LIST_03 | list | fields.yaml: texto_anexo3 | fields, refs |

---

## Contacts Coverage

| Source Block ID | Block Type | YAML Coverage | Files |
|-----------------|------------|---------------|-------|
| CONTACTS_HEADING | heading | Fixed text | - |
| CONTACTS_BLOCK | paragraph | fields.yaml: contacto*, cargo_contacto*, correo_contacto* | fields, refs |
| LEGAL_FOOTER_* | paragraph | texts.yaml: s_legal_footer_* | texts, refs |

---

## Conditional Logic Coverage

| Condition ID | Description | YAML Rule | Decision |
|--------------|-------------|-----------|----------|
| COND_001 | Master File no access | r001 | d1_master_file_access |
| COND_002 | Master File formal perspective | r002, r003 | d2_master_file_formal |
| COND_003 | Master File detailed table | r004 | d3_master_file_detailed |
| COND_004 | Service block activation | r005 | d4_service_activation |
| COND_005 | Compliance comment required | r006, r007 | d5_compliance_comment |

---

## Derived Fields Coverage

| Derivation ID | Target Field(s) | YAML Coverage |
|---------------|-----------------|---------------|
| DERIV_001 | anyo_ejercicio | derived.yaml |
| DERIV_002 | anyo_ejercicio_ant | derived.yaml |
| DERIV_003 | cost_1, cost_0 | derived.yaml |
| DERIV_004 | om_1, om_0 | derived.yaml |
| DERIV_005 | ncp_1, ncp_0 | derived.yaml |
| DERIV_006 | peso_oov_sobre_incn | derived.yaml |
| DERIV_007 | peso_oov_sobre_costes | derived.yaml |
| DERIV_008 | total_ingreso_oov | derived.yaml |
| DERIV_009 | total_gasto_oov | derived.yaml |
| DERIV_010 | var_* | derived.yaml |

---

## Coverage Summary

| Category | Total Items | Covered | Coverage % |
|----------|-------------|---------|------------|
| Document Blocks | 85 | 85 | 100% |
| Variables | 150+ | 150+ | 100% |
| Conditions | 5 | 5 | 100% |
| Derived Fields | 10 | 10 | 100% |
| Tables | 9 | 9 | 100% |
| Text Blocks | 3 | 3 | 100% |

**Total Coverage: 100%**

---

## Notes

All Step 1 source_block_ids are traceable through `refs.yaml`. No orphaned elements detected.
