# ui/streamlit_app/components.py
"""
Reusable UI components for Streamlit.
"""
import streamlit as st
from datetime import date
from typing import Any, Callable, Optional
from . import state_store as state


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
    default_value = state.get_field_value(field_name, "")

    label_display = f"{label} *" if required else label

    if multiline:
        value = st.text_area(
            label_display,
            value=default_value,
            key=widget_key,
            help=help_text,
            max_chars=max_length,
            on_change=state.create_sync_callback(field_name, widget_key),
        )
    else:
        value = st.text_input(
            label_display,
            value=default_value,
            key=widget_key,
            help=help_text,
            max_chars=max_length,
            on_change=state.create_sync_callback(field_name, widget_key),
        )

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
        on_change=state.create_sync_callback(field_name, widget_key),
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
        on_change=state.create_sync_callback(field_name, widget_key),
    )

    state.set_field_value(field_name, value)
    return value


def render_enum_input(
    field_name: str,
    label: str,
    options: list,
    required: bool = False,
    help_text: Optional[str] = None,
) -> Optional[str]:
    """Render an enum/select input field with stable state."""
    widget_key = state.get_stable_key(field_name)
    default_value = state.get_field_value(field_name)

    # Process options
    if options and isinstance(options[0], dict):
        option_labels = [opt.get("label", opt.get("value", "")) for opt in options]
        option_values = [opt.get("value", opt.get("label", "")) for opt in options]
    else:
        option_labels = [str(opt) for opt in options]
        option_values = list(options)

    # Find default index
    try:
        default_index = option_values.index(default_value) if default_value in option_values else 0
    except ValueError:
        default_index = 0

    label_display = f"{label} *" if required else label

    selected_label = st.selectbox(
        label_display,
        options=option_labels,
        index=default_index,
        key=widget_key,
        help=help_text,
        on_change=state.create_sync_callback(field_name, widget_key),
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
    default_value = state.get_field_value(field_name, False)

    value = st.checkbox(
        label,
        value=bool(default_value),
        key=widget_key,
        help=help_text,
        on_change=state.create_sync_callback(field_name, widget_key),
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
    """
    st.subheader(label)
    if help_text:
        st.caption(help_text)

    items = state.get_list_items(field_name)

    for idx, item in enumerate(items):
        cols = st.columns([0.9, 0.1])

        with cols[0]:
            widget_key = state.get_stable_key(field_name, idx, "value")
            current_value = item.get("value", "")

            new_value = st.text_input(
                f"Item {idx + 1}",
                value=current_value,
                key=widget_key,
                label_visibility="collapsed",
            )
            state.update_list_item(field_name, idx, "value", new_value)

        with cols[1]:
            if len(items) > min_items:
                if st.button("X", key=f"remove_{field_name}_{idx}"):
                    state.remove_list_item(field_name, idx)
                    st.rerun()

    if st.button(f"+ Add item", key=f"add_{field_name}"):
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
