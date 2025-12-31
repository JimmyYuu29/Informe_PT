# ui/streamlit_app/form_renderer.py
"""
Form Renderer - Dynamically render forms from plugin field definitions.
"""
import streamlit as st
from typing import Any, Optional
import sys
from pathlib import Path

# Add modules to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from modules.plugin_loader import PluginPack
from ui.streamlit_app import state_store as state
from ui.streamlit_app import components


def render_field(field_name: str, field_def: dict, context: dict) -> Any:
    """
    Render a single field based on its definition.

    Args:
        field_name: The field name/key.
        field_def: The field definition from fields.yaml.
        context: Current form context for conditional visibility.

    Returns:
        The field value.
    """
    # Check condition
    condition = field_def.get("condition")
    if condition:
        if not evaluate_simple_condition(condition, context):
            return None

    field_type = field_def.get("type", "text")
    label = field_def.get("label", field_name)
    required = field_def.get("required", False)
    description = field_def.get("description")
    multiline = field_def.get("multiline", False)
    validation = field_def.get("validation", {})

    if field_type == "text":
        return components.render_text_input(
            field_name=field_name,
            label=label,
            required=required,
            multiline=multiline,
            help_text=description,
            max_length=validation.get("max_length"),
        )

    elif field_type == "date":
        return components.render_date_input(
            field_name=field_name,
            label=label,
            required=required,
            help_text=description,
        )

    elif field_type == "currency":
        return components.render_number_input(
            field_name=field_name,
            label=label,
            required=required,
            is_currency=True,
            help_text=description,
        )

    elif field_type in ("int", "decimal", "percentage"):
        return components.render_number_input(
            field_name=field_name,
            label=label,
            required=required,
            is_currency=False,
            help_text=description,
        )

    elif field_type == "enum":
        options = field_def.get("values", [])
        return components.render_enum_input(
            field_name=field_name,
            label=label,
            options=options,
            required=required,
            help_text=description,
        )

    elif field_type == "bool":
        return components.render_checkbox(
            field_name=field_name,
            label=label,
            help_text=description,
        )

    elif field_type == "list":
        item_type = field_def.get("item_type")
        item_schema = field_def.get("item_schema", {})
        min_items = field_def.get("min_items", 0)

        if item_type == "text":
            # Simple string list
            components.render_simple_list(
                field_name=field_name,
                label=label,
                min_items=min_items,
                help_text=description,
            )
        else:
            # Complex object list
            item_fields = []
            for sub_name, sub_def in item_schema.items():
                item_fields.append({
                    "name": sub_name,
                    "label": sub_def.get("label", sub_name),
                    "type": sub_def.get("type", "text"),
                    "required": sub_def.get("required", False),
                    "default": sub_def.get("default", ""),
                })

            components.render_dynamic_list(
                field_name=field_name,
                label=label,
                item_fields=item_fields,
                min_items=min_items,
                help_text=description,
            )

        return state.get_list_items(field_name)

    else:
        # Fallback to text input
        return components.render_text_input(
            field_name=field_name,
            label=label,
            required=required,
            help_text=description,
        )


def evaluate_simple_condition(condition_str: str, context: dict) -> bool:
    """Evaluate a simple condition string."""
    try:
        if "==" in condition_str:
            parts = condition_str.split("==")
            field = parts[0].strip()
            expected = parts[1].strip()

            actual = context.get(field)

            # Try numeric comparison
            try:
                expected_val = int(expected)
                return actual == expected_val
            except ValueError:
                return str(actual) == expected
    except Exception:
        pass

    return True  # Default to visible


def render_section(
    section: dict,
    fields_def: dict,
    context: dict
) -> None:
    """
    Render a UI section with its fields.

    Args:
        section: Section definition from config.yaml.
        fields_def: All field definitions.
        context: Current form context.
    """
    section_id = section.get("id", "")
    section_label = section.get("label", section_id)
    section_condition = section.get("condition")
    field_names = section.get("fields", [])

    # Check section condition
    if section_condition:
        if not evaluate_simple_condition(section_condition, context):
            return

    with st.expander(section_label, expanded=True):
        for field_name in field_names:
            field_def = fields_def.get(field_name)
            if field_def:
                render_field(field_name, field_def, context)


