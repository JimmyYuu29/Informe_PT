# Exportar e Importar Metadatos - Documentación Técnica

Este documento describe la implementación actual de las funcionalidades de exportar e importar metadatos (JSON) en la plataforma de generación de documentos.

## Visión General

La funcionalidad permite a los usuarios:
1. **Exportar** los datos del formulario a un archivo JSON
2. **Importar** datos desde un archivo JSON para prellenar el formulario

## Arquitectura

### Archivos Principales

| Archivo | Función |
|---------|---------|
| `ui/streamlit_app/app.py` | Funciones `export_form_data()` y `load_json_data()` |
| `ui/streamlit_app/state_store.py` | Gestión del estado de sesión y widgets |
| `ui/streamlit_app/form_renderer.py` | Renderización del formulario y manejo de valores |
| `tests/test_json_import_export.py` | Tests de la funcionalidad |

## Exportar Metadatos

### Función: `export_form_data()`

**Ubicación**: `ui/streamlit_app/app.py:267-333`

#### Flujo de Exportación

1. **Serialización de valores**: Convierte objetos `date` a formato ISO string
2. **Orden de campos**: Mantiene el orden de los campos según las secciones de UI
3. **Campos escalares**: Se exportan directamente en el JSON raíz
4. **Listas/Arrays**: Se exportan directamente como arrays en el JSON raíz
5. **Limpieza**: Se eliminan campos internos (prefijados con `_`)

#### Estructura del JSON Exportado

```json
{
  "fecha_fin_fiscal": "2025-12-31",
  "entidad_cliente": "Nombre de la empresa",
  "master_file": 1,
  "cifra_1": 1500000.00,
  "cifra_0": 1200000.00,
  "documentacion_facilitada": [
    {"value": "Cuentas anuales 2024"},
    {"value": "Declaración IS 2024"}
  ],
  "servicios_vinculados": [
    {
      "servicio_vinculado": "Servicios de gestión",
      "entidades_vinculadas": [
        {
          "entidad_vinculada": "Parent Corp",
          "ingreso_entidad": 50000,
          "gasto_entidad": 0
        }
      ],
      "analisis": {
        "enabled": true,
        "titulo_servicio_oovv": "...",
        "metodo": "...",
        "min": 0,
        "lq": 0,
        "med": 0,
        "uq": 0,
        "max": 0
      }
    }
  ],
  "comentario_valorativo_1": "si",
  "comentario_valorativo_2": "no"
}
```

### Orden de Campos

El orden sigue las secciones de UI:
1. `sec_general` - Información general
2. `sec_financials` - Datos financieros
3. `sec_documents` - Documentación
4. `sec_operations` - Operaciones intragrupo
5. `sec_services` - Servicios OOVV
6. `sec_compliance_local` - Cumplimiento Local File
7. `sec_compliance_master` - Cumplimiento Master File
8. `sec_risks` - Evaluación de riesgos
9. `sec_local_detail` - Detalle Local File
10. `sec_master_detail` - Detalle Master File
11. `sec_anexo3` - Anexo III y comentarios valorativos
12. `sec_contacts` - Contactos

## Importar Metadatos

### Función: `load_json_data()`

**Ubicación**: `ui/streamlit_app/app.py:428-489`

#### Flujo de Importación

1. **Normalización**: Soporta formato legacy con `_list_items` separado
2. **Limpieza de widgets**: Elimina el estado de widgets existente para evitar conflictos
3. **Procesamiento de campos**:
   - Campos escalares: Se guardan directamente en `form_data`
   - Campos lista: Se añaden elementos individualmente con IDs únicos
4. **Coerción de tipos**: Convierte strings ISO a objetos `date`, números a floats
5. **Flag de importación**: Se establece `_data_just_imported` para priorizar datos importados

#### Funciones Auxiliares

- `_force_clear_widget_state()`: Limpia el estado de widgets Streamlit
- `_coerce_widget_value()`: Normaliza valores importados a tipos apropiados

## Problemas Conocidos

### 1. Comentarios Valorativos (comentario_texto)

**Problema**: El texto de los comentarios valorativos puede aparecer con el título y cuerpo unidos sin separación visual.

**Causa**:
- El archivo fuente Word (`Text_comentario valorativo.docx`) no tiene párrafo vacío entre título y cuerpo
- En modo RichText (fallback), `\a` crea salto de línea suave, no párrafo nuevo

**Solución implementada** (v1.3.1):
- Subdoc: Se añade espaciado `after` al primer párrafo (título)
- RichText: Se añade `\a` adicional después del título

### 2. Estado de Widgets vs Datos Importados

**Problema**: Después de importar JSON, los widgets pueden mostrar valores antiguos en lugar de los importados.

**Causa**: Streamlit prioriza `session_state[widget_key]` sobre el parámetro `value` del widget.

**Solución**:
- `_force_clear_widget_state()` elimina claves de widgets antes de importar
- Flag `_data_just_imported` indica a los componentes que prioricen `form_data`

### 3. Listas Anidadas

**Problema**: Las estructuras anidadas (como `entidades_vinculadas` dentro de `servicios_vinculados`) requieren manejo especial.

**Solución**: Se usa `copy.deepcopy()` para evitar referencias compartidas y se procesan recursivamente.

## Limitaciones Actuales

1. **Comentarios valorativos**: El texto no se exporta/importa; solo el booleano "si/no"
2. **Formato de fechas**: Se espera formato ISO (YYYY-MM-DD)
3. **Validación**: No hay validación de esquema al importar
4. **Versiones**: No hay migración automática entre versiones de esquema

## Flujo de Datos Completo

```
┌─────────────────────────────────────────────────────────────────┐
│                    EXPORTAR METADATOS                           │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  session_state.form_data ──┐                                    │
│                            ├──► serialize_value() ──► JSON      │
│  session_state.list_items ─┘    (dates → ISO)       string      │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                    IMPORTAR METADATOS                           │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  JSON ──► _force_clear_widget_state() ──► clear_form_data()     │
│   │                                                             │
│   ├── campos escalares ──► _coerce_widget_value() ──► form_data │
│   │                                                             │
│   └── campos lista ──► add_list_item() ──► list_items           │
│                        (deepcopy)                               │
│                                                                 │
│  Flag: _data_just_imported = True                               │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                  GENERACIÓN DE DOCUMENTO                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  form_data + list_items                                         │
│        │                                                        │
│        ▼                                                        │
│  context_builder.build_context()                                │
│        │                                                        │
│        ├── calculate_derived_fields()                           │
│        ├── format_fields()                                      │
│        └── build_comentarios_context()                          │
│                │                                                │
│                ├── Si Subdoc disponible: create_comentarios_subdocs()
│                └── Si no: get_comentarios_richtext()            │
│                                                                 │
│        ▼                                                        │
│  DocxTemplate.render(context)                                   │
│        │                                                        │
│        ▼                                                        │
│  Documento Word generado                                        │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

## Recomendaciones para Desarrollo Futuro

1. **Validación de esquema**: Implementar validación JSON Schema al importar
2. **Migración de versiones**: Sistema para actualizar JSONs de versiones antiguas
3. **Exportar texto completo**: Opción para incluir el texto de comentarios valorativos
4. **Preview de importación**: Mostrar resumen de cambios antes de aplicar
5. **Backup automático**: Guardar estado anterior antes de importar
