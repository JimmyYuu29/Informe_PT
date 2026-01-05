# ui/streamlit_app/components.py
"""
Reusable UI components for Streamlit.
"""
import streamlit as st
from datetime import date
from typing import Any, Callable, Optional
from ui.streamlit_app import state_store as state


def render_text_input(
    field_name: str,
    label: str,
    required: bool = False,
    multiline: bool = False,
    help_text: Optional[str] = None,
    max_length: Optional[int] = None,
) -> str:
    """Render a text input field with stable state."""
    widget_key = state.get_stable_key(field_name)

    # After JSON import, prioritize form_data over stale widget state
    # Otherwise check if widget key already exists in session_state
    if state.was_data_just_imported():
        default_value = state.get_field_value(field_name, "")
    elif widget_key in st.session_state:
        default_value = st.session_state[widget_key]
    else:
        default_value = state.get_field_value(field_name, "")

    label_display = f"{label} *" if required else label

    if multiline:
        value = st.text_area(
            label_display,
            value=default_value,
            key=widget_key,
            help=help_text,
            max_chars=max_length,
        )
    else:
        value = st.text_input(
            label_display,
            value=default_value,
            key=widget_key,
            help=help_text,
            max_chars=max_length,
        )

    # Always sync widget value back to form_data
    state.set_field_value(field_name, value)
    return value


def render_date_input(
    field_name: str,
    label: str,
    required: bool = False,
    help_text: Optional[str] = None,
) -> Optional[date]:
    """Render a date input field with stable state."""
    widget_key = state.get_stable_key(field_name)

    # After JSON import, prioritize form_data over stale widget state
    # Otherwise check if widget key already exists in session_state
    if state.was_data_just_imported():
        default_value = state.get_field_value(field_name)
    elif widget_key in st.session_state:
        default_value = st.session_state[widget_key]
    else:
        default_value = state.get_field_value(field_name)

    if default_value is None:
        default_value = date.today()
    elif isinstance(default_value, str):
        try:
            parts = default_value.split("-")
            default_value = date(int(parts[0]), int(parts[1]), int(parts[2]))
        except Exception:
            default_value = date.today()

    label_display = f"{label} *" if required else label

    value = st.date_input(
        label_display,
        value=default_value,
        key=widget_key,
        help=help_text,
    )

    state.set_field_value(field_name, value)
    return value


def render_number_input(
    field_name: str,
    label: str,
    required: bool = False,
    is_currency: bool = False,
    min_value: Optional[float] = None,
    max_value: Optional[float] = None,
    help_text: Optional[str] = None,
) -> Optional[float]:
    """Render a number input field with stable state."""
    widget_key = state.get_stable_key(field_name)

    # After JSON import, prioritize form_data over stale widget state
    # Otherwise check if widget key already exists in session_state
    if state.was_data_just_imported():
        default_value = state.get_field_value(field_name, 0.0)
    elif widget_key in st.session_state:
        default_value = st.session_state[widget_key]
    else:
        default_value = state.get_field_value(field_name, 0.0)

    try:
        default_value = float(default_value) if default_value else 0.0
    except (TypeError, ValueError):
        default_value = 0.0

    label_display = f"{label} *" if required else label
    if is_currency:
        label_display += " (EUR)"

    value = st.number_input(
        label_display,
        value=default_value,
        min_value=min_value,
        max_value=max_value,
        key=widget_key,
        help=help_text,
        format="%.2f" if is_currency else "%.0f",
    )

    state.set_field_value(field_name, value)
    return value


