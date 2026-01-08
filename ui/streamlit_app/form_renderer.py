# ui/streamlit_app/form_renderer.py
"""
Form Renderer - Dynamically render forms from plugin field definitions.
"""
import streamlit as st
from typing import Any, Optional
import sys
from pathlib import Path
from decimal import Decimal, ROUND_HALF_UP

# Add modules to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from modules.plugin_loader import PluginPack
from modules.comentarios_valorativos import get_comentarios_for_ui
from ui.streamlit_app import state_store as state
from ui.streamlit_app import components


# Global variable to cache the current plugin for use in render functions
_current_plugin: Optional[PluginPack] = None


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

    # Always get fresh context to handle dynamic changes from previous sections
    # This ensures conditions are evaluated with the latest field values
    fresh_context = state.get_all_form_data()

    # Check section condition
    if section_condition:
        if not evaluate_simple_condition(section_condition, fresh_context):
            return

    with st.expander(section_label, expanded=True):
        # Use specialized renderers for specific sections
        # Pass fresh_context to ensure field conditions work correctly
        if section_id == "sec_financials":
            render_financial_data_table(fresh_context, fields_def)
        elif section_id == "sec_operations":
            render_operaciones_intragrupo_table(fresh_context, fields_def)
            st.divider()
            render_operaciones_vinculadas_detail_table(fresh_context, fields_def)
        elif section_id == "sec_services":
            render_metodo_elegido_table(fresh_context, fields_def)
        elif section_id == "sec_compliance_local":
            render_cumplimiento_resumen_table(fresh_context, fields_def)
        elif section_id == "sec_compliance_master":
            render_cumplimiento_resumen_master_table(fresh_context, fields_def)
        elif section_id == "sec_risks" or "risk_elements" in field_names:
            render_risk_table(fresh_context, fields_def)
        elif section_id == "sec_local_detail" or "local_file_compliance" in field_names:
            render_local_file_compliance_detail(fresh_context, fields_def)
        elif section_id == "sec_master_detail" or "master_file_compliance" in field_names:
            render_master_file_compliance_detail(fresh_context, fields_def)
        elif section_id == "sec_anexo3":
            # Render texto_anexo3 field first
            field_def = fields_def.get("texto_anexo3")
            if field_def:
                render_field("texto_anexo3", field_def, fresh_context)
            # Then render comentarios valorativos section
            render_comentarios_valorativos_section(fresh_context, fields_def)
        else:
            # Default rendering - use fresh_context for field conditions
            for field_name in field_names:
                field_def = fields_def.get(field_name)
                if field_def:
                    render_field(field_name, field_def, fresh_context)


def render_form(plugin: PluginPack) -> dict:
    """
    Render the complete form for a plugin.

    Args:
        plugin: The loaded plugin pack.

    Returns:
        Dictionary of form data.
    """
    global _current_plugin
    _current_plugin = plugin

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


def calculate_variation(val_1: Any, val_0: Any) -> str:
    """Calculate year-over-year variation percentage."""
    try:
        if val_1 is None or val_0 is None:
            return "N/A"
        v1 = Decimal(str(val_1)) if val_1 else Decimal(0)
        v0 = Decimal(str(val_0)) if val_0 else Decimal(0)
        if v0 == 0:
            return "N/A"
        variation = ((v1 - v0) / abs(v0)) * 100
        variation = variation.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        return f"{variation:+.2f}".replace(".", ",")
    except Exception:
        return "N/A"


