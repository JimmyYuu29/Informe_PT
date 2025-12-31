# modules/context_builder.py
"""
Context Builder - Build rendering context from input data and derived fields.
"""
from datetime import date
from decimal import Decimal, ROUND_HALF_UP
from typing import Any, Optional
from .plugin_loader import PluginPack


# Spanish month names (full)
SPANISH_MONTHS = {
    1: "enero",
    2: "febrero",
    3: "marzo",
    4: "abril",
    5: "mayo",
    6: "junio",
    7: "julio",
    8: "agosto",
    9: "septiembre",
    10: "octubre",
    11: "noviembre",
    12: "diciembre",
}

# English month abbreviations
ENGLISH_MONTH_ABBR = {
    1: "Jan",
    2: "Feb",
    3: "Mar",
    4: "Apr",
    5: "May",
    6: "Jun",
    7: "Jul",
    8: "Aug",
    9: "Sep",
    10: "Oct",
    11: "Nov",
    12: "Dec",
}


def format_spanish_date(d: date) -> str:
    """Format a date in Spanish long format: '31 de diciembre de 2025'."""
    month_name = SPANISH_MONTHS.get(d.month, str(d.month))
    return f"{d.day} de {month_name} de {d.year}"


def format_date_short_english(d: date) -> str:
    """Format a date in short English format: '31 Dec 2025'."""
    month_abbr = ENGLISH_MONTH_ABBR.get(d.month, str(d.month))
    return f"{d.day} {month_abbr} {d.year}"


def format_currency_eur(value: Any) -> str:
    """Format a currency value in EUR format: '1.500.000 €'."""
    if value is None:
        return ""
    try:
        num = Decimal(str(value))
        # Round to whole number
        num = num.quantize(Decimal("1"), rounding=ROUND_HALF_UP)
        # Format with dots as thousand separators
        formatted = f"{num:,.0f}".replace(",", ".")
        return f"{formatted} €"
    except Exception:
        return str(value)


def format_percentage(value: Any, precision: int = 2) -> str:
    """Format a percentage value: '15,00 %'."""
    if value is None:
        return ""
    try:
        num = Decimal(str(value))
        pattern = f"1.{'0' * precision}"
        num = num.quantize(Decimal(pattern), rounding=ROUND_HALF_UP)
        # Replace decimal point with comma for Spanish format
        formatted = str(num).replace(".", ",")
        return f"{formatted} %"
    except Exception:
        return str(value)


def sanitize_template_value(value: Any) -> Any:
    """
    Sanitize a value for safe insertion into DOCX template.
    Ensures proper formatting and no unwanted whitespace that could
    disrupt table layouts.
    """
    if value is None:
        return ""
    if isinstance(value, str):
        # Strip leading/trailing whitespace that could affect alignment
        return value.strip()
    if isinstance(value, (int, float, Decimal)):
        return value
    if isinstance(value, list):
        return [sanitize_template_value(v) for v in value]
    if isinstance(value, dict):
        return {k: sanitize_template_value(v) for k, v in value.items()}
    return value


