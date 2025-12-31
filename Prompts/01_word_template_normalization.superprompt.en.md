# Step 1 — Word Template Normalization & Structuring (v2.1, 2025-12-31)

ROLE
You are a senior document automation architect preparing a semi-finished Word template for a governed, YAML-driven document generation platform.

INPUTS (ASSUME AVAILABLE IN REPO)
- Root template: `Plantilla_1231.docx`
- Platform prompt: `prompts/enterprise_docgen_platform.superprompt.en.md`

STEP 1 OBJECTIVE
From the semi-finished template (may contain invalid Jinja, author notes, inconsistent variable names):
1) Produce a STANDARDIZED TEMPLATE TEXT in TXT format suitable to be copy/pasted back into the Word template as the final docxtpl template.
2) Produce complete intermediate catalogs for Step 2 YAML generation.
3) Produce a patch plan (template_patch_plan.md) that lists every fix needed.

MANDATORY OUTPUT LOCATIONS
- Create folder: `Proces/step1_outputs/`
- Create folder: `config/` (if missing)
- Write ALL Step1 files into `Proces/step1_outputs/` with the exact filenames below.

NON-NEGOTIABLE RULES
1) Lossless fixed text:
   - Every visible paragraph/heading/list item in the Word template must appear verbatim in `normalized_template.txt`
   - EXCEPT author annotations which must be extracted to `author_notes_catalog.md`
2) Word is source of truth:
   - Do not rewrite, paraphrase, or improve any fixed wording.
3) Dual-track placeholder normalization:
   - Track BOTH original tokens and canonical tokens.
   - Canonical token rules: snake_case, lowercase ASCII, no spaces, no accents.
4) No YAML / No Python code in Step 1 outputs.
   - You MAY include docxtpl placeholders and simple loop tags in `normalized_template.txt`.
   - All other outputs must be plain text/markdown catalogs.

SPECIAL HANDLING — AUTHOR ANNOTATIONS
- Treat `[AI_NOTE] ... [/AI_NOTE]` and `[TEXT_BLOCK: id] ... [/TEXT_BLOCK]` as AUTHOR ANNOTATIONS.
- In `normalized_template.txt`, remove annotation content and insert a marker:
  `[AUTHOR_NOTE: <note_id>]` or `[TEXT_BLOCK: <block_id>]` at the exact position.
- In `author_notes_catalog.md`, store the extracted text verbatim + location + references.

TABLE HANDLING (CRITICAL)
For each table:
- Provide a reproducible schema snapshot (dimensions, headers, repeating rows, nested repeat needs)
- Identify which columns are user inputs vs derived/computed
- Identify formatting rules (e.g., si/no/parcial -> color)
- Identify mismatches between table design and author notes -> record as TODO + patch suggestion

REQUIRED OUTPUT FILES (MUST PRODUCE ALL)

(1) `normalized_template.txt`
- Linear, document order, verbatim fixed text
- Insert markers:
  [PAGE_BREAK], [SECTION_BREAK], [AUTHOR_NOTE: id], [TEXT_BLOCK: id], [TABLE: table_id]
- Replace placeholders with canonical `{{ canonical_name }}` where safe, and record mapping.
- If malformed placeholder exists, keep the raw text in place AND mark it as TODO in diagnostics + patch plan.

(2) `document_structure_catalog.md`
For each block:
- source_block_id (stable, deterministic)
- block_type (heading/paragraph/list/table/header/footer)
- location (approx section + paragraph index)
- style/level if visible
- conditional? Y/N (based on annotations/implied logic)
- linked table_id / note_id

(3) `variable_dictionary.md`
For each variable:
- canonical_name
- original_tokens (list)
- scope (global / local / per-item)
- appears_in (block_ids/table_ids/conditions)
- type (text/int/decimal/currency/date/enum/list/object)
- required/optional + default (if implied)
- validation hints
- formatting rules (e.g., Spanish long date)
- derivation rule if derived

(4) `conditional_logic_catalog.md`
For each condition:
- condition_id
- structured statement (IF ... THEN include/exclude/choose ...)
- variables involved (canonical)
- affected blocks/tables
- precedence notes

(5) `tables_catalog.md`
For each table:
- table_id, location, caption/title
- dimensions
- headers (verbatim)
- row types: header, repeating template row, fixed rows, totals rows
- repeat dimensions (e.g., list of services; list of operations)
- input fields per row (canonical)
- derived fields + formulas (in natural language)
- enum/color rules
- TODOs/missing placeholders

(6) `author_notes_catalog.md`
- note_id / text_block_id
- location
- extracted text verbatim
- referenced vars/blocks/tables

(7) `template_diagnostics_todos.md`
- malformed placeholders (exact location + fix)
- illegal variable names (spaces/accents) + canonical replacements
- duplicate TEXT_BLOCK IDs
- table design mismatches
- ambiguities requiring user decision

(8) `template_patch_plan.md`
- patch_id
- location (block/table/cell + reference to source_block_id/table_id)
- original text/token
- target canonical token or change
- reason
- impacted variables/tables/conditions

QUALITY BAR
Step1 outputs must allow Step2 to generate YAML without opening the Word file.