def render_enum_input(
    field_name: str,
    label: str,
    options: list,
    required: bool = False,
    help_text: Optional[str] = None,
    default: Optional[str] = None,
) -> Optional[str]:
    """Render an enum/select input field with stable state."""
    widget_key = state.get_stable_key(field_name)

    # After JSON import, prioritize form_data over stale widget state
    # Otherwise check if widget key already exists in session_state
    if state.was_data_just_imported():
        current_value = state.get_field_value(field_name)
    elif widget_key in st.session_state:
        current_value = st.session_state[widget_key]
    else:
        current_value = state.get_field_value(field_name)

    # Process options
    if options and isinstance(options[0], dict):
        option_labels = [opt.get("label", opt.get("value", "")) for opt in options]
        option_values = [opt.get("value", opt.get("label", "")) for opt in options]
    else:
        option_labels = [str(opt) for opt in options]
        option_values = list(options)

    # Find index for current value, or use default
    # Normalize current_value for comparison (handle int/str mismatch)
    default_index = 0
    found = False

    if current_value is not None:
        # Try direct match first
        if current_value in option_values:
            default_index = option_values.index(current_value)
            found = True
        elif current_value in option_labels:
            default_index = option_labels.index(current_value)
            found = True
        else:
            # Try string conversion for integer values (e.g., master_file: 0/1)
            str_value = str(current_value)
            for idx, val in enumerate(option_values):
                if str(val) == str_value:
                    default_index = idx
                    found = True
                    break
            if not found:
                for idx, lbl in enumerate(option_labels):
                    if str(lbl) == str_value:
                        default_index = idx
                        found = True
                        break

    if not found and default is not None:
        if default in option_values:
            default_index = option_values.index(default)
        elif str(default) in [str(v) for v in option_values]:
            default_index = [str(v) for v in option_values].index(str(default))

    # Ensure default_index is always a valid integer
    if not isinstance(default_index, int) or default_index < 0 or default_index >= len(option_labels):
        default_index = 0

    label_display = f"{label} *" if required else label

    selected_label = st.selectbox(
        label_display,
        options=option_labels,
        index=default_index,
        key=widget_key,
        help=help_text,
    )

    # Get actual value
    try:
        selected_index = option_labels.index(selected_label)
        value = option_values[selected_index]
    except (ValueError, IndexError):
        value = selected_label

    state.set_field_value(field_name, value)
    return value


def render_checkbox(
    field_name: str,
    label: str,
    help_text: Optional[str] = None,
) -> bool:
    """Render a checkbox input with stable state."""
    widget_key = state.get_stable_key(field_name)

    # After JSON import, prioritize form_data over stale widget state
    # Otherwise check if widget key already exists in session_state
    if state.was_data_just_imported():
        default_value = state.get_field_value(field_name, False)
    elif widget_key in st.session_state:
        default_value = st.session_state[widget_key]
    else:
        default_value = state.get_field_value(field_name, False)

    value = st.checkbox(
        label,
        value=bool(default_value),
        key=widget_key,
        help=help_text,
    )

    state.set_field_value(field_name, value)
    return value


def render_dynamic_list(
    field_name: str,
    label: str,
    item_fields: list[dict],
    min_items: int = 0,
    help_text: Optional[str] = None,
) -> None:
    """
    Render a dynamic list input where rows can be added/removed.

    CRITICAL: Uses stable keys and state management to prevent
    data loss during re-renders.
    """
    st.subheader(label)
    if help_text:
        st.caption(help_text)

    items = state.get_list_items(field_name)

    # Render existing items
    for idx, item in enumerate(items):
        with st.container():
            cols = st.columns([0.9, 0.1])

            with cols[0]:
                st.markdown(f"**Item {idx + 1}**")

                for field_def in item_fields:
                    sub_field = field_def["name"]
                    sub_label = field_def.get("label", sub_field)
                    sub_type = field_def.get("type", "text")
                    sub_required = field_def.get("required", False)

                    widget_key = state.get_stable_key(field_name, idx, sub_field)

                    # After JSON import, prioritize list_items over stale widget state
                    if state.was_data_just_imported():
                        current_value = item.get(sub_field, "")
                    elif widget_key in st.session_state:
                        current_value = st.session_state[widget_key]
                    else:
                        current_value = item.get(sub_field, "")

                    if sub_type == "text":
                        new_value = st.text_input(
                            sub_label,
                            value=current_value,
                            key=widget_key,
                        )
                    elif sub_type == "currency":
                        try:
                            current_float = float(current_value) if current_value else 0.0
                        except (TypeError, ValueError):
                            current_float = 0.0
                        new_value = st.number_input(
                            f"{sub_label} (EUR)",
                            value=current_float,
                            key=widget_key,
                            format="%.2f",
                        )
                    elif sub_type == "bool":
                        new_value = st.checkbox(
                            sub_label,
                            value=bool(current_value),
                            key=widget_key,
                        )
                    else:
                        new_value = st.text_input(
                            sub_label,
                            value=str(current_value),
                            key=widget_key,
                        )

                    state.update_list_item(field_name, idx, sub_field, new_value)

            with cols[1]:
                if len(items) > min_items:
                    if st.button("X", key=f"remove_{field_name}_{idx}"):
                        state.remove_list_item(field_name, idx)
                        st.rerun()

            st.divider()

    # Add new item button
    if st.button(f"+ Add {label.rstrip('s')}", key=f"add_{field_name}"):
        new_item = {f["name"]: f.get("default", "") for f in item_fields}
        state.add_list_item(field_name, new_item)
        st.rerun()