def render_form(plugin: PluginPack) -> dict:
    """
    Render the complete form for a plugin.

    Args:
        plugin: The loaded plugin pack.

    Returns:
        Dictionary of form data.
    """
    fields_def = plugin.get_field_definitions()
    sections = plugin.get_ui_sections()

    # Get current context for conditional rendering
    context = state.get_all_form_data()

    if sections:
        # Render sections from config
        for section in sections:
            render_section(section, fields_def, context)
    else:
        # Render all fields in a single section
        st.subheader("Input Data")
        for field_name, field_def in fields_def.items():
            render_field(field_name, field_def, context)

    return state.get_all_form_data()


def render_risk_table(context: dict, fields_def: dict) -> None:
    """
    Render the risk assessment table input.

    Special handling for the 12-row risk table with structured input.
    """
    risk_labels = [
        "Restructuraciones empresariales",
        "Valoración de transmisiones intragrupo de activos intangibles",
        "Pagos por cánones derivados de la cesión de intangibles",
        "Pagos por servicios intragrupo",
        "Existencia de pérdidas reiteradas",
        "Operaciones financieras entre partes vinculadas",
        "Estructuras funcionales de bajo riesgo",
        "Falta de declaración de ingresos intragrupo",
        "Erosión de bases imponibles",
        "Revisión de las formas societarias",
        "Operaciones con establecimientos permanentes",
        "Peso de las operaciones vinculadas relevante",
    ]

    impacto_options = ["si", "no", "posible"]
    afectacion_options = ["bajo", "medio", "alto"]

    st.subheader("Evaluación de Riesgos")

    for i, label in enumerate(risk_labels, 1):
        with st.container():
            st.markdown(f"**{i}. {label}**")

            cols = st.columns(4)

            with cols[0]:
                field_name = f"impacto_{i}"
                components.render_enum_input(
                    field_name=field_name,
                    label="Impacto",
                    options=impacto_options,
                    required=True,
                )

            with cols[1]:
                field_name = f"afectacion_pre_{i}"
                components.render_enum_input(
                    field_name=field_name,
                    label="Afectación Prelim.",
                    options=afectacion_options,
                    required=True,
                )

            with cols[2]:
                field_name = f"texto_mitigacion_{i}"
                components.render_text_input(
                    field_name=field_name,
                    label="Mitigadores",
                    required=False,
                )

            with cols[3]:
                field_name = f"afectacion_final_{i}"
                components.render_enum_input(
                    field_name=field_name,
                    label="Afectación Final",
                    options=afectacion_options,
                    required=True,
                )

            st.divider()


def render_compliance_table(
    prefix: str,
    count: int,
    labels: list[str],
    title: str,
    context: dict
) -> None:
    """
    Render a compliance table input (Local File or Master File).
    """
    st.subheader(title)

    cumplido_options = ["si", "parcial", "no"]

    for i, label in enumerate(labels[:count], 1):
        with st.container():
            cols = st.columns([0.6, 0.2, 0.2])

            with cols[0]:
                st.markdown(f"**{i}. {label}**")

            with cols[1]:
                field_name = f"cumplido_{prefix}_{i}"
                components.render_enum_input(
                    field_name=field_name,
                    label="Cumplimiento",
                    options=cumplido_options,
                    required=True,
                )

            with cols[2]:
                # Comment required if cumplido is 'no' or 'parcial'
                cumplido_value = state.get_field_value(f"cumplido_{prefix}_{i}", "si")
                comment_required = cumplido_value in ("no", "parcial")

                field_name = f"texto_cumplido_{prefix}_{i}"
                components.render_text_input(
                    field_name=field_name,
                    label="Comentario",
                    required=comment_required,
                )