def calculate_derived_fields(data: dict, derived_defs: dict) -> dict:
    """
    Calculate all derived fields from input data.

    Args:
        data: Input data dictionary.
        derived_defs: Derived field definitions.

    Returns:
        Dictionary of calculated derived values.
    """
    derived = {}

    # Order of calculation is important - follow calculation_order if provided
    calculation_groups = [
        ["anyo_ejercicio", "anyo_ejercicio_ant"],
        ["cost_1", "cost_0"],
        ["om_1", "om_0", "ncp_1", "ncp_0"],
        ["var_cifra", "var_cost", "var_ebit", "var_resfin", "var_ebt", "var_resnet", "var_om", "var_ncp"],
        ["total_ingreso_oov", "total_gasto_oov"],
        ["peso_oov_sobre_incn", "peso_oov_sobre_costes"],
    ]

    # Helper to get value from data or derived
    def get_val(field: str) -> Any:
        if field in derived:
            return derived[field]
        return data.get(field)

    def safe_divide(a: Any, b: Any, default: str = "N/A") -> Any:
        try:
            a_dec = Decimal(str(a)) if a is not None else None
            b_dec = Decimal(str(b)) if b is not None else None
            if a_dec is None or b_dec is None or b_dec == 0:
                return default
            return a_dec / b_dec
        except Exception:
            return default

    for group in calculation_groups:
        for field_id in group:
            if field_id not in derived_defs:
                continue

            field_def = derived_defs[field_id]
            formula = field_def.get("formula", "")

            try:
                # Date derivations
                if field_id == "anyo_ejercicio":
                    fecha = data.get("fecha_fin_fiscal")
                    if isinstance(fecha, date):
                        derived[field_id] = fecha.year
                    elif isinstance(fecha, str):
                        derived[field_id] = int(fecha.split("-")[0])

                elif field_id == "anyo_ejercicio_ant":
                    anyo = get_val("anyo_ejercicio")
                    if anyo:
                        derived[field_id] = anyo - 1

                # Cost derivations
                elif field_id == "cost_1":
                    cifra_1 = get_val("cifra_1")
                    ebit_1 = get_val("ebit_1")
                    if cifra_1 is not None and ebit_1 is not None:
                        derived[field_id] = Decimal(str(cifra_1)) - Decimal(str(ebit_1))

                elif field_id == "cost_0":
                    cifra_0 = get_val("cifra_0")
                    ebit_0 = get_val("ebit_0")
                    if cifra_0 is not None and ebit_0 is not None:
                        derived[field_id] = Decimal(str(cifra_0)) - Decimal(str(ebit_0))

                # Margin derivations
                elif field_id == "om_1":
                    ebit_1 = get_val("ebit_1")
                    cifra_1 = get_val("cifra_1")
                    result = safe_divide(ebit_1, cifra_1)
                    if result != "N/A":
                        derived[field_id] = result * 100

                elif field_id == "om_0":
                    ebit_0 = get_val("ebit_0")
                    cifra_0 = get_val("cifra_0")
                    result = safe_divide(ebit_0, cifra_0)
                    if result != "N/A":
                        derived[field_id] = result * 100

                elif field_id == "ncp_1":
                    ebit_1 = get_val("ebit_1")
                    cost_1 = get_val("cost_1")
                    result = safe_divide(ebit_1, cost_1)
                    if result != "N/A":
                        derived[field_id] = result * 100

                elif field_id == "ncp_0":
                    ebit_0 = get_val("ebit_0")
                    cost_0 = get_val("cost_0")
                    result = safe_divide(ebit_0, cost_0)
                    if result != "N/A":
                        derived[field_id] = result * 100

                # Variation derivations
                elif field_id.startswith("var_"):
                    base_field = field_id[4:]  # Remove "var_" prefix
                    field_1 = f"{base_field}_1" if not base_field.endswith(("1", "0")) else base_field
                    field_0 = field_1[:-1] + "0" if field_1.endswith("1") else None

                    # Special mappings
                    if field_id == "var_cifra":
                        field_1, field_0 = "cifra_1", "cifra_0"
                    elif field_id == "var_cost":
                        field_1, field_0 = "cost_1", "cost_0"
                    elif field_id == "var_ebit":
                        field_1, field_0 = "ebit_1", "ebit_0"
                    elif field_id == "var_resfin":
                        field_1, field_0 = "resultado_fin_1", "resultado_fin_0"
                    elif field_id == "var_ebt":
                        field_1, field_0 = "ebt_1", "ebt_0"
                    elif field_id == "var_resnet":
                        field_1, field_0 = "resultado_net_1", "resultado_net_0"
                    elif field_id == "var_om":
                        om_1 = get_val("om_1")
                        om_0 = get_val("om_0")
                        if om_1 is not None and om_0 is not None:
                            derived[field_id] = om_1 - om_0
                        continue
                    elif field_id == "var_ncp":
                        ncp_1 = get_val("ncp_1")
                        ncp_0 = get_val("ncp_0")
                        if ncp_1 is not None and ncp_0 is not None:
                            derived[field_id] = ncp_1 - ncp_0
                        continue

                    if field_0:
                        val_1 = get_val(field_1)
                        val_0 = get_val(field_0)
                        if val_1 is not None and val_0 is not None:
                            val_0_abs = abs(Decimal(str(val_0)))
                            if val_0_abs != 0:
                                diff = Decimal(str(val_1)) - Decimal(str(val_0))
                                derived[field_id] = (diff / val_0_abs) * 100

                # Aggregate derivations
                elif field_id == "total_ingreso_oov":
                    servicios = data.get("servicios_vinculados", [])
                    total = Decimal(0)
                    for servicio in servicios:
                        for entidad in servicio.get("entidades_vinculadas", []):
                            ingreso = entidad.get("ingreso_entidad", 0)
                            if ingreso:
                                total += Decimal(str(ingreso))
                    derived[field_id] = total

                elif field_id == "total_gasto_oov":
                    servicios = data.get("servicios_vinculados", [])
                    total = Decimal(0)
                    for servicio in servicios:
                        for entidad in servicio.get("entidades_vinculadas", []):
                            gasto = entidad.get("gasto_entidad", 0)
                            if gasto:
                                total += Decimal(str(gasto))
                    derived[field_id] = total

                # Weight derivations
                elif field_id == "peso_oov_sobre_incn":
                    total_ingreso = get_val("total_ingreso_oov")
                    cifra_1 = get_val("cifra_1")
                    result = safe_divide(total_ingreso, cifra_1)
                    if result != "N/A":
                        derived[field_id] = result * 100

                elif field_id == "peso_oov_sobre_costes":
                    total_gasto = get_val("total_gasto_oov")
                    cost_1 = get_val("cost_1")
                    result = safe_divide(total_gasto, cost_1)
                    if result != "N/A":
                        derived[field_id] = result * 100

            except Exception:
                # Skip field if calculation fails
                continue

    return derived