def render_financial_data_table(context: dict, fields_def: dict) -> None:
    """
    Render the financial data table with two columns for ejercicio actual and anterior,
    and automatic variation calculation.
    """
    st.subheader("Datos Financieros")

    # Define the financial rows
    financial_rows = [
        {
            "label": "Cifra de negocios",
            "field_1": "cifra_1",
            "field_0": "cifra_0",
            "is_currency": True,
        },
        {
            "label": "EBIT",
            "field_1": "ebit_1",
            "field_0": "ebit_0",
            "is_currency": True,
        },
        {
            "label": "Resultado Financiero",
            "field_1": "resultado_fin_1",
            "field_0": "resultado_fin_0",
            "is_currency": True,
        },
        {
            "label": "EBT",
            "field_1": "ebt_1",
            "field_0": "ebt_0",
            "is_currency": True,
        },
        {
            "label": "Resultado Neto",
            "field_1": "resultado_net_1",
            "field_0": "resultado_net_0",
            "is_currency": True,
        },
    ]

    # Get fiscal year for column headers
    anyo_actual = state.get_field_value("anyo_ejercicio", "Actual")
    anyo_anterior = state.get_field_value("anyo_ejercicio_ant", "Anterior")

    # Calculate years from fecha_fin_fiscal if available
    fecha = state.get_field_value("fecha_fin_fiscal")
    if fecha:
        try:
            from datetime import date
            if isinstance(fecha, date):
                anyo_actual = fecha.year
                anyo_anterior = fecha.year - 1
            elif isinstance(fecha, str):
                anyo_actual = int(fecha.split("-")[0])
                anyo_anterior = anyo_actual - 1
        except Exception:
            pass

    # Table header
    cols_header = st.columns([0.25, 0.20, 0.25, 0.30])
    with cols_header[0]:
        st.markdown("**Partidas Contables**")
    with cols_header[1]:
        st.markdown(f"**Variación (%)**")
    with cols_header[2]:
        st.markdown(f"**Ejercicio {anyo_actual} (EUR)**")
    with cols_header[3]:
        st.markdown(f"**Ejercicio {anyo_anterior} (EUR)**")

    st.divider()

    # Render each row
    for row in financial_rows:
        cols = st.columns([0.25, 0.20, 0.25, 0.30])

        with cols[0]:
            st.markdown(f"**{row['label']}**")

        # Input for ejercicio actual (current year)
        with cols[2]:
            val_1 = components.render_number_input(
                field_name=row["field_1"],
                label="",
                required=True,
                is_currency=row["is_currency"],
            )

        # Input for ejercicio anterior (prior year)
        with cols[3]:
            val_0 = components.render_number_input(
                field_name=row["field_0"],
                label="",
                required=True,
                is_currency=row["is_currency"],
            )

        # Calculate and display variation
        with cols[1]:
            variation = calculate_variation(val_1, val_0)
            st.markdown(f"**{variation} %**")

    st.divider()

    # Derived rows (calculated automatically)
    st.caption("Los siguientes valores se calculan automáticamente:")

    # Calculate derived values
    cifra_1 = state.get_field_value("cifra_1", 0)
    cifra_0 = state.get_field_value("cifra_0", 0)
    ebit_1 = state.get_field_value("ebit_1", 0)
    ebit_0 = state.get_field_value("ebit_0", 0)

    try:
        cost_1 = float(cifra_1 or 0) - float(ebit_1 or 0)
        cost_0 = float(cifra_0 or 0) - float(ebit_0 or 0)
        om_1 = (float(ebit_1 or 0) / float(cifra_1 or 1)) * 100 if cifra_1 else 0
        om_0 = (float(ebit_0 or 0) / float(cifra_0 or 1)) * 100 if cifra_0 else 0
        ncp_1 = (float(ebit_1 or 0) / float(cost_1 or 1)) * 100 if cost_1 else 0
        ncp_0 = (float(ebit_0 or 0) / float(cost_0 or 1)) * 100 if cost_0 else 0
    except Exception:
        cost_1 = cost_0 = om_1 = om_0 = ncp_1 = ncp_0 = 0

    derived_rows = [
        {"label": "Total costes operativos", "val_1": cost_1, "val_0": cost_0, "is_currency": True},
        {"label": "Operating Margin (OM)", "val_1": om_1, "val_0": om_0, "is_percent": True},
        {"label": "Net Cost Plus (NCP)", "val_1": ncp_1, "val_0": ncp_0, "is_percent": True},
    ]

    for row in derived_rows:
        cols = st.columns([0.25, 0.20, 0.25, 0.30])

        with cols[0]:
            st.markdown(f"*{row['label']}*")

        with cols[1]:
            variation = calculate_variation(row["val_1"], row["val_0"])
            st.markdown(f"*{variation} %*")

        with cols[2]:
            if row.get("is_currency"):
                formatted = f"{row['val_1']:,.2f} €".replace(",", "X").replace(".", ",").replace("X", ".")
            else:
                formatted = f"{row['val_1']:.2f} %".replace(".", ",")
            st.markdown(f"*{formatted}*")

        with cols[3]:
            if row.get("is_currency"):
                formatted = f"{row['val_0']:,.2f} €".replace(",", "X").replace(".", ",").replace("X", ".")
            else:
                formatted = f"{row['val_0']:.2f} %".replace(".", ",")
            st.markdown(f"*{formatted}*")


def render_operaciones_intragrupo_table(context: dict, fields_def: dict) -> None:
    """
    Render the operaciones intragrupo (related party operations) table
    matching the template layout.
    """
    st.subheader("Operaciones Intragrupo")

    items = state.get_list_items("servicios_vinculados")

    # Table header
    cols_header = st.columns([0.1, 0.9])
    with cols_header[0]:
        st.markdown("**#**")
    with cols_header[1]:
        st.markdown("**Operaciones intragrupo**")

    st.divider()

    # Render existing items
    for idx, item in enumerate(items):
        cols = st.columns([0.1, 0.9])
        with cols[0]:
            st.markdown(f"**{idx + 1}**")
        with cols[1]:
            widget_key = state.get_stable_key("servicios_vinculados", idx, "servicio_vinculado")
            # After JSON import, prioritize list_items over stale widget state
            if state.was_data_just_imported():
                current_value = item.get("servicio_vinculado", "")
            elif widget_key in st.session_state:
                current_value = st.session_state[widget_key]
            else:
                current_value = item.get("servicio_vinculado", "")
            new_value = st.text_input(
                "Tipo de operación",
                value=current_value,
                key=widget_key,
                label_visibility="collapsed",
            )
            state.update_list_item("servicios_vinculados", idx, "servicio_vinculado", new_value)

            # Remove button
            if len(items) > 1:
                if st.button("Eliminar", key=f"remove_servicio_{idx}"):
                    state.remove_list_item("servicios_vinculados", idx)
                    st.rerun()

    # Add button
    if st.button("+ Añadir operación", key="add_servicio"):
        state.add_list_item("servicios_vinculados", {
            "servicio_vinculado": "",
            "entidades_vinculadas": []
        })
        st.rerun()