def render_simple_list(
    field_name: str,
    label: str,
    min_items: int = 0,
    help_text: Optional[str] = None,
) -> None:
    """
    Render a simple list input (list of strings).
    Uses st.container to minimize page jumps on add/remove.
    """
    st.subheader(label)
    if help_text:
        st.caption(help_text)

    items = state.get_list_items(field_name)

    # Check for pending add/remove actions to process after rendering
    action_key = f"_action_{field_name}"
    if action_key in st.session_state:
        action = st.session_state[action_key]
        if action["type"] == "remove":
            state.remove_list_item(field_name, action["index"])
        del st.session_state[action_key]
        # Items list has changed, get fresh copy
        items = state.get_list_items(field_name)

    # Use a container with unique ID to prevent scroll jumps
    list_container = st.container()

    with list_container:
        for idx, item in enumerate(items):
            cols = st.columns([0.85, 0.15])

            with cols[0]:
                widget_key = state.get_stable_key(field_name, idx, "value")
                # After JSON import, prioritize form_data over stale widget state
                # Otherwise check session state first for the widget value
                if state.was_data_just_imported():
                    current_value = item.get("value", "")
                elif widget_key in st.session_state:
                    current_value = st.session_state[widget_key]
                else:
                    current_value = item.get("value", "")

                new_value = st.text_input(
                    f"Item {idx + 1}",
                    value=current_value,
                    key=widget_key,
                    label_visibility="collapsed",
                    placeholder="Ingrese documento...",
                )
                state.update_list_item(field_name, idx, "value", new_value)

            with cols[1]:
                if len(items) > min_items:
                    # Use a unique key that includes item count to avoid stale key conflicts
                    remove_key = f"rm_{field_name}_{idx}_{len(items)}_{item.get('_id', idx)}"
                    if st.button("✕", key=remove_key, help="Eliminar"):
                        # Schedule removal for next rerun
                        st.session_state[action_key] = {"type": "remove", "index": idx}
                        st.rerun()

    # Add button - use unique key based on item count
    add_key = f"add_{field_name}_{len(items)}"
    if st.button(f"+ Añadir documento", key=add_key):
        state.add_list_item(field_name, {"value": ""})
        st.rerun()


def render_validation_errors(errors: list) -> None:
    """Render validation errors."""
    if errors:
        with st.expander("Validation Errors", expanded=True):
            for error in errors:
                st.error(error)


def render_success_message(output_path: str, trace_id: Optional[str] = None) -> None:
    """Render success message with download link."""
    st.success("Document generated successfully!")

    if output_path:
        st.info(f"Output: {output_path}")

        # Read file for download
        try:
            with open(output_path, "rb") as f:
                data = f.read()

            st.download_button(
                label="Download Document",
                data=data,
                file_name=output_path.split("/")[-1],
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            )
        except Exception as e:
            st.warning(f"Could not prepare download: {e}")

    if trace_id:
        st.caption(f"Trace ID: {trace_id}")
