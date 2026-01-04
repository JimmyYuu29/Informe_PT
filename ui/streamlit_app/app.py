#!/usr/bin/env python3
# ui/streamlit_app/app.py
"""
Streamlit Application for Document Generation.

Run with: streamlit run ui/streamlit_app/app.py
"""
import streamlit as st
import sys
import json
import copy
from collections import OrderedDict
from pathlib import Path
from datetime import date

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from modules.plugin_loader import PluginPack, load_plugin, list_plugins
from modules.generate import generate, GenerationOptions
from modules.validate_plugin import validate_plugin

from ui.streamlit_app import state_store as state
from ui.streamlit_app import components
from ui.streamlit_app import form_renderer


# Page configuration
st.set_page_config(
    page_title="Document Generation Platform",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded",
)


def main():
    """Main application entry point."""
    st.title("Enterprise Document Generation Platform")

    # Get available plugins first
    available_plugins = list_plugins()
    if not available_plugins:
        st.error("No plugins found in config/yamls/")
        st.stop()

    # Initialize session state with default plugin
    default_plugin = available_plugins[0]
    current_plugin = st.session_state.get("plugin_id", default_plugin)
    if current_plugin not in available_plugins:
        current_plugin = default_plugin
    state.init_session_state(current_plugin)

    # Sidebar - Plugin selection
    with st.sidebar:
        st.header("Plugin Selection")

        selected_plugin = st.selectbox(
            "Select Plugin",
            options=available_plugins,
            index=available_plugins.index(current_plugin) if current_plugin in available_plugins else 0,
        )

        # Update session state if plugin changed
        if selected_plugin != st.session_state.get("plugin_id"):
            st.session_state.plugin_id = selected_plugin

        # Plugin info
        if selected_plugin:
            try:
                plugin = load_plugin(selected_plugin)
                st.info(f"**{plugin.manifest.get('name', selected_plugin)}**")
                st.caption(plugin.manifest.get('description', ''))
            except Exception as e:
                st.error(f"Error loading plugin: {e}")
                st.stop()

        st.divider()

        # Validate plugin button
        if st.button("Validate Plugin", use_container_width=True):
            with st.spinner("Validating..."):
                result = validate_plugin(selected_plugin)

            if result.is_valid:
                st.success("Plugin is valid!")
            else:
                st.error("Plugin validation failed")

            if result.errors:
                with st.expander("Errors", expanded=True):
                    for error in result.errors:
                        st.error(error)

            if result.warnings:
                with st.expander("Warnings"):
                    for warning in result.warnings:
                        st.warning(warning)

        st.divider()

        # JSON Import Section
        st.header("Import Data")
        uploaded_file = st.file_uploader(
            "Import JSON Metadata",
            type=["json"],
            help="Upload a JSON file with form data to pre-fill the form",
        )

        if uploaded_file is not None:
            try:
                json_data = json.load(uploaded_file)
                if st.button("Load JSON Data", use_container_width=True):
                    load_json_data(json_data)
                    st.success("JSON data loaded successfully!")
                    st.rerun()
            except json.JSONDecodeError as e:
                st.error(f"Invalid JSON file: {e}")
            except Exception as e:
                st.error(f"Error loading JSON: {e}")

        st.divider()

        # JSON Export Section
        st.header("Export Data")
        export_data = export_form_data()
        st.download_button(
            label="Export to JSON",
            data=export_data,
            file_name="form_data.json",
            mime="application/json",
            use_container_width=True,
        )

        st.divider()

        # Actions
        st.header("Actions")

        if st.button("Clear Form", use_container_width=True):
            state.clear_form_data()
            st.rerun()

    # Load plugin
    try:
        plugin = load_plugin(selected_plugin)
    except Exception as e:
        st.error(f"Failed to load plugin: {e}")
        st.stop()

    # Main content - Form
    # Note: Not using st.form() because dynamic lists require st.button()
    # for add/remove functionality, which is not allowed inside forms.
    st.header("Input Data")

    # Render dynamic form
    form_data = form_renderer.render_form(plugin)

    # Clear import flag after form rendering is complete
    # This ensures the flag only affects the first render after import
    state.clear_import_flag()

    st.divider()

    # Generate button
    if st.button(
        "Generate Document",
        type="primary",
        use_container_width=True,
    ):
        generate_document(selected_plugin, form_data)

    # Show results
    show_results()