def render_operaciones_vinculadas_detail_table(context: dict, fields_def: dict) -> None:
    """
    Render the detailed operaciones vinculadas table with entity breakdown,
    matching the template layout. Includes gasto (expense) input for calculating totals.
    """
    st.subheader("Detalle de Operaciones Vinculadas")

    # Get fiscal year for column header
    anyo_actual = state.get_field_value("anyo_ejercicio", "Actual")
    fecha = state.get_field_value("fecha_fin_fiscal")
    if fecha:
        try:
            from datetime import date
            if isinstance(fecha, date):
                anyo_actual = fecha.year
            elif isinstance(fecha, str):
                anyo_actual = int(fecha.split("-")[0])
        except Exception:
            pass

    servicios = state.get_list_items("servicios_vinculados")

    # Table header - now with 4 columns including gasto
    cols_header = st.columns([0.25, 0.25, 0.25, 0.25])
    with cols_header[0]:
        st.markdown("**Tipo de operación vinculada**")
    with cols_header[1]:
        st.markdown("**Entidad vinculada**")
    with cols_header[2]:
        st.markdown(f"**Ingreso FY {anyo_actual} (EUR)**")
    with cols_header[3]:
        st.markdown(f"**Gasto FY {anyo_actual} (EUR)**")

    st.divider()

    total_ingreso = 0
    total_gasto = 0

    for serv_idx, servicio in enumerate(servicios):
        servicio_name = servicio.get("servicio_vinculado", f"Servicio {serv_idx + 1}")
        entidades = servicio.get("entidades_vinculadas", [])

        if not entidades:
            entidades = [{"entidad_vinculada": "", "ingreso_entidad": 0, "gasto_entidad": 0}]
            servicio["entidades_vinculadas"] = entidades

        for ent_idx, entidad in enumerate(entidades):
            cols = st.columns([0.25, 0.25, 0.25, 0.25])

            with cols[0]:
                if ent_idx == 0:
                    st.markdown(f"**{servicio_name}**")
                else:
                    st.markdown("")

            with cols[1]:
                widget_key = f"entidad_{serv_idx}_{ent_idx}_nombre"
                # After JSON import, prioritize list_items over stale widget state
                if state.was_data_just_imported():
                    current_value = entidad.get("entidad_vinculada", "")
                elif widget_key in st.session_state:
                    current_value = st.session_state[widget_key]
                else:
                    current_value = entidad.get("entidad_vinculada", "")
                new_value = st.text_input(
                    "Entidad",
                    value=current_value,
                    key=widget_key,
                    label_visibility="collapsed",
                )
                if "entidades_vinculadas" not in servicio:
                    servicio["entidades_vinculadas"] = []
                while len(servicio["entidades_vinculadas"]) <= ent_idx:
                    servicio["entidades_vinculadas"].append({})
                servicio["entidades_vinculadas"][ent_idx]["entidad_vinculada"] = new_value

            with cols[2]:
                widget_key = f"entidad_{serv_idx}_{ent_idx}_ingreso"
                # After JSON import, prioritize list_items over stale widget state
                if state.was_data_just_imported():
                    current_ingreso = entidad.get("ingreso_entidad", 0)
                elif widget_key in st.session_state:
                    current_ingreso = st.session_state[widget_key]
                else:
                    current_ingreso = entidad.get("ingreso_entidad", 0)
                try:
                    current_float = float(current_ingreso) if current_ingreso else 0.0
                except (TypeError, ValueError):
                    current_float = 0.0
                new_ingreso = st.number_input(
                    "Ingreso",
                    value=current_float,
                    key=widget_key,
                    format="%.2f",
                    label_visibility="collapsed",
                )
                servicio["entidades_vinculadas"][ent_idx]["ingreso_entidad"] = new_ingreso
                total_ingreso += new_ingreso

            with cols[3]:
                widget_key = f"entidad_{serv_idx}_{ent_idx}_gasto"
                # After JSON import, prioritize list_items over stale widget state
                if state.was_data_just_imported():
                    current_gasto = entidad.get("gasto_entidad", 0)
                elif widget_key in st.session_state:
                    current_gasto = st.session_state[widget_key]
                else:
                    current_gasto = entidad.get("gasto_entidad", 0)
                try:
                    current_gasto_float = float(current_gasto) if current_gasto else 0.0
                except (TypeError, ValueError):
                    current_gasto_float = 0.0
                new_gasto = st.number_input(
                    "Gasto",
                    value=current_gasto_float,
                    key=widget_key,
                    format="%.2f",
                    label_visibility="collapsed",
                )
                servicio["entidades_vinculadas"][ent_idx]["gasto_entidad"] = new_gasto
                total_gasto += new_gasto

        # Add entity button for this service
        if st.button(f"+ Añadir entidad a '{servicio_name}'", key=f"add_entidad_{serv_idx}"):
            if "entidades_vinculadas" not in servicio:
                servicio["entidades_vinculadas"] = []
            servicio["entidades_vinculadas"].append({
                "entidad_vinculada": "",
                "ingreso_entidad": 0,
                "gasto_entidad": 0
            })
            st.rerun()

        st.divider()

    # Show totals
    cols_total = st.columns([0.50, 0.25, 0.25])
    with cols_total[0]:
        st.markdown("**Totales OOVV**")
    with cols_total[1]:
        formatted_ingreso = f"{total_ingreso:,.2f} €".replace(",", "X").replace(".", ",").replace("X", ".")
        st.markdown(f"**{formatted_ingreso}**")
    with cols_total[2]:
        formatted_gasto = f"{total_gasto:,.2f} €".replace(",", "X").replace(".", ",").replace("X", ".")
        st.markdown(f"**{formatted_gasto}**")

    # Calculate and display peso OOVV metrics
    st.divider()
    st.caption("Indicadores calculados automáticamente:")

    # Get cifra_1 and cost_1 for peso calculations
    cifra_1 = state.get_field_value("cifra_1", 0)
    ebit_1 = state.get_field_value("ebit_1", 0)

    try:
        cifra_1_float = float(cifra_1) if cifra_1 else 0.0
        ebit_1_float = float(ebit_1) if ebit_1 else 0.0
        cost_1 = cifra_1_float - ebit_1_float
    except (TypeError, ValueError):
        cifra_1_float = 0.0
        cost_1 = 0.0

    # Peso oovv sobre INCN = (total_ingreso / cifra_1) * 100
    if cifra_1_float != 0:
        peso_incn = (total_ingreso / Decimal(str(cifra_1_float))) * 100
        peso_incn_formatted = f"{float(peso_incn):.2f}".replace(".", ",")
    else:
        peso_incn_formatted = "N/A"

    # Peso oovv sobre total costes = (total_gasto / cost_1) * 100
    if cost_1 != 0:
        peso_costes = (total_gasto / Decimal(str(cost_1))) * 100
        peso_costes_formatted = f"{float(peso_costes):.2f}".replace(".", ",")
    else:
        peso_costes_formatted = "N/A"

    # Display peso rows
    cols_peso1 = st.columns([0.50, 0.50])
    with cols_peso1[0]:
        st.markdown("*Peso OOVV sobre INCN*")
    with cols_peso1[1]:
        st.markdown(f"*{peso_incn_formatted} %*")

    cols_peso2 = st.columns([0.50, 0.50])
    with cols_peso2[0]:
        st.markdown("*Peso OOVV sobre total costes*")
    with cols_peso2[1]:
        st.markdown(f"*{peso_costes_formatted} %*")

    # Valoración OOVV text field
    st.divider()
    components.render_text_input(
        field_name="valoracion_oovv",
        label="Valoración de Operaciones Vinculadas",
        required=False,
        multiline=True,
        help_text="Texto de valoración basado en los indicadores de peso OOVV",
    )


