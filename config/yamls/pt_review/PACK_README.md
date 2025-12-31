# PACK_README - pt_review Plugin

**Plugin ID:** `pt_review`
**Version:** 1.0.0
**Generated:** 2025-12-31 | Step 2 - YAML Pack Generation

---

## Overview

This YAML pack configures a Transfer Pricing Review Report generator for Spanish tax compliance audits. The report includes:

- Executive summary with financial data
- Related-party transaction analysis
- Risk assessment (Anexo I)
- Formal compliance review (Anexo II - Local File & Master File)
- Technical comments (Anexo III)

---

## File Structure

```
config/yamls/pt_review/
├── manifest.yaml         # Plugin metadata and settings
├── config.yaml          # UI configuration and sections
├── fields.yaml          # All input field definitions
├── texts.yaml           # Fixed text blocks (verbatim)
├── tables.yaml          # Table schemas and layouts
├── logic.yaml           # Conditional rules (DSL only)
├── decision_map.yaml    # Human-readable governance map
├── refs.yaml            # Traceability to Step 1 sources
├── derived.yaml         # Calculated field formulas
├── formatting.yaml      # Date/currency/enum formatting
├── template_patches.md  # Template modification log
├── coverage_matrix.md   # Source coverage verification
├── validation_report.md # Validation results
├── PACK_README.md       # This file
└── sample_inputs/       # Test data vectors
    ├── pt_review_minimal.json
    ├── pt_review_branch_a.json
    └── pt_review_branch_b.json
```

---

## How to Add a New Field

1. **Define the field in `fields.yaml`:**
   ```yaml
   my_new_field:
     type: text        # text, currency, date, enum, list, etc.
     required: true
     label: "My New Field"
     source_block_ids:
       - BLOCK_ID      # From Step 1 document_structure_catalog.md
   ```

2. **Add traceability in `refs.yaml`:**
   ```yaml
   fields:
     my_new_field:
       source_block_ids: [BLOCK_ID]
       step1_catalog: variable_dictionary.md
   ```

3. **Update `config.yaml` to add to UI section:**
   ```yaml
   sections:
     - id: sec_xxx
       fields:
         - my_new_field
   ```

4. **Update template:** Add `{{ my_new_field }}` placeholder to template_final.docx

5. **Update sample inputs:** Add test values to all JSON files in `sample_inputs/`

---

## How to Add a New Conditional Paragraph Variant

1. **Add condition text in `texts.yaml`:**
   ```yaml
   s_my_conditional_text:
     key: s_my_conditional_text
     condition: "my_field == 'some_value'"
     content: |
       The conditional text content goes here.
     source_block_ids:
       - BLOCK_ID
   ```

2. **Add rule in `logic.yaml`:**
   ```yaml
   r0XX:
     rule_id: r0XX
     name: "My Conditional Rule"
     condition:
       operator: equals
       field: my_field
       value: "some_value"
     action:
       type: include_text
       text_key: s_my_conditional_text
     source_block_ids:
       - BLOCK_ID
   ```

3. **Add decision in `decision_map.yaml`:**
   ```yaml
   dX_my_decision:
     decision_id: dX_my_decision
     trigger_condition: "my_field == 'some_value'"
     affected_elements:
       texts: [s_my_conditional_text]
     rules: [r0XX]
   ```

4. **Update template:** Add `{% if condition %}...{% endif %}` in template_final.docx

---

## How to Add a New Repeating Table

1. **Define table in `tables.yaml`:**
   ```yaml
   t_my_table:
     table_id: t_my_table
     repeat: true
     repeat_source: my_list_field
     columns:
       - name: "Column 1"
         type: text
         field: item_field_1
       - name: "Column 2"
         type: currency
         field: item_field_2
   ```

2. **Define list field in `fields.yaml`:**
   ```yaml
   my_list_field:
     type: list
     item_schema:
       item_field_1:
         type: text
       item_field_2:
         type: currency
   ```

3. **Add template loop:**
   ```jinja
   {% for item in my_list_field %}
   | {{ item.item_field_1 }} | {{ item.item_field_2 }} |
   {% endfor %}
   ```

---

## How to Update Template and Keep Traceability

1. **Before editing template_final.docx:**
   - Document current state
   - Identify affected source_block_ids

2. **After editing:**
   - Update `refs.yaml` if new variables added
   - Update `fields.yaml` for new input fields
   - Update `tables.yaml` for table changes
   - Update `texts.yaml` for fixed text changes
   - Update `coverage_matrix.md`

3. **Validation:**
   - Run `validate_plugin` to check integrity
   - Test with all sample_inputs

---

## Common Pitfalls

### Duplicate IDs
- Each `rule_id`, `decision_id`, `text_key`, `table_id` must be unique
- Check `logic.yaml` and `decision_map.yaml` for conflicts

### Illegal Tokens
- Variable names must be snake_case, lowercase, ASCII only
- No spaces in placeholder names
- Use `{{ var }}` not `{{var}}`

### Shadowed Rules
- In `logic.yaml`, first-match wins
- Check `precedence` values to ensure correct evaluation order
- Higher precedence = evaluated first

### Missing References
- Every `source_block_id` must exist in Step 1 catalogs
- Run reference resolver to verify all links

### Nesting Depth
- Max depth 3 for conditional logic
- Avoid complex nested conditions; use derived flags instead

---

## Allowed DSL Operators

The following operators are permitted in `logic.yaml`:

| Category | Operators |
|----------|-----------|
| Logical | `and`, `or`, `not` |
| Equality | `equals`, `not_equals` |
| Comparison | `gt`, `gte`, `lt`, `lte` |
| Membership | `in`, `not_in` |
| Existence | `exists`, `not_exists`, `is_empty`, `not_empty` |
| String | `contains`, `not_contains`, `starts_with`, `ends_with` |

**NOT ALLOWED:** regex, eval, exec, dynamic code execution

---

## Key Decisions

| Decision | Variable | When True | When False |
|----------|----------|-----------|------------|
| Master File Access | `master_file == 1` | Show MF tables & text | Show "no access" warning |
| Service Enabled | `servicio.enabled == true` | Include analysis block | Omit block |
| Comment Required | `cumplido_* in [no, parcial]` | Require texto_cumplido_* | Optional |

---

## Testing

Use the sample_inputs for testing different scenarios:

| File | Scenario | Decisions Covered |
|------|----------|-------------------|
| `pt_review_minimal.json` | Minimal valid input, no Master File | d1 (no access) |
| `pt_review_branch_a.json` | Full data with Master File access | d2, d3, d6 |
| `pt_review_branch_b.json` | Multiple services, partial compliance | d4, d5 |

---

## Maintenance Workflow

1. **Before changes:** Review current state, backup files
2. **Make changes:** Edit YAML files, update template if needed
3. **Update refs:** Ensure `refs.yaml` reflects all changes
4. **Validate:** Run `validate_plugin` script
5. **Test:** Generate documents with all sample_inputs
6. **Document:** Update this README if adding new patterns

---

## Contact

For issues with this plugin pack, refer to:
- Step 1 outputs: `Proces/step1_outputs/`
- Original template: `Plantilla_1231.docx`
- Platform prompts: `Prompts/`