class ContextBuilder:
    """Builds the rendering context from input data and plugin configuration."""

    def __init__(self, plugin: PluginPack):
        self.plugin = plugin
        self.formatting = plugin.formatting

    def build_context(self, data: dict) -> dict:
        """
        Build the complete rendering context.

        Args:
            data: Input data dictionary.

        Returns:
            Context dictionary for template rendering.
        """
        context = dict(data)  # Start with input data

        # Calculate derived fields
        derived_defs = self.plugin.get_derived_fields()
        derived_values = calculate_derived_fields(data, derived_defs)
        context.update(derived_values)

        # Format special fields
        context = self._format_fields(context)

        # Add text blocks
        context["texts"] = self._get_text_blocks()

        # Add fixed lists
        context["fixed_lists"] = self.plugin.texts.get("fixed_lists", {})

        # Sanitize all values to ensure proper template insertion
        # This helps preserve table layouts by removing unwanted whitespace
        context = sanitize_template_value(context)

        return context

    def _format_fields(self, context: dict) -> dict:
        """Apply formatting to fields."""
        # Format date - using short English format: "31 Dec 2025"
        if "fecha_fin_fiscal" in context:
            fecha = context["fecha_fin_fiscal"]
            if isinstance(fecha, date):
                context["fecha_fin_fiscal_formatted"] = format_date_short_english(fecha)
            elif isinstance(fecha, str):
                try:
                    parts = fecha.split("-")
                    d = date(int(parts[0]), int(parts[1]), int(parts[2]))
                    context["fecha_fin_fiscal_formatted"] = format_date_short_english(d)
                except Exception:
                    context["fecha_fin_fiscal_formatted"] = fecha

        # Format currency fields
        currency_fields = self.formatting.get("currency_formats", {}).get("eur", {}).get("applies_to", [])
        for field in currency_fields:
            if field in context and context[field] is not None:
                context[f"{field}_formatted"] = format_currency_eur(context[field])

        # Format percentage fields
        pct_fields = self.formatting.get("percentage_formats", {}).get("standard", {}).get("applies_to", [])
        for field in pct_fields:
            if field in context and context[field] is not None:
                context[f"{field}_formatted"] = format_percentage(context[field])

        return context

    def _get_text_blocks(self) -> dict:
        """Get all text blocks for rendering."""
        return self.plugin.get_text_blocks()