def render_metodo_elegido_table(context: dict, fields_def: dict) -> None:
    """
    Render the método elegido (benchmark) table matching the template layout.
    Now linked to servicios_vinculados - each servicio can be marked for analysis.
    """
    st.subheader("Análisis de Servicios OOVV - Método Elegido")

    servicios_vinculados = state.get_list_items("servicios_vinculados")

    if not servicios_vinculados:
        st.info("Primero añada operaciones vinculadas en la sección anterior.")
        return

    st.markdown("Seleccione los servicios vinculados que desea analizar:")
    st.divider()

    # Track which servicios have analysis enabled
    for serv_idx, servicio in enumerate(servicios_vinculados):
        servicio_name = servicio.get("servicio_vinculado", f"Servicio {serv_idx + 1}")

        if not servicio_name.strip():
            servicio_name = f"Servicio {serv_idx + 1}"

        # Initialize analisis data if not present
        if "analisis" not in servicio:
            servicio["analisis"] = {
                "enabled": False,
                "titulo_servicio_oovv": servicio_name,
                "texto_intro_servicio": "",
                "descripcion_tabla": "",
                "metodo": "",
                "min": 0,
                "lq": 0,
                "med": 0,
                "uq": 0,
                "max": 0,
                "texto_conclusion_servicio": "",
            }

        analisis = servicio["analisis"]

        # Helper function to get value with import priority
        def get_imported_value(widget_key: str, data_dict: dict, field: str, default):
            if state.was_data_just_imported():
                return data_dict.get(field, default)
            elif widget_key in st.session_state:
                return st.session_state[widget_key]
            else:
                return data_dict.get(field, default)

        # Checkbox to enable analysis for this servicio
        widget_key = f"analizar_servicio_{serv_idx}"
        enabled_val = get_imported_value(widget_key, analisis, "enabled", False)
        analizar = st.checkbox(
            f"Analizar: **{servicio_name}**",
            value=bool(enabled_val),
            key=widget_key,
        )
        analisis["enabled"] = analizar

        # If analysis is enabled, show the analysis fields
        if analizar:
            with st.container():
                st.markdown(f"##### Análisis de {servicio_name}")

                # Título del servicio
                widget_key = f"servicio_oovv_{serv_idx}_titulo"
                val = get_imported_value(widget_key, analisis, "titulo_servicio_oovv", servicio_name)
                analisis["titulo_servicio_oovv"] = st.text_input(
                    "Título del servicio",
                    value=val,
                    key=widget_key,
                )

                # Texto introductorio
                widget_key = f"servicio_oovv_{serv_idx}_intro"
                val = get_imported_value(widget_key, analisis, "texto_intro_servicio", "")
                analisis["texto_intro_servicio"] = st.text_area(
                    "Texto introductorio",
                    value=val,
                    key=widget_key,
                    height=100,
                )

                # Descripción de la tabla
                widget_key = f"servicio_oovv_{serv_idx}_desc_tabla"
                val = get_imported_value(widget_key, analisis, "descripcion_tabla", "")
                analisis["descripcion_tabla"] = st.text_input(
                    "Descripción de la tabla",
                    value=val,
                    key=widget_key,
                )

                # Benchmark table
                st.markdown("**Datos del Benchmark:**")
                cols_header = st.columns([0.25, 0.15, 0.15, 0.15, 0.15, 0.15])
                headers = ["Método Elegido", "Min %", "LQ %", "Med %", "UQ %", "Max %"]
                for col, header in zip(cols_header, headers):
                    with col:
                        st.caption(header)

                cols = st.columns([0.25, 0.15, 0.15, 0.15, 0.15, 0.15])

                # Método
                with cols[0]:
                    widget_key = f"servicio_oovv_{serv_idx}_metodo"
                    val = get_imported_value(widget_key, analisis, "metodo", "")
                    analisis["metodo"] = st.text_input(
                        "Método",
                        value=val,
                        key=widget_key,
                        label_visibility="collapsed",
                    )

                # Min
                with cols[1]:
                    widget_key = f"servicio_oovv_{serv_idx}_min"
                    val = get_imported_value(widget_key, analisis, "min", 0)
                    try:
                        current_val = float(val) if val else 0.0
                    except (TypeError, ValueError):
                        current_val = 0.0
                    analisis["min"] = st.number_input(
                        "Min",
                        value=current_val,
                        key=widget_key,
                        format="%.2f",
                        label_visibility="collapsed",
                    )

                # LQ
                with cols[2]:
                    widget_key = f"servicio_oovv_{serv_idx}_lq"
                    val = get_imported_value(widget_key, analisis, "lq", 0)
                    try:
                        current_val = float(val) if val else 0.0
                    except (TypeError, ValueError):
                        current_val = 0.0
                    analisis["lq"] = st.number_input(
                        "LQ",
                        value=current_val,
                        key=widget_key,
                        format="%.2f",
                        label_visibility="collapsed",
                    )

                # Med
                with cols[3]:
                    widget_key = f"servicio_oovv_{serv_idx}_med"
                    val = get_imported_value(widget_key, analisis, "med", 0)
                    try:
                        current_val = float(val) if val else 0.0
                    except (TypeError, ValueError):
                        current_val = 0.0
                    analisis["med"] = st.number_input(
                        "Med",
                        value=current_val,
                        key=widget_key,
                        format="%.2f",
                        label_visibility="collapsed",
                    )

                # UQ
                with cols[4]:
                    widget_key = f"servicio_oovv_{serv_idx}_uq"
                    val = get_imported_value(widget_key, analisis, "uq", 0)
                    try:
                        current_val = float(val) if val else 0.0
                    except (TypeError, ValueError):
                        current_val = 0.0
                    analisis["uq"] = st.number_input(
                        "UQ",
                        value=current_val,
                        key=widget_key,
                        format="%.2f",
                        label_visibility="collapsed",
                    )

                # Max
                with cols[5]:
                    widget_key = f"servicio_oovv_{serv_idx}_max"
                    val = get_imported_value(widget_key, analisis, "max", 0)
                    try:
                        current_val = float(val) if val else 0.0
                    except (TypeError, ValueError):
                        current_val = 0.0
                    analisis["max"] = st.number_input(
                        "Max",
                        value=current_val,
                        key=widget_key,
                        format="%.2f",
                        label_visibility="collapsed",
                    )

                # Texto conclusión
                widget_key = f"servicio_oovv_{serv_idx}_conclusion"
                val = get_imported_value(widget_key, analisis, "texto_conclusion_servicio", "")
                analisis["texto_conclusion_servicio"] = st.text_area(
                    "Texto de conclusión",
                    value=val,
                    key=widget_key,
                    height=100,
                )

        st.divider()


