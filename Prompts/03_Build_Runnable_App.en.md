# Step 3 — Build Runnable App (Engine + Streamlit + API + CLI + Tests) (v2.1, 2025-12-31)

ROLE
You are a senior Python engineering lead delivering a runnable, CI-ready repository.

INPUTS (ASSUME AVAILABLE IN REPO)
- Platform prompt: `prompts/enterprise_docgen_platform.superprompt.en.md`
- YAML pack: `config/yamls/<plugin_id>/`
- Final template: `config/templates/<plugin_id>/template_final.docx`
- Optional rules:
  - `docs/rules/yaml_dsl_rules.md`
  - `docs/rules/docx_template_constraints.md`

PRIMARY OBJECTIVE
Deliver a runnable repository with:
- Core engine in `modules/` (plugin-driven from config/yamls)
- Unified entrypoint: `generate(plugin_id, input_data, options)`
- Plugin validator: `validate_plugin` (CI friendly)
- Streamlit UI in `ui/streamlit_app/` driven by fields+config (supports dynamic list[object])
- FastAPI backend in `ui/api/backend/` exposing endpoints to list plugins, validate, schema, generate
- HTML UI integration prompt at `ui/api/ui/FRONTEND_PROMPT.md`
- CLI scripts in `scripts/`
- Tests in `tests/` including at least 1 golden regression

NON-NEGOTIABLE
1) No plugin-specific hardcoding.
2) Controlled DSL only; no eval/exec.
3) Stable Streamlit UI state:
   - session_state is source of truth
   - stable widget keys
   - dynamic add/remove rows without losing inputs
4) Rendering:
   - Use docxtpl for placeholders + simple loops
   - Use python-docx only when needed (e.g., table cell shading for enum states)
5) Traceability:
   - Output trace includes decision hits + rule ids + source_block_ids

REQUIRED OUTPUT STRUCTURE
- `modules/`:
  - plugin_loader.py
  - dsl_allowlist.py
  - contract_models.py (or contracts/ with Pydantic models builder)
  - contract_validator.py
  - rule_engine.py
  - context_builder.py
  - renderer_docx.py
  - audit_logger.py
  - validate_plugin.py
  - generate.py
- `ui/streamlit_app/`:
  - app.py
  - form_renderer.py
  - state_store.py
  - components.py
- `ui/api/backend/`:
  - main.py (FastAPI app)
  - schemas.py
  - deps.py
- `ui/api/ui/FRONTEND_PROMPT.md`:
  - A copy-paste prompt that instructs another AI how to build an HTML UI
  - Must specify endpoint contracts, payloads, auth strategy (even if “none”), CORS, file upload rules
- `scripts/`:
  - run_validate.py
  - run_generate.py
- `tests/`:
  - test_validator.py
  - test_rule_engine.py
  - golden/ (inputs + expected outputs metadata)
- Root `README.md` with run/dev/add-plugin instructions

API ENDPOINT MINIMUM SET (MANDATORY)
- GET `/plugins`
- GET `/plugins/{plugin_id}/schema`
- POST `/plugins/{plugin_id}/validate`
- POST `/plugins/{plugin_id}/generate`  (returns generated file path or bytes, plus trace id)

OUTPUT FORMAT
- Provide file tree
- Provide full contents for each file in fenced code blocks
- Keep code production-grade: type hints, clear errors, logging, minimal dependencies
