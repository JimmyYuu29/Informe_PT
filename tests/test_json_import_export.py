#!/usr/bin/env python3
"""
Test JSON Import/Export Functionality

Tests the core import/export logic without requiring Streamlit.
"""
import sys
import json
from pathlib import Path
from datetime import date

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from modules.plugin_loader import load_plugin


def test_export_field_order():
    """Test that export field order includes all expected fields."""
    print("=== Test 1: Export Field Order ===")

    plugin = load_plugin("pt_review")

    # Get UI sections
    sections = plugin.get_ui_sections()

    # Build expected ordered fields manually (simulating _get_export_field_order)
    ordered_fields = []

    for section in sections:
        section_id = section.get("id", "")
        field_names = section.get("fields", [])

        if section_id == "sec_general":
            ordered_fields.extend([
                "fecha_fin_fiscal", "entidad_cliente",
                "master_file", "descripcion_actividad"
            ])
        elif section_id == "sec_financials":
            ordered_fields.extend([
                "cifra_1", "cifra_0",
                "ebit_1", "ebit_0",
                "resultado_fin_1", "resultado_fin_0",
                "ebt_1", "ebt_0",
                "resultado_net_1", "resultado_net_0",
            ])
        elif section_id == "sec_compliance_local":
            ordered_fields.extend([f"cumplimiento_resumen_local_{i}" for i in range(1, 4)])
        elif section_id == "sec_compliance_master":
            ordered_fields.extend([f"cumplimiento_resumen_mast_{i}" for i in range(1, 5)])
        elif section_id == "sec_risks":
            for idx in range(1, 13):
                ordered_fields.extend([
                    f"impacto_{idx}",
                    f"afectacion_pre_{idx}",
                    f"texto_mitigacion_{idx}",
                    f"afectacion_final_{idx}",
                ])
        elif section_id == "sec_local_detail":
            for idx in range(1, 15):
                ordered_fields.extend([
                    f"cumplido_local_{idx}",
                    f"texto_cumplido_local_{idx}",
                ])
        elif section_id == "sec_master_detail":
            for idx in range(1, 18):
                ordered_fields.extend([
                    f"cumplido_mast_{idx}",
                    f"texto_cumplido_mast_{idx}",
                ])
        elif section_id == "sec_anexo3":
            ordered_fields.append("texto_anexo3")
        elif section_id == "sec_contacts":
            for i in range(1, 4):
                ordered_fields.extend([
                    f"contacto{i}",
                    f"cargo_contacto{i}",
                    f"correo_contacto{i}",
                ])
        else:
            ordered_fields.extend(field_names)

    # Check expected sections
    expected_fields = {
        "sec_general": ["fecha_fin_fiscal", "entidad_cliente", "master_file", "descripcion_actividad"],
        "sec_financials": ["cifra_1", "cifra_0", "ebit_1", "ebit_0", "resultado_fin_1",
                          "resultado_fin_0", "ebt_1", "ebt_0", "resultado_net_1", "resultado_net_0"],
        "sec_anexo3": ["texto_anexo3"],
        "sec_contacts": ["contacto1", "cargo_contacto1", "correo_contacto1",
                        "contacto2", "cargo_contacto2", "correo_contacto2",
                        "contacto3", "cargo_contacto3", "correo_contacto3"],
    }

    all_passed = True
    for section, fields in expected_fields.items():
        for field in fields:
            if field in ordered_fields:
                print(f"  ✓ {field} in export order")
            else:
                print(f"  ✗ {field} MISSING from export order")
                all_passed = False

    if all_passed:
        print("\nTest 1 PASSED: All expected fields are in export order")
    else:
        print("\nTest 1 FAILED: Some fields are missing")

    return all_passed