def _get_risk_field_order() -> list[str]:
    """Return the risk table field order as shown in the UI."""
    ordered_fields = []
    for idx in range(1, 13):
        ordered_fields.extend([
            f"impacto_{idx}",
            f"afectacion_pre_{idx}",
            f"texto_mitigacion_{idx}",
            f"afectacion_final_{idx}",
        ])
    return ordered_fields


def _get_compliance_detail_order(prefix: str, total_rows: int) -> list[str]:
    """Return the compliance detail field order as shown in the UI."""
    ordered_fields = []
    for idx in range(1, total_rows + 1):
        ordered_fields.extend([
            f"cumplido_{prefix}_{idx}",
            f"texto_cumplido_{prefix}_{idx}",
        ])
    return ordered_fields


def _get_financials_field_order() -> list[str]:
    """Return the financial data field order as shown in the UI."""
    return [
        "cifra_1", "cifra_0",
        "ebit_1", "ebit_0",
        "resultado_fin_1", "resultado_fin_0",
        "ebt_1", "ebt_0",
        "resultado_net_1", "resultado_net_0",
    ]


def _get_compliance_resumen_order(prefix: str, total_rows: int) -> list[str]:
    """Return the compliance resumen field order as shown in the UI."""
    return [f"cumplimiento_resumen_{prefix}_{i}" for i in range(1, total_rows + 1)]


def _get_contacts_field_order() -> list[str]:
    """Return the contacts field order as shown in the UI."""
    fields = []
    for i in range(1, 4):
        fields.extend([
            f"contacto{i}",
            f"cargo_contacto{i}",
            f"correo_contacto{i}",
        ])
    return fields


def _get_export_field_order(plugin: PluginPack) -> list[str]:
    """Return form field names in the same order as the UI sections."""
    ordered_fields: list[str] = []
    for section in plugin.get_ui_sections():
        section_id = section.get("id", "")
        field_names = section.get("fields", [])

        if section_id == "sec_general":
            # Explicit order for Información General
            ordered_fields.extend([
                "fecha_fin_fiscal",
                "entidad_cliente",
                "master_file",
                "descripcion_actividad",
            ])
        elif section_id == "sec_financials":
            # Explicit order for Datos Financieros
            ordered_fields.extend(_get_financials_field_order())
        elif section_id == "sec_compliance_local":
            # Explicit order for Cumplimiento Local File (Resumen)
            ordered_fields.extend(_get_compliance_resumen_order("local", 3))
        elif section_id == "sec_compliance_master":
            # Explicit order for Cumplimiento Master File (Resumen)
            ordered_fields.extend(_get_compliance_resumen_order("mast", 4))
        elif section_id == "sec_risks" or "risk_elements" in field_names:
            ordered_fields.extend(_get_risk_field_order())
        elif section_id == "sec_local_detail" or "local_file_compliance" in field_names:
            ordered_fields.extend(_get_compliance_detail_order("local", 14))
        elif section_id == "sec_master_detail" or "master_file_compliance" in field_names:
            ordered_fields.extend(_get_compliance_detail_order("mast", 17))
        elif section_id == "sec_anexo3":
            # Explicit order for Anexo III - Comentarios
            ordered_fields.append("texto_anexo3")
        elif section_id == "sec_contacts":
            # Explicit order for Contactos
            ordered_fields.extend(_get_contacts_field_order())
        else:
            ordered_fields.extend(field_names)

    return ordered_fields