def render_cumplimiento_resumen_table(context: dict, fields_def: dict) -> None:
    """
    Render the cumplimiento resumen (compliance summary) table
    matching the template layout.
    """
    st.subheader("Cumplimiento Local File (Resumen)")

    sections = [
        {"num": 1, "label": "Información del contribuyente"},
        {"num": 2, "label": "Información de las operaciones vinculadas"},
        {"num": 3, "label": "Información económico-financiera del contribuyente"},
    ]

    cumplimiento_options = ["si", "no"]

    # Table header
    cols_header = st.columns([0.1, 0.6, 0.3])
    with cols_header[0]:
        st.markdown("**#**")
    with cols_header[1]:
        st.markdown("**Secciones (Artículo 16 del Reglamento)**")
    with cols_header[2]:
        st.markdown("**Cumplimiento**")

    st.divider()

    for section in sections:
        cols = st.columns([0.1, 0.6, 0.3])

        with cols[0]:
            st.markdown(f"**{section['num']}**")

        with cols[1]:
            st.markdown(section["label"])

        with cols[2]:
            field_name = f"cumplimiento_resumen_local_{section['num']}"
            components.render_enum_input(
                field_name=field_name,
                label="",
                options=cumplimiento_options,
                required=True,
            )


def render_cumplimiento_resumen_master_table(context: dict, fields_def: dict) -> None:
    """
    Render the Master File cumplimiento resumen (compliance summary) table
    matching the template layout.

    Table structure based on Artículo 15 del Reglamento:
    | # | Secciones (Artículo 15 del Reglamento) | Cumplimiento |
    """
    st.subheader("Cumplimiento Master File (Resumen)")

    sections = [
        {"num": 1, "label": "Información relativa a la estructura y actividades del Grupo"},
        {"num": 2, "label": "Información relativa a los activos intangibles del Grupo"},
        {"num": 3, "label": "Información relativa a la actividad financiera"},
        {"num": 4, "label": "Situación financiera y fiscal del Grupo"},
    ]

    cumplimiento_options = ["si", "no"]

    # Table header
    cols_header = st.columns([0.1, 0.6, 0.3])
    with cols_header[0]:
        st.markdown("**#**")
    with cols_header[1]:
        st.markdown("**Secciones (Artículo 15 del Reglamento)**")
    with cols_header[2]:
        st.markdown("**Cumplimiento**")

    st.divider()

    for section in sections:
        cols = st.columns([0.1, 0.6, 0.3])

        with cols[0]:
            st.markdown(f"**{section['num']}**")

        with cols[1]:
            st.markdown(section["label"])

        with cols[2]:
            field_name = f"cumplimiento_resumen_mast_{section['num']}"
            components.render_enum_input(
                field_name=field_name,
                label="",
                options=cumplimiento_options,
                required=True,
            )