def test_json_roundtrip():
    """Test JSON export/import roundtrip simulation."""
    print("\n=== Test 2: JSON Roundtrip Simulation ===")

    # Simulate form data (what would be in st.session_state.form_data)
    form_data = {
        # sec_general
        "fecha_fin_fiscal": "2025-12-31",
        "entidad_cliente": "Test Company S.L.",
        "master_file": 1,
        "descripcion_actividad": "Actividad de prueba para testing",

        # sec_financials
        "cifra_1": 1500000.50,
        "cifra_0": 1200000.25,
        "ebit_1": 250000.00,
        "ebit_0": 200000.00,
        "resultado_fin_1": -15000.00,
        "resultado_fin_0": -12000.00,
        "ebt_1": 235000.00,
        "ebt_0": 188000.00,
        "resultado_net_1": 180000.00,
        "resultado_net_0": 145000.00,

        # sec_anexo3
        "texto_anexo3": "Comentario de prueba para Anexo III",

        # sec_contacts
        "contacto1": "Juan García",
        "cargo_contacto1": "Director Financiero",
        "correo_contacto1": "juan.garcia@test.com",
        "contacto2": "María López",
        "cargo_contacto2": "Controller",
        "correo_contacto2": "maria.lopez@test.com",
        "contacto3": "Pedro Sánchez",
        "cargo_contacto3": "Analista",
        "correo_contacto3": "pedro.sanchez@test.com",
    }

    list_items = {
        "documentacion_facilitada": [
            {"value": "Cuentas anuales 2024"},
            {"value": "Declaración IS 2024"},
        ],
        "servicios_vinculados": [
            {
                "servicio_vinculado": "Servicios de gestión",
                "entidades_vinculadas": [
                    {"entidad_vinculada": "Parent Corp", "ingreso_entidad": 50000, "gasto_entidad": 0},
                ]
            }
        ],
    }

    # Simulate export
    def serialize_value(v):
        if isinstance(v, date):
            return v.isoformat()
        elif isinstance(v, list):
            return [serialize_value(item) for item in v]
        elif isinstance(v, dict):
            return {k: serialize_value(val) for k, val in v.items()}
        return v

    serialized = {}
    for k, v in form_data.items():
        serialized[k] = serialize_value(v)

    serialized["_list_items"] = {}
    for field_name, items in list_items.items():
        serialized["_list_items"][field_name] = []
        for item in items:
            cleaned = {k: serialize_value(v) for k, v in item.items() if not k.startswith("_")}
            serialized["_list_items"][field_name].append(cleaned)

    serialized["_metadata"] = {
        "exported_at": date.today().isoformat(),
        "plugin_id": "pt_review",
        "version": "2.0",
    }

    json_str = json.dumps(serialized, ensure_ascii=False, indent=2)
    print(f"  Exported JSON length: {len(json_str)} bytes")

    # Simulate import
    json_data = json.loads(json_str)

    # Check that all original data is recoverable
    all_passed = True

    # Check scalar fields
    for key, expected_value in form_data.items():
        if key in json_data:
            actual_value = json_data[key]
            if actual_value == expected_value or str(actual_value) == str(expected_value):
                print(f"  ✓ {key}: matches")
            else:
                print(f"  ✗ {key}: expected {expected_value}, got {actual_value}")
                all_passed = False
        else:
            print(f"  ✗ {key}: MISSING from JSON")
            all_passed = False

    # Check list items
    for field_name, expected_items in list_items.items():
        if field_name in json_data["_list_items"]:
            actual_items = json_data["_list_items"][field_name]
            if len(actual_items) == len(expected_items):
                print(f"  ✓ {field_name}: {len(actual_items)} items")
            else:
                print(f"  ✗ {field_name}: expected {len(expected_items)} items, got {len(actual_items)}")
                all_passed = False
        else:
            print(f"  ✗ {field_name}: MISSING from _list_items")
            all_passed = False

    if all_passed:
        print("\nTest 2 PASSED: All data survives roundtrip")
    else:
        print("\nTest 2 FAILED: Some data was lost")

    return all_passed