def export_form_data() -> str:
    """
    Export current form data to JSON string.

    Exports both scalar form_data and list_items separately to ensure
    complete data restoration on import.

    Returns:
        JSON string of form data, or empty string if no data.
    """
    # Convert date objects to ISO format strings
    def serialize_value(v):
        if isinstance(v, date):
            return v.isoformat()
        elif isinstance(v, list):
            return [serialize_value(item) for item in v]
        elif isinstance(v, dict):
            return {k: serialize_value(val) for k, val in v.items()}
        return v

    plugin_id = st.session_state.get("plugin_id", "unknown")
    if "form_data" not in st.session_state or "list_items" not in st.session_state:
        state.init_session_state(plugin_id)
    plugin = load_plugin(plugin_id)
    ordered_fields = _get_export_field_order(plugin)
    form_data = st.session_state.get("form_data", {})
    list_items = st.session_state.get("list_items", {})
    list_field_names = set(list_items.keys())

    # Export scalar fields in UI order
    serialized: OrderedDict[str, object] = OrderedDict()

    # Export scalar fields in UI order
    for field_name in ordered_fields:
        if field_name in list_field_names:
            continue
        if field_name in form_data:
            serialized[field_name] = serialize_value(form_data[field_name])

    # Append any remaining scalar fields not defined in UI order
    for k, v in form_data.items():
        if k in serialized or k in list_field_names:
            continue
        serialized[k] = serialize_value(v)

    # Export list items with full structure (including nested lists)
    list_items_serialized: OrderedDict[str, list] = OrderedDict()
    ordered_list_fields = [name for name in ordered_fields if name in list_items]
    for field_name in ordered_list_fields:
        items = list_items[field_name]
        list_items_serialized[field_name] = []
        for item in items:
            # Remove internal _id field but keep all other data
            cleaned = {k: serialize_value(v) for k, v in item.items() if not k.startswith("_")}
            list_items_serialized[field_name].append(cleaned)
    for field_name, items in list_items.items():
        if field_name in list_items_serialized:
            continue
        list_items_serialized[field_name] = []
        for item in items:
            cleaned = {k: serialize_value(v) for k, v in item.items() if not k.startswith("_")}
            list_items_serialized[field_name].append(cleaned)

    serialized["_list_items"] = list_items_serialized

    # Add metadata
    serialized["_metadata"] = {
        "exported_at": date.today().isoformat(),
        "plugin_id": plugin_id,
        "version": "2.0",  # Version 2.0 with improved list handling
    }

    return json.dumps(serialized, ensure_ascii=False, indent=2)


def _force_clear_widget_state() -> None:
    """
    Force clear all widget state keys that might interfere with imported data.

    This is a comprehensive cleanup that ensures Streamlit widgets will use
    the imported values from form_data/list_items instead of cached widget state.
    """
    # List of all possible widget key patterns used in the application
    # This must be kept in sync with the widget keys used in form_renderer.py
    # and components.py
    patterns_to_clear = []

    # Collect all keys that match common widget patterns
    for key in list(st.session_state.keys()):
        # Skip internal state keys
        if key in ("initialized", "plugin_id", "form_data", "list_items",
                   "generation_result", "validation_errors", "_data_just_imported"):
            continue

        # Skip metadata keys
        if key.startswith("_"):
            continue

        # Clear any key that looks like a widget key
        # Widget keys typically have patterns like field_xxx, entidad_x_x_xxx, etc.
        if any(pattern in key for pattern in (
            "field_", "entidad_", "servicio_", "analizar_", "impacto_",
            "afectacion_", "texto_", "cumplido_", "cumplimiento_",
            "rm_", "add_", "remove_", "_action_",
            # Additional patterns for sec_general, sec_anexo3, sec_contacts, sec_financials
            "contacto", "cargo_", "correo_", "fecha_", "master_",
            "descripcion_", "cifra_", "ebit_", "resultado_", "ebt_"
        )):
            patterns_to_clear.append(key)

    # Delete the collected keys
    for key in patterns_to_clear:
        if key in st.session_state:
            del st.session_state[key]


def _coerce_widget_value(value):
    """Normalize imported scalar values to widget-friendly types."""
    if isinstance(value, str):
        try:
            return date.fromisoformat(value)
        except ValueError:
            return value
    return value


