# Document Structure Catalog (PATCHED)

Generated: 2025-12-31 | Step 1 - Template Normalization
Source: Plantilla_1231.docx
Status: All issues resolved - variables normalized to canonical format

---

## Overview

This catalog documents the structural elements of the template in document order, assigning stable `source_block_id` references for traceability in Step 2.

---

## Block Registry

| source_block_id | block_type | style | location | conditional | linked_ids | description |
|-----------------|------------|-------|----------|-------------|------------|-------------|
| HEADER_01 | header | Normal | All pages | N | - | Fixed header: "Departamento de Precios de Transferencia / Forvis Mazars Tax & Legal, S.L.P." |
| FOOTER_01 | footer | Normal | All pages | N | - | Page number |
| COVER_TITLE | heading | Title | Cover, P3 | N | - | Main title with `fecha_fin_fiscal` |
| COVER_SUBTITLE_01 | heading | Subtitle | Cover, P4 | N | - | Company name `entidad_cliente` |
| COVER_NOTE_01 | annotation | Normal | Cover, P5-P12 | N | note_01 | AI_NOTE explaining variables |
| COVER_SUBTITLE_02 | heading | Subtitle | Cover, P13 | N | - | Fixed: "Forvis Mazars Tax & Legal, S.L.P." |
| TOC_SECTION | paragraph | Normal | TOC, P15 | N | - | "Contenidos" heading |
| TOC_ENTRY_01 | paragraph | toc 1 | TOC, P17 | N | - | "1. Introducción y alcance del trabajo" |
| TOC_ENTRY_02 | paragraph | toc 1 | TOC, P18 | N | - | "2. Resumen ejecutivo" |
| TOC_ENTRY_03 | paragraph | toc 1 | TOC, P19 | N | - | "Anexo I – Revisión valorativa" |
| TOC_ENTRY_04 | paragraph | toc 1 | TOC, P20 | N | - | "Anexo II – Revisión de requisitos formales en detalle" |
| TOC_ENTRY_05 | paragraph | toc 1 | TOC, P21 | N | - | "Anexo III – Desarrollo Comentarios técnicos" |
| SEC1_HEADING | heading | Heading 1 | Section 1, P25 | N | - | "Introducción y alcance del trabajo" |
| SEC1_INTRO_PARA | paragraph | Normal | Section 1, P27 | N | - | Main introduction paragraph (fixed legal text) |
| SEC1_TEXTBLOCK_01 | text_block | Normal | Section 1, P28-P30 | Y | master_file_no_acceso | Conditional block when Master File not accessible |
| SEC1_NOTE_02 | annotation | Normal | Section 1, P32-P39 | N | note_02 | AI_NOTE explaining condition for master_file_no_acceso |
| SEC1_PARA_02 | paragraph | Normal | Section 1, P40 | N | - | Reference to fiscal year transactions |
| SEC1_NOTE_03 | annotation | Normal | Section 1, P41-P46 | N | note_03 | AI_NOTE explaining derived variable anyo_ejercicio |
| SEC1_PARA_03 | paragraph | Normal | Section 1, P47 | N | - | Documentation analysis note |
| SEC1_PARA_04 | paragraph | Normal | Section 1, P48 | N | - | Economic analysis limitation |
| SEC1_PARA_05 | paragraph | Normal | Section 1, P49 | N | - | Financial audit disclaimer |
| SEC1_PARA_06 | paragraph | Normal | Section 1, P50 | N | - | Other fiscal obligations disclaimer |
| SEC1_PARA_07 | paragraph | Normal | Section 1, P51 | N | - | Final disclaimer about interpretations |
| SEC1_PARA_08 | paragraph | Normal | Section 1, P52 | N | - | Work basis statement |
| SEC1_PARA_09 | paragraph | Normal | Section 1, P53 | N | - | Memo value statement |
| SEC1_PARA_10 | paragraph | Normal | Section 1, P54 | N | - | Documentation access intro |
| SEC1_LIST_DOC | list | List Paragraph | Section 1, P55 | N | - | Dynamic list: documentacion_facilitada |
| SEC1_NOTE_04 | annotation | Normal | Section 1, P56-P65 | N | note_04 | AI_NOTE explaining documentacion_facilitada list |
| SEC1_PARA_11 | paragraph | Normal | Section 1, P66 | N | - | Intro to operations table |
| SEC1_TABLE_CAPTION_01 | paragraph | Tablas | Section 1, P67 | N | table_01 | "Tabla 1. Identificación de las operaciones intragrupo..." |
| SEC1_TABLE_01 | table | - | Section 1 | N | table_01 | Table 0: Operations list (2 cols, repeating rows) |
| SEC1_NOTE_05 | annotation | Normal | Section 1, P69-P73 | N | note_05 | AI_NOTE explaining dynamic service list |
| SEC2_HEADING | heading | Heading 1 | Section 2, P75 | N | - | "Resumen ejecutivo" |
| SEC2_SUBHEAD_01 | heading | Heading 2 | Section 2, P76 | N | - | "Situación general" |
| SEC2_PARA_01 | paragraph | Normal | Section 2, P77 | N | - | Variable: descripcion_actividad |
| SEC2_NOTE_06 | annotation | Normal | Section 2, P78-P80 | N | note_06 | AI_NOTE about descripcion_actividad |
| SEC2_PARA_02 | paragraph | Normal | Section 2, P81 | N | - | Intro to business situation tables |
| SEC2_TABLE_CAPTION_02 | paragraph | Tablas | Section 2, P82 | N | table_02 | "Tabla 2. Situación de negocio..." |
| SEC2_NOTE_07 | annotation | Normal | Section 2, P83-P93 | N | note_07 | AI_NOTE explaining derived variables |
| SEC2_TABLE_02 | table | - | Section 2 | N | table_02 | Table 1: Business situation (9 rows, 4 cols) |
| SEC2_TABLE_CAPTION_03 | paragraph | Tablas | Section 2, P95 | N | table_03 | "Tabla 3. Operaciones vinculadas..." |
| SEC2_NOTE_08 | annotation | Normal | Section 2, P96-P107 | N | note_08 | AI_NOTE explaining linked operations table |
| SEC2_TABLE_03 | table | - | Section 2 | N | table_03 | Table 2: Linked operations (6 rows, 3 cols, nested repeating) |
| SEC2_PARA_03 | paragraph | Normal | Section 2, P108 | N | - | Linked expenses summary with variable |
| SEC2_SUBHEAD_02 | heading | Heading 2 | Section 2, P109 | N | - | "Conclusiones" |
| SEC2_SERVICE_TITLE | heading | Heading 3 | Section 2, P110 | Y | - | Service title: `{{ servicio.titulo_servicio_oovv }}` (within loop) ✅ FIXED |
| SEC2_SERVICE_INTRO | paragraph | Normal | Section 2, P111 | Y | - | Service intro text variable |
| SEC2_TABLE_CAPTION_04 | paragraph | Tablas | Section 2, P112 | Y | table_04 | Table description variable |
| SEC2_TABLE_04 | table | - | Section 2, P113 | Y | table_04 | Table 3: Analysis table (repeating per service) |
| SEC2_SERVICE_CONCLUSION | paragraph | Normal | Section 2, P114 | Y | - | Service conclusion text |
| SEC2_NOTE_09 | annotation | Normal | Section 2, P115-P127 | N | note_09 | AI_NOTE explaining service block activation |
| SEC2_SUBHEAD_03 | heading | Heading 3 | Section 2, P129 | N | - | Fixed text: "Conclusiones desde una perspectiva formal" ✅ FIXED |
| SEC2_TEXTBLOCK_02 | text_block | Normal | Section 2, P135-P138 | N | texto_perspectiva_forma_1 | Formal perspective intro (inline content) ✅ FIXED |
| SEC2_TABLE_05 | table | - | Section 2 | Y | table_05 | Table 4: Local File summary compliance |
| SEC2_TABLE_06 | table | - | Section 2 | Y | table_06 | Table 5: Master File summary compliance |
| SEC2_TEXTBLOCK_03 | text_block | Normal | Section 2, P139-P143 | Y | texto_perspectiva_forma_2 | Formal perspective conclusion (condition: master_file==1) ✅ FIXED |
| SEC2_NOTE_10 | annotation | Normal | Section 2, P145-P157 | N | note_10 | AI_NOTE about Master File condition |
| ANEXO1_HEADING | heading | No Spacing | Anexo I, P159 | N | - | "Anexo I – Revisión valorativa" |
| ANEXO1_PARA_01 | paragraph | Normal | Anexo I, P160 | N | - | Risk introduction |
| ANEXO1_PARA_02 | paragraph | Normal | Anexo I, P161 | N | - | Risk origin explanation |
| ANEXO1_PARA_03 | paragraph | Normal | Anexo I, P162 | N | - | Section objective |
| ANEXO1_PARA_04 | paragraph | Normal | Anexo I, P163 | N | - | Analysis importance |
| ANEXO1_PARA_05 | paragraph | Normal | Anexo I, P164 | N | - | Strategic Plan 2024-2027 reference |
| ANEXO1_PARA_06 | paragraph | Normal | Anexo I, P165 | N | - | Annual Control Plan reference |
| ANEXO1_PARA_07 | paragraph | Normal | Anexo I, P166 | N | - | Administration areas intro |
| ANEXO1_LIST_RISKS | list | Normal | Anexo I, P167-P178 | N | - | Fixed list of 12 risk categories |
| ANEXO1_PARA_08 | paragraph | Normal | Anexo I, P179 | N | - | Review explanation |
| ANEXO1_PARA_09 | paragraph | Normal | Anexo I, P180 | N | - | Additional points from experience |
| ANEXO1_TABLE_CAPTION | paragraph | Tablas | Anexo I, P183 | N | table_07 | "Tabla 9. Revisión de elementos identificados..." |
| ANEXO1_TABLE_07 | table | - | Anexo I | N | table_07 | Table 6: Risk elements (13 rows, 6 cols) |
| ANEXO1_NOTE_11 | annotation | Normal | Anexo I, P185-P188 | N | note_11 | AI_NOTE about impacto/afectacion enum values |
| ANEXO2_HEADING | heading | No Spacing | Anexo II, P193 | N | - | "Anexo II – Revisión de requisitos formales en detalle" |
| ANEXO2_TABLE_CAPTION_01 | paragraph | Tablas | Anexo II, P194 | N | table_08 | "Tabla 10. Grado de cumplimiento formal... Local File" |
| ANEXO2_TABLE_08 | table | - | Anexo II | N | table_08 | Table 7: Local File detailed compliance (15 rows) |
| ANEXO2_TABLE_CAPTION_02 | paragraph | Tablas | Anexo II, P196 | N | table_09 | "Tabla 11. Grado de cumplimiento formal... Master File" |
| ANEXO2_TABLE_09 | table | - | Anexo II | Y | table_09 | Table 8: Master File detailed compliance (18 rows) - conditional on master_file==1 |
| ANEXO2_NOTE_12 | annotation | Normal | Anexo II, P198-P202 | N | note_12 | AI_NOTE about cumplido enum and Master File condition |
| ANEXO3_HEADING | heading | No Spacing | Anexo III, P210 | N | - | "Anexo III – Desarrollo Comentarios técnicos" |
| ANEXO3_PARA_01 | paragraph | Normal | Anexo III, P212 | N | - | Analysis intro |
| ANEXO3_SUBHEAD | heading | Style1 | Anexo III, P213 | N | - | "Comentarios relativos a los requisitos..." |
| ANEXO3_PARA_02 | paragraph | Normal | Anexo III, P214 | N | - | Table-based comments intro |
| ANEXO3_LIST_01 | list | List Paragraph | Anexo III, P215 | N | - | General/formal requirements comment |
| ANEXO3_LIST_02 | list | List Paragraph | Anexo III, P216 | N | - | Master File access comment |
| ANEXO3_LIST_03 | list | List Paragraph | Anexo III, P217 | N | - | Variable: texto_anexo3 |
| ANEXO3_LIST_04 | list | List Paragraph | Anexo III, P218 | N | - | Documentation timing comment |
| ANEXO3_LIST_05 | list | List Paragraph | Anexo III, P219 | N | - | Recommendation |
| ANEXO3_LIST_06 | list | List Paragraph | Anexo III, P220 | N | - | "Comentarios valorativos" (section placeholder) |
| ANEXO3_LIST_07 | list | List Paragraph | Anexo III, P221 | N | - | "Documentación en otro idioma" (section placeholder) |
| ANEXO3_LIST_08 | list | List Paragraph | Anexo III, P222 | N | - | "Texto del comentario" (placeholder) |
| ANEXO3_LIST_09 | list | List Paragraph | Anexo III, P224 | N | - | "Servicios intragrupo" (section placeholder) |
| ANEXO3_LIST_10 | list | List Paragraph | Anexo III, P225 | N | - | "Texto del comentario" (placeholder) |
| ANEXO3_LIST_11 | list | List Paragraph | Anexo III, P227 | N | - | "ETC" (placeholder) |
| CONTACTS_HEADING | heading | Title | Contacts, P237 | N | - | "Contactos" |
| CONTACTS_BLOCK | paragraph | Normal | Contacts, P239-P247 | N | - | 3 contact blocks with variables |
| LEGAL_FOOTER_01 | paragraph | Normal | Footer, P249 | N | - | Forvis Mazars network description |
| LEGAL_FOOTER_02 | paragraph | Normal | Footer, P250 | N | - | Spanish entities description |
| LEGAL_FOOTER_03 | paragraph | Normal | Footer, P252 | N | - | Website: www.forvismazars.es |

---

## Summary Statistics

- **Total blocks**: 85
- **Headings**: 12
- **Paragraphs**: 38
- **Lists**: 14
- **Tables**: 9
- **Annotations (AI_NOTE)**: 12
- **Text blocks (TEXT_BLOCK)**: 3
- **Conditional blocks**: 10

---

## Cross-References

### Blocks with Variables
- COVER_TITLE: `fecha_fin_fiscal`
- COVER_SUBTITLE_01: `entidad_cliente`
- SEC1_INTRO_PARA: `entidad_cliente`
- SEC1_PARA_02, SEC1_PARA_03, SEC2_PARA_03, etc.: `anyo_ejercicio`
- SEC2_PARA_01: `descripcion_actividad`
- SEC1_LIST_DOC: `documentacion_facilitada` (list)
- Multiple tables: see tables_catalog.md

### Conditional Blocks
- SEC1_TEXTBLOCK_01: condition `master_file == 0`
- SEC2_SERVICE_*: condition per-service activation flag
- SEC2_TEXTBLOCK_02/03: condition `master_file == 1`
- ANEXO2_TABLE_09: condition `master_file == 1`