def test_widget_key_prefixes():
    """Test that widget key prefixes cover all expected fields."""
    print("\n=== Test 3: Widget Key Prefix Coverage ===")

    # Widget prefixes from state_store.py
    widget_prefixes = (
        "field_",
        "entidad_",
        "servicio_oovv_",
        "analizar_servicio_",
        "rm_",
        "add_",
        "remove_",
        "_action_",
        "servicio_",
        "cumplimiento_",
        "impacto_",
        "afectacion_",
        "texto_",
        "cumplido_",
        "contacto",
        "cargo_",
        "correo_",
        "fecha_",
        "master_",
        "descripcion_",
        "cifra_",
        "ebit_",
        "resultado_",
        "ebt_",
    )

    # Expected widget keys that should be covered
    expected_widget_keys = [
        "field_fecha_fin_fiscal",
        "field_entidad_cliente",
        "field_master_file",
        "field_descripcion_actividad",
        "field_cifra_1",
        "field_ebit_1",
        "field_resultado_fin_1",
        "field_ebt_1",
        "field_resultado_net_1",
        "field_texto_anexo3",
        "field_contacto1",
        "field_cargo_contacto1",
        "field_correo_contacto1",
    ]

    all_passed = True
    for key in expected_widget_keys:
        if any(key.startswith(prefix) for prefix in widget_prefixes):
            print(f"  ✓ {key} covered by prefixes")
        else:
            print(f"  ✗ {key} NOT covered by prefixes")
            all_passed = False

    if all_passed:
        print("\nTest 3 PASSED: All widget keys covered")
    else:
        print("\nTest 3 FAILED: Some widget keys not covered")

    return all_passed


def test_json_field_order():
    """Test that JSON export maintains field order."""
    print("\n=== Test 4: JSON Field Order ===")

    # Simulate ordered export
    plugin = load_plugin("pt_review")
    sections = plugin.get_ui_sections()

    # Print section order
    print("  UI Section order:")
    for i, section in enumerate(sections):
        print(f"    {i+1}. {section.get('id')} - {section.get('label')}")

    # Verify key sections are in correct order
    section_ids = [s.get("id") for s in sections]

    expected_order = [
        "sec_general",
        "sec_financials",
        "sec_documents",
        "sec_operations",
        "sec_services",
        "sec_compliance_local",
        "sec_compliance_master",
        "sec_risks",
        "sec_local_detail",
        "sec_master_detail",
        "sec_anexo3",
        "sec_contacts",
    ]

    all_passed = True
    for i, expected in enumerate(expected_order):
        if i < len(section_ids) and section_ids[i] == expected:
            print(f"  ✓ Position {i+1}: {expected}")
        else:
            actual = section_ids[i] if i < len(section_ids) else "MISSING"
            print(f"  ✗ Position {i+1}: expected {expected}, got {actual}")
            all_passed = False

    if all_passed:
        print("\nTest 4 PASSED: Section order is correct")
    else:
        print("\nTest 4 FAILED: Section order is incorrect")

    return all_passed


if __name__ == "__main__":
    print("=" * 60)
    print("JSON Import/Export Functionality Tests")
    print("=" * 60)

    results = []

    results.append(("Export Field Order", test_export_field_order()))
    results.append(("JSON Roundtrip", test_json_roundtrip()))
    results.append(("Widget Key Prefixes", test_widget_key_prefixes()))
    results.append(("JSON Field Order", test_json_field_order()))

    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)

    all_passed = True
    for name, passed in results:
        status = "✓ PASSED" if passed else "✗ FAILED"
        print(f"  {status}: {name}")
        if not passed:
            all_passed = False

    print("\n" + "=" * 60)
    if all_passed:
        print("ALL TESTS PASSED")
    else:
        print("SOME TESTS FAILED")
    print("=" * 60)

    sys.exit(0 if all_passed else 1)