def load_json_data(json_data: dict) -> None:
    """
    Load JSON data into the form state.

    Handles both simple fields and complex list structures.
    Supports both v1.0 format (lists at top level) and v2.0 format (_list_items).
    Uses deep copy for nested structures to prevent reference issues.

    CRITICAL: This function must properly clear all widget state to ensure
    Streamlit widgets display the imported values instead of cached values.
    """
    # Normalize payloads that wrap data under form_data/list_items
    if isinstance(json_data.get("form_data"), dict):
        normalized = dict(json_data["form_data"])
        if "_metadata" in json_data:
            normalized["_metadata"] = json_data["_metadata"]
        if "_list_items" in json_data:
            normalized["_list_items"] = json_data["_list_items"]
        if "list_items" in json_data and "_list_items" not in normalized:
            normalized["_list_items"] = json_data["list_items"]
        json_data = normalized

    def _set_scalar_field(key: str, value) -> None:
        """Set both form_data and widget state for scalar fields."""
        widget_key = state.get_stable_key(key)
        coerced = _coerce_widget_value(value)
        try:
            st.session_state[widget_key] = coerced
        except Exception:
            st.session_state[widget_key] = value
        state.set_field_value(key, coerced)

    # FIRST: Force clear all widget state BEFORE clearing form data
    # This ensures no stale widget values interfere with import
    _force_clear_widget_state()

    # Clear existing form data (this also clears widget state keys and sets import flag)
    state.clear_form_data()

    # Extract metadata and list items without mutating original dict
    metadata = json_data.get("_metadata", {})
    list_items_data = json_data.get("_list_items", None)

    # Check export version
    is_v2 = metadata.get("version") == "2.0" or list_items_data is not None

    # Track which fields are list fields to avoid double processing
    list_field_names = set()

    if is_v2 and list_items_data:
        # V2.0 format: list items are stored separately in _list_items
        list_field_names = set(list_items_data.keys())

        # Process list items from _list_items using deep copy
        for field_name, items in list_items_data.items():
            st.session_state.list_items[field_name] = []
            for item in items:
                if isinstance(item, dict):
                    # Use deep copy to preserve nested structures
                    state.add_list_item(field_name, copy.deepcopy(item))
                else:
                    state.add_list_item(field_name, {"value": item})

        # Process ALL scalar fields (exclude only internal keys and list fields)
        for key, value in json_data.items():
            if key.startswith("_"):
                continue
            if key in list_field_names:
                continue
            if isinstance(value, list):
                # This is a list at top level that wasn't in _list_items
                # Process it as a list field
                st.session_state.list_items[key] = []
                for item in value:
                    if isinstance(item, dict):
                        state.add_list_item(key, copy.deepcopy(item))
                    else:
                        state.add_list_item(key, {"value": item})
            else:
                # Handle scalar fields - including all sections:
                # sec_general, sec_financials, sec_anexo3, sec_contacts, etc.
                _set_scalar_field(key, value)
    else:
        # V1.0 format: lists are mixed with scalar fields
        for key, value in json_data.items():
            if key.startswith("_"):
                continue

            if isinstance(value, list):
                # Handle list fields using deep copy
                st.session_state.list_items[key] = []
                for item in value:
                    if isinstance(item, dict):
                        state.add_list_item(key, copy.deepcopy(item))
                    else:
                        state.add_list_item(key, {"value": item})
            else:
                # Handle scalar fields
                _set_scalar_field(key, value)

    # Ensure the import flag is still set after all operations
    st.session_state._data_just_imported = True


def generate_document(plugin_id: str, form_data: dict) -> None:
    """Generate the document with the provided data."""
    # Collect all form data including list items
    all_data = state.get_all_form_data()

    # Convert date to string for JSON compatibility
    for key, value in all_data.items():
        if isinstance(value, date):
            all_data[key] = value.isoformat()

    with st.spinner("Generating document..."):
        options = GenerationOptions(
            validate=True,
            strict_validation=False,  # Generate even with validation errors
            apply_cell_colors=True,
            save_trace=True,
        )

        result = generate(plugin_id, all_data, options)
        state.set_generation_result(result)

        if result.validation_result and result.validation_result.errors:
            state.set_validation_errors(result.validation_result.errors)


def show_results() -> None:
    """Display generation results."""
    result = state.get_generation_result()
    errors = state.get_validation_errors()

    if errors:
        components.render_validation_errors(errors)

    if result:
        if result.success:
            components.render_success_message(
                str(result.output_path) if result.output_path else "",
                result.trace_id,
            )

            # Show trace info
            if result.evaluation_traces:
                with st.expander("Decision Trace"):
                    for trace in result.evaluation_traces:
                        st.markdown(f"**{trace.decision_name}**")
                        for hit in trace.rule_hits:
                            status = "✅" if hit.condition_met else "❌"
                            st.text(f"  {status} {hit.rule_id}: {hit.rule_name}")
        else:
            if result.error:
                st.error(f"Generation failed: {result.error}")


# Tab-based sections for complex plugins
def render_tabs(plugin):
    """Render form in tabs for better organization."""
    fields_def = plugin.get_field_definitions()
    sections = plugin.get_ui_sections()

    if not sections:
        form_renderer.render_form(plugin)
        return

    # Group sections into tabs
    tab_names = [s.get("label", s.get("id", f"Section {i}")) for i, s in enumerate(sections)]
    tabs = st.tabs(tab_names)

    context = state.get_all_form_data()

    for tab, section in zip(tabs, sections):
        with tab:
            form_renderer.render_section(section, fields_def, context)


if __name__ == "__main__":
    main()