def render_risk_table(context: dict, fields_def: dict) -> None:
    """
    Render the risk assessment table (Evaluación de Riesgos) matching template layout.

    Table structure:
    | # | Elemento de Riesgo | Impacto | Afectación Preliminar | Mitigadores | Afectación Final |
    """
    risk_labels = [
        "Restructuraciones empresariales",
        "Valoración de transmisiones intragrupo de activos intangibles",
        "Pagos por cánones derivados de la cesión de intangibles",
        "Pagos por servicios intragrupo",
        "Existencia de pérdidas reiteradas",
        "Operaciones financieras entre partes vinculadas",
        "Estructuras funcionales de bajo riesgo, tanto en el ámbito de la fabricación como de la distribución",
        "Falta de declaración de ingresos intragrupo por las prestaciones de servicios o de cesiones de activos intangibles no repercutidos",
        "Erosión de bases imponibles causada por el establecimiento de estructuras en el exterior en las que se remanses beneficios que deben tributar en España",
        "Revisión de las formas societarias utilizadas para el desempeño de la actividad económica con el objetivo de verificar si se está produciendo una minoración improcedente de la correcta tributación de la actividad desarrollada o una traslación de bases imponibles negativas hacia entidades jurídicas sometidas a menores tipos",
        "Operaciones con establecimientos permanentes",
        "Peso de las operaciones vinculadas relevante",
    ]

    impacto_options = ["si", "no", "posible"]
    afectacion_options = ["bajo", "medio", "alto"]

    st.subheader("Evaluación de Riesgos")

    # Table header
    cols_header = st.columns([0.05, 0.30, 0.13, 0.13, 0.26, 0.13])
    headers = ["#", "Elemento de riesgo", "Impacto", "Afect. Prelim.", "Mitigadores", "Afect. Final"]
    for col, header in zip(cols_header, headers):
        with col:
            st.markdown(f"**{header}**")

    st.divider()

    for i, label in enumerate(risk_labels, 1):
        cols = st.columns([0.05, 0.30, 0.13, 0.13, 0.26, 0.13])

        with cols[0]:
            st.markdown(f"**{i}**")

        with cols[1]:
            st.markdown(label)

        with cols[2]:
            field_name = f"impacto_{i}"
            components.render_enum_input(
                field_name=field_name,
                label="",
                options=impacto_options,
                required=True,
                default="no",  # Default impacto to "no"
            )

        with cols[3]:
            field_name = f"afectacion_pre_{i}"
            components.render_enum_input(
                field_name=field_name,
                label="",
                options=afectacion_options,
                required=True,
                default="bajo",  # Default afectacion to "bajo"
            )

        with cols[4]:
            field_name = f"texto_mitigacion_{i}"
            components.render_text_input(
                field_name=field_name,
                label="",
                required=False,
            )

        with cols[5]:
            field_name = f"afectacion_final_{i}"
            components.render_enum_input(
                field_name=field_name,
                label="",
                options=afectacion_options,
                required=True,
                default="bajo",  # Default afectacion_final to "bajo"
            )


