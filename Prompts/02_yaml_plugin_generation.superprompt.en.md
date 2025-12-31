# Step 2 — Generate YAML Pack in config/yamls/<plugin_id>/ (v2.1, 2025-12-31)

ROLE
You are a senior rules engineer and document automation architect producing a CI-verifiable YAML pack.

INPUTS (ASSUME AVAILABLE IN REPO)
- Platform prompt: `prompts/enterprise_docgen_platform.superprompt.en.md`
- Step1 outputs: `Proces/step1_outputs/*`
- Final template (user-edited after Step1): `config/templates/<plugin_id>/template_final.docx`
- Optional rules:
  - `docs/rules/yaml_dsl_rules.md`
  - `docs/rules/docx_template_constraints.md`

PRIMARY OBJECTIVE
Generate a complete YAML pack under:
- `config/yamls/<plugin_id>/`

The pack must be deterministic, traceable, statically verifiable, and maintainable.

MANDATORY OUTPUT FILES (WRITE ALL)
- `manifest.yaml`
- `config.yaml`
- `fields.yaml`
- `texts.yaml`           (lossless fixed wording, verbatim from template)
- `tables.yaml`          (reproducible table schemas)
- `logic.yaml`           (controlled DSL only, depth<=3, first-match)
- `decision_map.yaml`    (human-readable governance)
- `refs.yaml`            (traceability index back to Step1 source_block_id)
- `derived.yaml`         (if any derived fields exist)
- `formatting.yaml`      (date/currency/enum color maps)
- `template_patches.md`  (must reflect unresolved docx patch needs)
- `coverage_matrix.md`
- `validation_report.md`
- `PACK_README.md`       (EXPLAINS each file purpose, edit rules, and maintenance workflow)
- `sample_inputs/<plugin_id>_{minimal,branch_a,branch_b}.json`

CRITICAL RULES
1) No paraphrasing:
   - texts.yaml must preserve template fixed text verbatim.
2) Controlled DSL only:
   - Use allowlisted operators (from yaml_dsl_rules.md if present; else use default allowlist)
   - No regex unless explicitly allowed
   - Max nesting depth <= 3
3) Stable naming (diff-friendly):
   - rule_id: r001, r002...
   - decision_id: d{section}_{intent}
   - text_key: s{section}_{topic}_{variant}
   - table_key: t{section}_{name}
4) Cross-file integrity:
   - Every reference must resolve by inspection: fields/texts/tables/logic/config/decision_map/refs
5) Traceability:
   - Every text_key/table_key includes `source_block_id` list from Step1
6) Maintainability:
   - If logic gets complex, factor into derived flags in derived.yaml.

DEFAULT OPERATOR SET (ONLY IF NO DSL RULES FILE)
and, or, not,
equals, not_equals, gt, gte, lt, lte,
in, not_in,
exists, not_exists, is_empty, not_empty,
contains, not_contains, starts_with, ends_with

PACK_README.md MUST INCLUDE
- How to add a new field
- How to add a new conditional paragraph variant
- How to add a new repeating table
- How to update template + keep traceability
- Common pitfalls (duplicate IDs, illegal tokens, shadowed rules)

OUTPUT FORMAT
- Provide file tree under `config/yamls/<plugin_id>/`
- Then output full content of each file in fenced code blocks
- Do not omit any required file.
