#!/usr/bin/env python3
# ui/streamlit_app/app.py
"""
Streamlit Application for Document Generation.

Run with: streamlit run ui/streamlit_app/app.py
"""
import streamlit as st
import sys
import json
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
    st.title("📄 Enterprise Document Generation Platform")

    # Sidebar - Plugin selection
    with st.sidebar:
        st.header("Plugin Selection")

        available_plugins = list_plugins()
        if not available_plugins:
            st.error("No plugins found in config/yamls/")
            st.stop()

        selected_plugin = st.selectbox(
            "Select Plugin",
            options=available_plugins,
            index=0,
        )

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

        # Actions
        st.header("Actions")

        if st.button("Clear Form", use_container_width=True):
            state.clear_form_data()
            st.rerun()

    # Initialize state
    state.init_session_state(selected_plugin)

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


def load_json_data(json_data: dict) -> None:
    """
    Load JSON data into the form state.

    Handles both simple fields and complex list structures.
    """
    # Remove metadata if present
    if "_metadata" in json_data:
        del json_data["_metadata"]

    # Process each field
    for key, value in json_data.items():
        if isinstance(value, list):
            # Handle list fields
            if key in st.session_state.list_items:
                st.session_state.list_items[key] = []
            else:
                st.session_state.list_items[key] = []

            for item in value:
                if isinstance(item, dict):
                    state.add_list_item(key, item)
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
