# Validation Report

**Plugin ID:** pt_review
**Generated:** 2025-12-31 | Step 2 - YAML Pack Generation
**Status:** PASSED

---

## 1. File Completeness Check

| Required File | Status | Notes |
|---------------|--------|-------|
| manifest.yaml | PRESENT | Version 1.0.0 |
| config.yaml | PRESENT | 13 UI sections defined |
| fields.yaml | PRESENT | 150+ fields defined |
| texts.yaml | PRESENT | 25+ text blocks |
| tables.yaml | PRESENT | 9 tables defined |
| logic.yaml | PRESENT | 9 rules defined |
| decision_map.yaml | PRESENT | 6 decisions mapped |
| refs.yaml | PRESENT | Full traceability |
| derived.yaml | PRESENT | 18 derived fields |
| formatting.yaml | PRESENT | 4 color maps defined |
| template_patches.md | PRESENT | No unresolved patches |
| coverage_matrix.md | PRESENT | 100% coverage |
| PACK_README.md | PRESENT | Maintenance guide |
| sample_inputs/*.json | PRESENT | 3 vectors |

**Result: 14/14 files present**

---

## 2. Reference Integrity Check

### 2.1 Field References
All field references in logic.yaml, tables.yaml, and texts.yaml resolve to definitions in fields.yaml or derived.yaml.

| Check | Count | Status |
|-------|-------|--------|
| Fields referenced in logic.yaml | 25 | RESOLVED |
| Fields referenced in tables.yaml | 80+ | RESOLVED |
| Fields referenced in texts.yaml | 15 | RESOLVED |
| Orphan field definitions | 0 | NONE |

### 2.2 Source Block ID References
All source_block_ids reference valid blocks from Step 1 document_structure_catalog.md.

| Catalog | Referenced IDs | Status |
|---------|----------------|--------|
| document_structure_catalog.md | 85 | VERIFIED |
| variable_dictionary.md | 150+ | VERIFIED |
| conditional_logic_catalog.md | 5 conditions, 10 derivations | VERIFIED |
| tables_catalog.md | 9 tables | VERIFIED |
| author_notes_catalog.md | 12 notes | VERIFIED |

**Result: All references resolve**

---

## 3. DSL Compliance Check

### 3.1 Allowed Operators
All operators in logic.yaml are from the allowlist:

| Operator | Used In | Status |
|----------|---------|--------|
| equals | r001-r009 | ALLOWED |
| or | r006, r007 | ALLOWED |
| and | r007 | ALLOWED |

### 3.2 Nesting Depth
Maximum nesting depth found: **2** (in r007)

| Rule | Max Depth | Status |
|------|-----------|--------|
| r001 | 1 | OK |
| r002 | 1 | OK |
| r003 | 1 | OK |
| r004 | 1 | OK |
| r005 | 1 | OK |
| r006 | 2 | OK |
| r007 | 2 | OK |
| r008 | 1 | OK |
| r009 | 1 | OK |

**Result: All rules comply (max depth ≤ 3)**

### 3.3 Forbidden Patterns
| Pattern | Found | Status |
|---------|-------|--------|
| regex | No | OK |
| eval | No | OK |
| exec | No | OK |
| dynamic injection | No | OK |

**Result: No forbidden patterns detected**

---

## 4. Sample Input Validation

### 4.1 Vector: pt_review_minimal.json

**Scenario:** Minimal valid input, no Master File access

| Decision | Expected Outcome | Validated |
|----------|------------------|-----------|
| d1_master_file_access | Show "no access" warning (master_file=0) | YES |
| d2_master_file_formal | Hide Master File tables | YES |
| d3_master_file_detailed | Hide Table 9 | YES |
| d4_service_activation | No service blocks (empty servicios_oovv) | YES |
| d5_compliance_comment | No comments required (all cumplido=si) | YES |
| d6_master_file_fields | Master File fields not required | YES |

**Derived Fields Test:**
| Field | Input | Expected | Status |
|-------|-------|----------|--------|
| anyo_ejercicio | 2024-12-31 | 2024 | OK |
| anyo_ejercicio_ant | - | 2023 | OK |
| cost_1 | cifra_1=15M, ebit_1=1.2M | 13.8M | OK |
| om_1 | ebit_1/cifra_1 | 8.00% | OK |
| total_gasto_oov | SUM(gastos) | 250,000 | OK |

**Result: PASSED**

---

### 4.2 Vector: pt_review_branch_a.json

**Scenario:** Full data with Master File access

| Decision | Expected Outcome | Validated |
|----------|------------------|-----------|
| d1_master_file_access | Hide "no access" warning (master_file=1) | YES |
| d2_master_file_formal | Show Table 8, show conclusion text | YES |
| d3_master_file_detailed | Show Table 11 (17 rows) | YES |
| d4_service_activation | 1 service block enabled | YES |
| d5_compliance_comment | Comment required for cumplido_local_3=parcial | YES |
| d6_master_file_fields | All cumplido_mast_* required | YES |

**Derived Fields Test:**
| Field | Input | Expected | Status |
|-------|-------|----------|--------|
| anyo_ejercicio | 2024-12-31 | 2024 | OK |
| cost_1 | cifra_1=85M, ebit_1=4.25M | 80.75M | OK |
| total_gasto_oov | SUM(all gastos) | 74.65M | OK |
| peso_oov_sobre_costes | 74.65M / 80.75M | 92.44% | OK |

**Result: PASSED**

---

### 4.3 Vector: pt_review_branch_b.json

**Scenario:** Multiple services, partial compliance

| Decision | Expected Outcome | Validated |
|----------|------------------|-----------|
| d1_master_file_access | Show "no access" warning (master_file=0) | YES |
| d4_service_activation | 2 service blocks enabled (1 disabled) | YES |
| d5_compliance_comment | Comments required for: | |
| | - cumplido_local_2=parcial | YES |
| | - cumplido_local_3=no | YES |
| | - cumplido_local_6=parcial | YES |
| | - cumplido_local_12=parcial | YES |

**Service Block Test:**
| Service | enabled | Included | Status |
|---------|---------|----------|--------|
| Desarrollo de software | true | YES | OK |
| Consultoría IT | true | YES | OK |
| Soporte técnico | false | NO | OK |

**Derived Fields Test:**
| Field | Input | Expected | Status |
|-------|-------|----------|--------|
| anyo_ejercicio | 2024-12-31 | 2024 | OK |
| total_ingreso_oov | 12M + 8M + 3.5M | 23.5M | OK |
| total_gasto_oov | 0.8M | 0.8M | OK |
| peso_oov_sobre_incn | 23.5M / 25M | 94.00% | OK |

**Result: PASSED**

---

## 5. Decision Coverage Summary

| Decision ID | Description | Covered By |
|-------------|-------------|------------|
| d1_master_file_access | No access warning | minimal, branch_b |
| d2_master_file_formal | MF formal perspective | branch_a |
| d3_master_file_detailed | MF detailed table | branch_a |
| d4_service_activation | Service blocks | branch_a (1), branch_b (2) |
| d5_compliance_comment | Comment requirement | branch_a (1), branch_b (4) |
| d6_master_file_fields | MF fields required | branch_a |

**Coverage: 6/6 decisions (100%)**

---

## 6. Type Consistency Check

All field types are consistent between fields.yaml, derived.yaml, and sample inputs:

| Type | Count | Sample Validation |
|------|-------|-------------------|
| text | 45+ | String values | OK |
| date | 1 | ISO format | OK |
| currency | 20+ | Numeric values | OK |
| decimal | 15+ | Numeric with precision | OK |
| enum | 80+ | Values in allowed list | OK |
| list | 3 | Array structures | OK |
| bool | 1 | true/false | OK |

**Result: All types consistent**

---

## 7. Validation Summary

| Category | Status |
|----------|--------|
| File Completeness | PASSED (14/14) |
| Reference Integrity | PASSED |
| DSL Compliance | PASSED (depth ≤ 3) |
| Sample Validation | PASSED (3/3) |
| Decision Coverage | PASSED (6/6) |
| Type Consistency | PASSED |

---

## Final Result: ALL CHECKS PASSED

The YAML pack is valid and ready for Step 3 (Build Runnable App).

---

## Notes for Step 3

1. **Template Binding:** Verify template_final.docx placeholders match fields.yaml definitions
2. **Derived Calculation:** Implement derived.yaml formulas with proper error handling for division by zero
3. **Conditional Rendering:** Logic.yaml rules must be evaluated in precedence order
4. **Color Formatting:** Implement formatting.yaml color maps for enum cells in tables
5. **Validation:** Implement COND_005 validation for required comments

---

## Appendix: Derived Field Calculation Examples

### From pt_review_branch_a.json:

```
Input:
  fecha_fin_fiscal: 2024-12-31
  cifra_1: 85,000,000
  ebit_1: 4,250,000

Calculations:
  anyo_ejercicio = YEAR(2024-12-31) = 2024
  anyo_ejercicio_ant = 2024 - 1 = 2023
  cost_1 = 85,000,000 - 4,250,000 = 80,750,000
  om_1 = (4,250,000 / 85,000,000) * 100 = 5.00%
  ncp_1 = (4,250,000 / 80,750,000) * 100 = 5.26%

Linked Operations:
  total_gasto_oov = 1,200,000 + 450,000 + 45,000,000 + 28,000,000 = 74,650,000
  peso_oov_sobre_costes = (74,650,000 / 80,750,000) * 100 = 92.44%
```
