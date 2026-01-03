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
from pathlib import Path
from datetime import date

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from modules.plugin_loader import load_plugin, list_plugins
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

    # Export scalar fields
    serialized = {}
    for k, v in st.session_state.form_data.items():
        serialized[k] = serialize_value(v)

    # Export list items with full structure (including nested lists)
    serialized["_list_items"] = {}
    for field_name, items in st.session_state.list_items.items():
        serialized["_list_items"][field_name] = []
        for item in items:
            # Remove internal _id field but keep all other data
            cleaned = {k: serialize_value(v) for k, v in item.items() if not k.startswith("_")}
            serialized["_list_items"][field_name].append(cleaned)

    # Add metadata
    serialized["_metadata"] = {
        "exported_at": date.today().isoformat(),
        "plugin_id": st.session_state.get("plugin_id", "unknown"),
        "version": "2.0",  # Version 2.0 with improved list handling
    }

    return json.dumps(serialized, ensure_ascii=False, indent=2)


def load_json_data(json_data: dict) -> None:
    """
    Load JSON data into the form state.

    Handles both simple fields and complex list structures.
    Supports both v1.0 format (lists at top level) and v2.0 format (_list_items).
    Uses deep copy for nested structures to prevent reference issues.
    """
    # Clear existing form data (this also clears widget state keys)
    state.clear_form_data()

    # Extract metadata and list items without mutating original dict
    metadata = json_data.get("_metadata", {})
    list_items_data = json_data.get("_list_items", None)

    # Check export version
    is_v2 = metadata.get("version") == "2.0" or list_items_data is not None

    if is_v2 and list_items_data:
        # V2.0 format: list items are stored separately in _list_items
        # First, process scalar fields (exclude fields that are in list_items)
        for key, value in json_data.items():
            if not key.startswith("_") and key not in list_items_data:
                state.set_field_value(key, value)

        # Then, process list items from _list_items using deep copy
        for field_name, items in list_items_data.items():
            st.session_state.list_items[field_name] = []
            for item in items:
                if isinstance(item, dict):
                    # Use deep copy to preserve nested structures
                    state.add_list_item(field_name, copy.deepcopy(item))
                else:
                    state.add_list_item(field_name, {"value": item})
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
                state.set_field_value(key, value)


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
