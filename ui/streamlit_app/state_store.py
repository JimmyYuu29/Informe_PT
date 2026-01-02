# ui/streamlit_app/state_store.py
"""
State Store - Stable session state management for Streamlit.

CRITICAL: This module ensures dynamic inputs (like list/table rows)
don't lose data when the UI re-renders. All form state is stored
in st.session_state with stable keys.
"""
import streamlit as st
from typing import Any, Optional
from datetime import date
import uuid


def init_session_state(plugin_id: str) -> None:
    """
    Initialize session state for a plugin.

    This must be called at the start of the app to ensure
    all state keys exist before widgets are created.
    """
    if "initialized" not in st.session_state:
        st.session_state.initialized = False

    if "plugin_id" not in st.session_state:
        st.session_state.plugin_id = plugin_id

    if "form_data" not in st.session_state:
        st.session_state.form_data = {}

    if "list_items" not in st.session_state:
        st.session_state.list_items = {}

    if "generation_result" not in st.session_state:
        st.session_state.generation_result = None

    if "validation_errors" not in st.session_state:
        st.session_state.validation_errors = []


def get_stable_key(field_name: str, index: Optional[int] = None, sub_field: Optional[str] = None) -> str:
    """
    Generate a stable widget key for a field.

    Using stable keys prevents widget state from being lost
    when the component tree changes.
    """
    if index is not None and sub_field:
        return f"field_{field_name}_{index}_{sub_field}"
    elif index is not None:
        return f"field_{field_name}_{index}"
    else:
        return f"field_{field_name}"


def get_field_value(field_name: str, default: Any = None) -> Any:
    """Get a field value from session state."""
    return st.session_state.form_data.get(field_name, default)


def set_field_value(field_name: str, value: Any) -> None:
    """Set a field value in session state."""
    st.session_state.form_data[field_name] = value


def get_list_items(field_name: str) -> list:
    """Get list items for a repeating field."""
    if field_name not in st.session_state.list_items:
        st.session_state.list_items[field_name] = []
    return st.session_state.list_items[field_name]


def add_list_item(field_name: str, item: dict) -> int:
    """
    Add an item to a list field.

    Returns the index of the new item.
    """
    if field_name not in st.session_state.list_items:
        st.session_state.list_items[field_name] = []

    # Assign a stable ID to the item
    item["_id"] = str(uuid.uuid4())
    st.session_state.list_items[field_name].append(item)
    return len(st.session_state.list_items[field_name]) - 1


def remove_list_item(field_name: str, index: int) -> None:
    """Remove an item from a list field by index."""
    if field_name in st.session_state.list_items:
        items = st.session_state.list_items[field_name]
        if 0 <= index < len(items):
            items.pop(index)


def update_list_item(field_name: str, index: int, key: str, value: Any) -> None:
    """Update a specific field in a list item."""
    if field_name in st.session_state.list_items:
        items = st.session_state.list_items[field_name]
        if 0 <= index < len(items):
            items[index][key] = value


def get_all_form_data() -> dict:
    """
    Get all form data as a dictionary for generation.

    Combines scalar fields and list items.
    Flattens simple text lists (items with only 'value' key) to plain strings.
    """
    data = dict(st.session_state.form_data)

    # Add list items
    for field_name, items in st.session_state.list_items.items():
        # Clean items (remove internal _id field)
        cleaned_items = []
        for item in items:
            cleaned = {k: v for k, v in item.items() if not k.startswith("_")}
            # Flatten simple text lists: if item only has 'value' key, extract the value
            if list(cleaned.keys()) == ["value"]:
                cleaned_items.append(cleaned["value"])
            else:
                cleaned_items.append(cleaned)
        data[field_name] = cleaned_items

    return data


def clear_form_data() -> None:
    """Clear all form data and widget state."""
    st.session_state.form_data = {}
    st.session_state.list_items = {}
    st.session_state.generation_result = None
    st.session_state.validation_errors = []

    # Clear all widget keys related to form inputs to ensure
    # imported values take precedence over old widget state
    # Prefixes used by various form components:
    # - field_: standard field widgets
    # - entidad_: entity detail table widgets
    # - servicio_oovv_: service OOVV table widgets
    # - rm_/add_/remove_: list action buttons
    widget_prefixes = (
        "field_",
        "entidad_",
        "servicio_oovv_",
        "rm_",
        "add_",
        "remove_",
        "_action_",
    )
    keys_to_delete = [
        key for key in st.session_state.keys()
        if any(key.startswith(prefix) for prefix in widget_prefixes)
    ]
    for key in keys_to_delete:
        del st.session_state[key]

    # Set a flag to indicate data was just cleared/imported
    # This helps components prioritize form_data over stale widget state
    st.session_state._data_just_imported = True


def set_generation_result(result: Any) -> None:
    """Store the generation result."""
    st.session_state.generation_result = result


def get_generation_result() -> Any:
    """Get the stored generation result."""
    return st.session_state.generation_result


def set_validation_errors(errors: list) -> None:
    """Store validation errors."""
    st.session_state.validation_errors = errors


def get_validation_errors() -> list:
    """Get stored validation errors."""
    return st.session_state.validation_errors


def sync_widget_to_state(field_name: str, widget_key: str) -> None:
    """
    Callback to sync widget value to form state.

    Use this as on_change callback for widgets.
    """
    if widget_key in st.session_state:
        set_field_value(field_name, st.session_state[widget_key])


def create_sync_callback(field_name: str, widget_key: str):
    """Create a callback function for syncing widget to state."""
    def callback():
        if widget_key in st.session_state:
            set_field_value(field_name, st.session_state[widget_key])
    return callback


def was_data_just_imported() -> bool:
    """
    Check if data was just imported/cleared.

    Returns True only once per import, then clears the flag.
    This helps components prioritize form_data over stale widget state
    after a JSON import.
    """
    return st.session_state.get("_data_just_imported", False)


def clear_import_flag() -> None:
    """Clear the import flag after the first render cycle."""
    if "_data_just_imported" in st.session_state:
        del st.session_state["_data_just_imported"]