def render_local_file_compliance_detail(context: dict, fields_def: dict) -> None:
    """
    Render the detailed Local File compliance table (ANEXO 2 - Table 08).

    Table structure:
    | # | Contenido | Cumplido | Comentario |
    """
    local_file_items = [
        "Estructura de dirección, organigrama y personas o entidades destinatarias de los informes sobre la evolución de las actividades del contribuyente, indicando los países o territorios en que dichas personas o entidades tienen su residencia fiscal.",
        "Descripción de las actividades del contribuyente, de su estrategia de negocio y, en su caso, de su participación en operaciones de reestructuración o de cesión o transmisión de activos intangibles en el período impositivo.",
        "Principales competidores",
        "Descripción detallada de la naturaleza, características e importe de las operaciones vinculadas.",
        "Nombre y apellidos o razón social o denominación completa, domicilio fiscal y número de identificación fiscal del contribuyente y de las personas o entidades vinculadas con las que se realice la operación.",
        "Análisis de comparabilidad, en los términos descritos en el artículo 17 de este Reglamento.",
        "Explicación relativa a la selección del método de valoración elegido, incluyendo una descripción de las razones que justificaron la elección del mismo, así como su forma de aplicación, los comparables obtenidos y la especificación del valor o intervalo de valores derivados del mismo.",
        "En su caso, criterios de reparto de gastos en concepto de servicios prestados conjuntamente en favor de varias personas o entidades vinculadas, así como los refiere el artículo 18 de este Reglamento.",
        "Copia de los acuerdos previos de valoración vigentes y cualquier otra decisión con alguna autoridad fiscal que estén relacionados con las operaciones vinculadas señaladas anteriormente.",
        "Cualquier otra información relevante de la que haya dispuesto el contribuyente para determinar la valoración de sus operaciones vinculadas.",
        "Estados financieros anuales del contribuyente.",
        "Conciliación entre los datos utilizados para aplicar los métodos de precios de transferencia y los estados financieros anuales, cuando corresponda y resulte relevante.",
        "Datos financieros de los comparables utilizados y fuente de la que proceden.",
        "Si, para determinar el valor de mercado, se utilizan otros métodos y técnicas de valoración generalmente aceptados distintos en los señalados en las letras a) a e) del artículo 18.4 de la Ley del Impuesto, como pudieran ser métodos de descuento de flujos de efectivo futuro estimados, se describirá detalladamente el método o técnica concreto elegido, así como las razones de su elección.",
    ]

    cumplido_options = ["si", "parcial", "no"]

    st.subheader("Cumplimiento Local File - Detalle")

    # Table header
    cols_header = st.columns([0.05, 0.50, 0.15, 0.30])
    headers = ["#", "Contenido", "Cumplido", "Comentario"]
    for col, header in zip(cols_header, headers):
        with col:
            st.markdown(f"**{header}**")

    st.divider()

    for i, item in enumerate(local_file_items, 1):
        cols = st.columns([0.05, 0.50, 0.15, 0.30])

        with cols[0]:
            st.markdown(f"**{i}**")

        with cols[1]:
            st.markdown(item)

        with cols[2]:
            field_name = f"cumplido_local_{i}"
            components.render_enum_input(
                field_name=field_name,
                label="",
                options=cumplido_options,
                required=True,
            )

        with cols[3]:
            # Comment required if cumplido is 'no' or 'parcial'
            cumplido_value = state.get_field_value(f"cumplido_local_{i}", "si")
            comment_required = cumplido_value in ("no", "parcial")

            field_name = f"texto_cumplido_local_{i}"
            components.render_text_input(
                field_name=field_name,
                label="",
                required=comment_required,
            )


def render_master_file_compliance_detail(context: dict, fields_def: dict) -> None:
    """
    Render the detailed Master File compliance table (ANEXO 2 - Table 09).

    Table structure:
    | # | Contenido | Cumplido | Comentario |
    """
    master_file_items = [
        "Descripción general de la estructura organizativa, jurídica y operativa del grupo, así como cualquier cambio relevante en la misma.",
        "Identificación de las distintas entidades que formen parte del grupo",
        "Actividades principales del grupo, así como descripción de los principales mercados geográficos en los que opera el grupo, fuentes principales de beneficios y cadena de suministro de aquellos bienes y servicios que representen, al menos, el 10 por ciento del importe neto de la cifra de negocios del grupo, correspondiente al período impositivo.",
        "Descripción general de las funciones ejercidas, riesgos asumidos y principales activos utilizados por las distintas entidades del grupo, incluyendo los cambios respecto del período impositivo anterior.",
        "Descripción de la política del grupo en materia de precios de transferencia que incluya el método o métodos de fijación de los precios adoptados por el grupo.",
        "Relación y breve descripción de los acuerdos de reparto de costes y contratos de prestación de servicios relevantes entre entidades del grupo.",
        "Descripción de las operaciones de reorganización y de adquisición o cesión de activos relevantes, realizadas durante el período impositivo.",
        "Descripción general de la estrategia global del grupo en relación al desarrollo, propiedad y explotación de los activos intangibles, incluyendo la localización de las principales instalaciones en las que se realicen actividades de investigación y desarrollo, así como la dirección de las mismas.",
        "Relación de los activos intangibles del grupo relevantes a efectos de precios de transferencia, indicando las entidades titulares de los mismos, así como descripción general de la política de precios de transferencia del grupo en relación con los mismos.",
        "Importe de las contraprestaciones correspondientes a las operaciones vinculadas del grupo, derivadas de la utilización de los activos intangibles, identificando las entidades del grupo afectadas y sus territorios de residencia fiscal.",
        "Relación de acuerdos entre las entidades del grupo relativos a intangibles, incluyendo los acuerdos de reparto de costes, los principales acuerdos de servicios de investigación y acuerdos de licencias.",
        "Descripción general de cualquier transferencia relevante sobre activos intangibles realizada en el período impositivo, incluyendo las entidades, países e importes.",
        "Descripción general de la forma de financiación del grupo, incluyendo los principales acuerdos de financiación suscritos con personas o entidades ajenas al grupo.",
        "Identificación de las entidades del grupo que realicen las principales funciones de financiación del grupo, así como el país de su constitución y el correspondiente a su sede de dirección efectiva.",
        "Descripción general de la política de precios de transferencia relativa a los acuerdos de financiación entre entidades del grupo.",
        "Estados financieros anuales consolidados del grupo, siempre que resulten obligatorios para el mismo o se elaboren de manera voluntaria.",
        "Relación y breve descripción de los acuerdos previos de valoración vigentes y cualquier otra decisión con alguna autoridad fiscal que afecte a la distribución de los beneficios del grupo entre países.",
    ]

    cumplido_options = ["si", "parcial", "no"]

    st.subheader("Cumplimiento Master File - Detalle")

    # Table header
    cols_header = st.columns([0.05, 0.50, 0.15, 0.30])
    headers = ["#", "Contenido", "Cumplido", "Comentario"]
    for col, header in zip(cols_header, headers):
        with col:
            st.markdown(f"**{header}**")

    st.divider()

    for i, item in enumerate(master_file_items, 1):
        cols = st.columns([0.05, 0.50, 0.15, 0.30])

        with cols[0]:
            st.markdown(f"**{i}**")

        with cols[1]:
            st.markdown(item)

        with cols[2]:
            field_name = f"cumplido_mast_{i}"
            components.render_enum_input(
                field_name=field_name,
                label="",
                options=cumplido_options,
                required=True,
            )

        with cols[3]:
            # Comment required if cumplido is 'no' or 'parcial'
            cumplido_value = state.get_field_value(f"cumplido_mast_{i}", "si")
            comment_required = cumplido_value in ("no", "parcial")

            field_name = f"texto_cumplido_mast_{i}"
            components.render_text_input(
                field_name=field_name,
                label="",
                required=comment_required,
            )


def render_comentarios_valorativos_section(context: dict, fields_def: dict) -> None:
    """
    Render the comentarios valorativos section with 17 conditional questions.

    Each question:
    - Displays the question text from YAML
    - Has a si/no selector (default: no)
    - Shows a preview of the first 3 lines when "si" is selected
    """
    global _current_plugin

    st.divider()
    st.subheader("Comentarios Valorativos")
    st.caption("Seleccione los comentarios que desea incluir en el documento.")

    # Get comentarios definitions from plugin
    if _current_plugin is None:
        st.warning("No se pudo cargar la configuración de comentarios valorativos.")
        return

    comentarios_defs = _current_plugin.get_comentarios_valorativos()
    comentarios_ui = get_comentarios_for_ui(comentarios_defs)

    si_no_options = ["no", "si"]

    for comentario in comentarios_ui:
        field_name = comentario["id"]
        index = comentario["index"]
        question = comentario["question"]
        text_preview = comentario["text_preview"]

        # Create a container for each comentario
        with st.container():
            # Row with question, selector, and conditional preview
            cols = st.columns([0.55, 0.15, 0.30])

            with cols[0]:
                st.markdown(f"**{index}.** {question}")

            with cols[1]:
                widget_key = state.get_stable_key(field_name)

                # After JSON import, prioritize form_data over stale widget state
                if state.was_data_just_imported():
                    current_value = state.get_field_value(field_name, "no")
                elif widget_key in st.session_state:
                    current_value = st.session_state[widget_key]
                else:
                    current_value = state.get_field_value(field_name, "no")

                # Find index for current value
                try:
                    default_index = si_no_options.index(current_value)
                except ValueError:
                    default_index = 0  # Default to "no"

                selected = st.selectbox(
                    f"Incluir comentario {index}",
                    options=si_no_options,
                    index=default_index,
                    key=widget_key,
                    label_visibility="collapsed",
                )

                state.set_field_value(field_name, selected)

            with cols[2]:
                # Show preview only if "si" is selected
                if selected == "si" and text_preview:
                    st.text_area(
                        f"Vista previa comentario {index}",
                        value=text_preview,
                        height=80,
                        disabled=True,
                        label_visibility="collapsed",
                    )

        st.divider()
