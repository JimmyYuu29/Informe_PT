# Informe PT - 修改日志 / Changes Log

**日期 / Date:** 2026-01-03
**分支 / Branch:** claude/fix-json-import-errors-tIsT2

---

## 修改概述 / Summary of Changes

本次修改解决了以下问题：

1. JSON 导入时 Información General、Datos Financieros、Anexo III - Comentarios、Contactos 板块数据丢失
2. JSON 导出顺序与 UI 完全一致化
3. Widget 状态清理机制优化

---

## 1. JSON 导入数据丢失修复 / JSON Import Data Loss Fix

### 问题描述 / Problem
JSON 元数据导入后，以下板块数据无法正确显示：
- **Información General** (fecha_fin_fiscal, entidad_cliente, master_file, descripcion_actividad)
- **Datos Financieros** (cifra_1, cifra_0, ebit_1, ebit_0, 等) - 计算结果显示但输入数据丢失
- **Anexo III - Comentarios** (texto_anexo3)
- **Contactos** (contacto1-3, cargo_contacto1-3, correo_contacto1-3)

### 根本原因 / Root Cause
1. Widget 键值清理不完整，部分字段前缀（如 contacto, cargo_, correo_, fecha_, cifra_, ebit_ 等）未被包含在清理列表中
2. 导入后 widget 状态未完全同步，导致 Streamlit 使用缓存的 widget 值而非导入的数据

### 解决方案 / Solution

#### 1.1 扩展 Widget 键值清理模式
在 `ui/streamlit_app/state_store.py` 中添加更多 widget 键值前缀：

```python
widget_prefixes = (
    # 原有前缀
    "field_", "entidad_", "servicio_oovv_", ...
    # 新增前缀 - 覆盖所有缺失板块
    "contacto", "cargo_", "correo_",      # sec_contacts
    "fecha_", "master_", "descripcion_",  # sec_general
    "cifra_", "ebit_", "resultado_", "ebt_",  # sec_financials
)
```

#### 1.2 优化 `_force_clear_widget_state()` 函数
在 `ui/streamlit_app/app.py` 中同步添加相同的清理模式：

```python
if any(pattern in key for pattern in (
    "field_", "entidad_", "servicio_", ...
    # 新增模式
    "contacto", "cargo_", "correo_", "fecha_", "master_",
    "descripcion_", "cifra_", "ebit_", "resultado_", "ebt_"
)):
```

#### 1.3 优化 `load_json_data()` 导入流程
改进导入顺序，确保 widget 状态在数据加载前后都被正确清理：

```python
def load_json_data(json_data: dict) -> None:
    # FIRST: 在清理 form_data 之前先清理 widget 状态
    _force_clear_widget_state()

    # 清理现有数据并设置导入标志
    state.clear_form_data()

    # ... 加载数据 ...

    # FINAL: 再次清理任何可能干扰的 widget 状态
    _force_clear_widget_state()

    # 确保导入标志仍然被设置
    st.session_state._data_just_imported = True
```

---

## 2. JSON 导出顺序与 UI 完全一致化 / JSON Export Order Full Alignment

### 问题描述 / Problem
导出的 JSON 字段顺序与 UI 界面中的显示顺序不一致，特别是对于特殊板块。

### 解决方案 / Solution

#### 2.1 添加板块专用字段顺序函数
在 `ui/streamlit_app/app.py` 中为每个特殊板块添加专用排序函数：

```python
def _get_financials_field_order() -> list[str]:
    """财务数据字段顺序"""
    return [
        "cifra_1", "cifra_0",
        "ebit_1", "ebit_0",
        "resultado_fin_1", "resultado_fin_0",
        "ebt_1", "ebt_0",
        "resultado_net_1", "resultado_net_0",
    ]

def _get_compliance_resumen_order(prefix: str, total_rows: int) -> list[str]:
    """合规摘要字段顺序"""
    return [f"cumplimiento_resumen_{prefix}_{i}" for i in range(1, total_rows + 1)]

def _get_contacts_field_order() -> list[str]:
    """联系人字段顺序"""
    fields = []
    for i in range(1, 4):
        fields.extend([f"contacto{i}", f"cargo_contacto{i}", f"correo_contacto{i}"])
    return fields
```

#### 2.2 更新 `_get_export_field_order()` 函数
为每个板块使用显式排序：

```python
def _get_export_field_order(plugin: PluginPack) -> list[str]:
    ordered_fields: list[str] = []
    for section in plugin.get_ui_sections():
        section_id = section.get("id", "")

        if section_id == "sec_general":
            ordered_fields.extend(["fecha_fin_fiscal", "entidad_cliente",
                                   "master_file", "descripcion_actividad"])
        elif section_id == "sec_financials":
            ordered_fields.extend(_get_financials_field_order())
        elif section_id == "sec_anexo3":
            ordered_fields.append("texto_anexo3")
        elif section_id == "sec_contacts":
            ordered_fields.extend(_get_contacts_field_order())
        # ... 其他板块处理 ...

    return ordered_fields
```

---

## 修改的文件 / Modified Files

| 文件 / File | 修改类型 / Change Type |
|------------|----------------------|
| `ui/streamlit_app/state_store.py` | 扩展 widget 键值清理前缀列表 |
| `ui/streamlit_app/app.py` | 优化导入流程、添加导出字段顺序函数 |
| `CHANGES_LOG.md` | 更新修改日志 |

---

## 测试验证 / Testing Verification

### 导入导出测试 / Import/Export Test
1. 在表单中填写所有板块数据
2. 导出 JSON 文件
3. 清空表单
4. 重新导入 JSON 文件
5. 验证以下板块数据正确显示：
   - ✓ Información General (日期、客户名称、Master File 访问、活动描述)
   - ✓ Datos Financieros (所有财务数据字段)
   - ✓ Anexo III - Comentarios (评论文本)
   - ✓ Contactos (所有联系人信息)

---

*生成时间 / Generated at: 2026-01-03*

---
---

# 历史修改记录 / Historical Changes

**日期 / Date:** 2026-01-03
**分支 / Branch:** work

---

## 修改概述 / Summary of Changes

本次修改解决了以下问题：

1. JSON 导出顺序与 UI 一致化
2. 特殊表格字段导出顺序补齐
3. JSON 导入增加封装结构兼容

---

## 1. JSON 导出顺序与 UI 一致化 / JSON Export Order Alignment

### 问题描述 / Problem
导出的 JSON 字段顺序与 UI 表单顺序不一致，且部分特殊表格字段缺少与界面一致的导出顺序。

### 根本原因 / Root Cause
导出逻辑依赖 `session_state.form_data` 的插入顺序，未基于 UI section 与表格渲染顺序进行排序。

### 解决方案 / Solution

#### 1.1 统一导出字段顺序
在 `ui/streamlit_app/app.py` 中根据 UI section 顺序生成导出字段顺序，并将未在 UI 列表中的字段追加到末尾：

```python
ordered_fields = _get_export_field_order(plugin)
for field_name in ordered_fields:
    if field_name in list_field_names:
        continue
    if field_name in st.session_state.form_data:
        serialized[field_name] = serialize_value(st.session_state.form_data[field_name])
```

#### 1.2 补齐特殊表格字段顺序
为风险评估与合规明细表添加固定字段顺序，保证导出顺序与 UI 表格一致：

```python
def _get_risk_field_order() -> list[str]:
    return [
        "impacto_1", "afectacion_pre_1", "texto_mitigacion_1", "afectacion_final_1",
        ...
    ]
```

### 修改的文件 / Modified Files
- `ui/streamlit_app/app.py` - 新增导出字段排序与表格顺序逻辑
- `CHANGES_LOG.md` - 更新修改日志

---

## 2. JSON 导入封装结构兼容 / JSON Import Wrapper Compatibility

### 问题描述 / Problem
部分导入 JSON 将表单数据封装在 `form_data` 或 `list_items` 字段中，导致标量字段未被正确读取。

### 解决方案 / Solution
在导入逻辑中增加 payload 归一化处理，优先合并封装的表单数据与列表数据：

```python
if isinstance(json_data.get("form_data"), dict):
    normalized = dict(json_data["form_data"])
    if "_list_items" in json_data:
        normalized["_list_items"] = json_data["_list_items"]
```

### 修改的文件 / Modified Files
- `ui/streamlit_app/app.py` - 增加导入 payload 归一化逻辑

---

**日期 / Date:** 2026-01-03
**分支 / Branch:** claude/fix-json-metadata-import-0PLXS

---

## 修改概述 / Summary of Changes

本次修改解决了以下问题：

1. JSON 元数据导入问题的深度修复
2. 添加 requirements.txt 依赖文件

---

## 1. JSON 元数据导入深度修复 / JSON Metadata Import Deep Fix

### 问题描述 / Problem
JSON 元数据导入后，部分数据无法正确显示在表单中。这是由于 Streamlit 的 session_state 机制导致：当 widget 有 `key` 参数时，Streamlit 会优先使用 `session_state[key]` 中的值，而忽略 `value` 参数传递的新值。

### 根本原因 / Root Cause
1. Widget state keys 清理不完整，部分 widget 保留了旧值
2. 导入数据后，widget 状态没有完全同步

### 解决方案 / Solution

#### 1.1 扩展 widget key 清理范围
在 `ui/streamlit_app/state_store.py` 中的 `clear_form_data()` 函数添加更多 widget key 前缀：

```python
widget_prefixes = (
    "field_",
    "entidad_",
    "servicio_oovv_",
    "analizar_servicio_",
    "rm_",
    "add_",
    "remove_",
    "_action_",
    # Additional prefixes
    "servicio_",
    "cumplimiento_",
    "impacto_",
    "afectacion_",
    "texto_",
    "cumplido_",
)
```

#### 1.2 添加强制清理函数
在 `ui/streamlit_app/app.py` 中添加 `_force_clear_widget_state()` 函数，在数据导入后执行二次清理：

```python
def _force_clear_widget_state() -> None:
    """Force clear all widget state keys that might interfere with imported data."""
    patterns_to_clear = []
    for key in list(st.session_state.keys()):
        if key in ("initialized", "plugin_id", "form_data", "list_items", ...):
            continue
        if any(pattern in key for pattern in (
            "field_", "entidad_", "servicio_", ...
        )):
            patterns_to_clear.append(key)
    for key in patterns_to_clear:
        del st.session_state[key]
```

#### 1.3 改进 load_json_data 函数
- 优化处理顺序：先处理 list items，再处理 scalar fields
- 添加对 v2.0 格式中顶层列表的额外处理
- 在数据导入结束时调用 `_force_clear_widget_state()`

### 修改的文件 / Modified Files
- `ui/streamlit_app/state_store.py` - 扩展 widget key 清理范围
- `ui/streamlit_app/app.py` - 添加强制清理函数，改进导入逻辑

---

## 2. 添加 requirements.txt / Add requirements.txt

### 文件内容 / File Contents
```
# Informe PT - Python Dependencies
streamlit>=1.28.0
python-docx>=0.8.11
docxtpl>=0.16.0
fastapi>=0.104.0
uvicorn>=0.24.0
pydantic>=2.0.0
pyyaml>=6.0
pytest>=7.4.0
```

---

## 文件修改摘要 / Files Modified Summary

| 文件 / File | 修改类型 / Change Type |
|------------|----------------------|
| `ui/streamlit_app/state_store.py` | 扩展 widget key 清理范围 |
| `ui/streamlit_app/app.py` | 添加强制清理函数，改进导入逻辑 |
| `requirements.txt` | 新增依赖文件 |
| `CHANGES_LOG.md` | 更新修改日志 |

---

*生成时间 / Generated at: 2026-01-03*

---
---

# 历史修改记录 / Historical Changes

**日期 / Date:** 2026-01-03
**分支 / Branch:** claude/fix-master-file-ui-Upmor

---

## 修改概述 / Summary of Changes

本次修改解决了以下问题：

1. Master File Resumen 表格UI修复
2. JSON导入嵌套数据结构修复

---

## 1. Master File Resumen 表格UI修复 / Master File Resumen Table UI Fix

### 问题描述 / Problem
当 `master_file == 1` 时，"Cumplimiento Master File (Resumen)" 板块的UI显示不正确，需要调整为与 "Cumplimiento Local File (Resumen)" 相同的表格样式。

### 解决方案 / Solution
在 `ui/streamlit_app/form_renderer.py` 中添加了新的 `render_cumplimiento_resumen_master_table` 函数，并更新了 `render_section` 函数以正确路由该板块。

#### 新增函数 / New Function
```python
def render_cumplimiento_resumen_master_table(context: dict, fields_def: dict) -> None:
    """
    Render the Master File cumplimiento resumen (compliance summary) table
    matching the template layout.

    Table structure based on Artículo 15 del Reglamento:
    | # | Secciones (Artículo 15 del Reglamento) | Cumplimiento |
    """
    sections = [
        {"num": 1, "label": "Información relativa a la estructura y actividades del Grupo"},
        {"num": 2, "label": "Información relativa a los activos intangibles del Grupo"},
        {"num": 3, "label": "Información relativa a la actividad financiera"},
        {"num": 4, "label": "Situación financiera y fiscal del Grupo"},
    ]
```

#### 表格结构 / Table Structure
| # | Secciones (Artículo 15 del Reglamento) | Cumplimiento |
|---|----------------------------------------|--------------|
| 1 | Información relativa a la estructura y actividades del Grupo | si/no |
| 2 | Información relativa a los activos intangibles del Grupo | si/no |
| 3 | Información relativa a la actividad financiera | si/no |
| 4 | Situación financiera y fiscal del Grupo | si/no |

### 修改的文件 / Modified Files
- `ui/streamlit_app/form_renderer.py`
  - 添加 `render_cumplimiento_resumen_master_table()` 函数 (第984-1030行)
  - 更新 `render_section()` 函数添加 `sec_compliance_master` 路由 (第204行)

---

## 2. JSON导入嵌套数据结构修复 / JSON Import Nested Data Fix

### 问题描述 / Problem
JSON元数据导入时无法正确接收和显示所有数据，特别是嵌套数据结构（如 `servicios_vinculados` 中的 `entidades_vinculadas` 和 `analisis`）。

### 解决方案 / Solution
在 `ui/streamlit_app/app.py` 中更新 `load_json_data` 函数，使用 `copy.deepcopy()` 处理嵌套数据结构。

#### 修改前 / Before
```python
state.add_list_item(field_name, item.copy())  # 浅拷贝
```

#### 修改后 / After
```python
import copy
state.add_list_item(field_name, copy.deepcopy(item))  # 深拷贝
```

### 修改的文件 / Modified Files
- `ui/streamlit_app/app.py`
  - 添加 `import copy` (第11行)
  - 更新 `load_json_data()` 函数使用 `copy.deepcopy()` (第221-271行)
  - 排除已在 `_list_items` 中的字段避免重复处理 (第243行)

### 修复的问题 / Fixed Issues
1. 嵌套列表和字典数据现在正确导入
2. 避免浅拷贝导致的引用问题
3. V2.0格式导入时排除重复字段

---

## 测试验证 / Testing Verification

### Master File 表格测试 / Master File Table Test
1. 设置 `master_file` = "Hay acceso" (值为1)
2. 验证 "Cumplimiento Master File (Resumen)" 板块显示
3. 确认表格包含4行，标题为 "Artículo 15 del Reglamento"

### JSON导入测试 / JSON Import Test
1. 导出包含嵌套数据的表单
2. 清空表单
3. 重新导入JSON文件
4. 验证所有数据正确显示，包括：
   - 基本字段 (entidad_cliente, fecha_fin_fiscal等)
   - 列表数据 (documentacion_facilitada)
   - 嵌套数据 (servicios_vinculados内的entidades_vinculadas和analisis)

---

## 文件修改摘要 / Files Modified Summary

| 文件 / File | 修改类型 / Change Type |
|------------|----------------------|
| `ui/streamlit_app/form_renderer.py` | 新增Master File表格渲染函数，更新section路由 |
| `ui/streamlit_app/app.py` | 修复JSON导入深拷贝处理 |
| `CHANGES_LOG.md` | 更新修改日志 |

---

*生成时间 / Generated at: 2026-01-03*

---
---

# 历史修改记录 / Historical Changes

**日期 / Date:** 2026-01-03
**分支 / Branch:** claude/fix-date-format-coloring-RiHT5

---

## 修改概述 / Summary of Changes

本次修改解决了以下四个主要问题：

1. 日期格式修改
2. 合规状态单元格颜色修改
3. "si" 值替换为勾号
4. JSON导入导出功能修复

---

## 1. 日期格式修改 / Date Format Change

### 问题描述 / Problem
`{{ fecha_fin_fiscal }}` 变量输出格式为 `31-Ene-2025`，需要更改为 `01 de enero del 2025` 格式。

### 解决方案 / Solution
在 `modules/context_builder.py` 中添加了新的日期格式化函数：

```python
def format_spanish_date_del(d: date) -> str:
    """Format a date in Spanish long format with 'del': '01 de enero del 2025'."""
    month_name = SPANISH_MONTHS.get(d.month, str(d.month))
    return f"{d.day:02d} de {month_name} del {d.year}"
```

### 修改的文件 / Modified Files
- `modules/context_builder.py`
  - 添加 `format_spanish_date_del()` 函数 (第67-70行)
  - 更新 `_format_fields()` 方法使用新格式 (第487-505行)

### 示例 / Example
- **输入 / Input:** `2025-01-01`
- **输出 / Output:** `01 de enero del 2025`

---

## 2. 合规摘要单元格颜色修改 / Compliance Summary Cell Coloring

### 问题描述 / Problem
`cumplimiento_resumen_local_*` 和 `cumplimiento_resumen_mast_*` 变量需要根据值进行颜色标记：
- 值为 "si" → 绿色背景
- 其他值 → 黄色背景

### 解决方案 / Solution
修改 `config/yamls/pt_review/formatting.yaml` 中的颜色配置：

```yaml
compliance_color:
  values:
    "si":
      background: "#00B050"  # 绿色 / Green
    "no":
      background: "#FFFF00"  # 黄色 / Yellow
```

### 修改的文件 / Modified Files
- `config/yamls/pt_review/formatting.yaml`
  - 更新 `compliance_color.values.no.background` 从 `#FF0000` 改为 `#FFFF00` (第149-158行)
  - 添加引号修复YAML布尔值解析问题

### 影响的变量 / Affected Variables (7个)
- `cumplimiento_resumen_local_1`, `cumplimiento_resumen_local_2`, `cumplimiento_resumen_local_3`
- `cumplimiento_resumen_mast_1`, `cumplimiento_resumen_mast_2`, `cumplimiento_resumen_mast_3`, `cumplimiento_resumen_mast_4`

---

## 3. "si" 值替换为勾号 / Replace "si" with Checkmark

### 问题描述 / Problem
以下变量当值为 "si" 时，需要在文档导出时显示为 "✓" 勾号：
- `cumplimiento_resumen_local_*`
- `cumplimiento_resumen_mast_*`
- `cumplido_local_*`
- `cumplido_mast_*`

### 解决方案 / Solution
在 `modules/context_builder.py` 中添加了勾号替换函数：

```python
COMPLIANCE_CHECKMARK_FIELDS = (
    ["cumplimiento_resumen_local_" + str(i) for i in range(1, 4)] +
    ["cumplimiento_resumen_mast_" + str(i) for i in range(1, 5)] +
    ["cumplido_local_" + str(i) for i in range(1, 15)] +
    ["cumplido_mast_" + str(i) for i in range(1, 18)]
)

def replace_si_with_checkmark(context: dict) -> dict:
    for field_name in COMPLIANCE_CHECKMARK_FIELDS:
        if field_name in context:
            value = context[field_name]
            if isinstance(value, str) and value.lower() == "si":
                context[field_name] = "✓"
    return context
```

### 修改的文件 / Modified Files
- `modules/context_builder.py`
  - 添加 `COMPLIANCE_CHECKMARK_FIELDS` 常量 (第73-84行)
  - 添加 `replace_si_with_checkmark()` 函数 (第87-107行)
  - 在 `build_context()` 中调用该函数 (第517-520行)
- `modules/renderer_docx.py`
  - 更新 `_apply_color_if_match()` 方法以支持勾号颜色匹配 (第166-169行)

### 影响的变量数量 / Number of Affected Variables
**共38个变量 / Total 38 variables:**
- `cumplimiento_resumen_local_1` 到 `cumplimiento_resumen_local_3` (3个)
- `cumplimiento_resumen_mast_1` 到 `cumplimiento_resumen_mast_4` (4个)
- `cumplido_local_1` 到 `cumplido_local_14` (14个)
- `cumplido_mast_1` 到 `cumplido_mast_17` (17个)

### 示例 / Example
- **输入值 / Input:** `si`, `Si`, `SI`
- **输出值 / Output:** `✓`
- **其他值不变 / Other values unchanged:** `no`, `parcial`

---

## 4. JSON导入导出功能修复 / JSON Import/Export Fix

### 问题描述 / Problem
- 导出的JSON不包含所有已填写的数据
- 导入JSON后无法正确恢复所有数据
- 特别是 "Información General"、"Datos Financieros"、"Contactos" 等部分数据缺失

### 解决方案 / Solution
修复了Streamlit组件在JSON导入后优先使用导入数据而非缓存的小部件状态的问题。

### 修改的文件 / Modified Files

#### `ui/streamlit_app/components.py`
更新了以下函数以正确处理导入标志：
- `render_date_input()` (第55-92行)
- `render_number_input()` (第95-136行)
- `render_checkbox()` (第197-222行)
- `render_dynamic_list()` (第252-298行)

每个函数现在都检查 `state.was_data_just_imported()` 以优先使用导入的数据：

```python
if state.was_data_just_imported():
    default_value = state.get_field_value(field_name)
elif widget_key in st.session_state:
    default_value = st.session_state[widget_key]
else:
    default_value = state.get_field_value(field_name)
```

#### `ui/streamlit_app/form_renderer.py`
更新了以下表格渲染函数：
- `render_operaciones_intragrupo_table()` (第548-568行)
- `render_operaciones_vinculadas_detail_table()` (第640-705行)
- `render_metodo_elegido_table()` (第773-934行)

添加了辅助函数来处理导入优先级：

```python
def get_imported_value(widget_key, data_dict, field, default):
    if state.was_data_just_imported():
        return data_dict.get(field, default)
    elif widget_key in st.session_state:
        return st.session_state[widget_key]
    else:
        return data_dict.get(field, default)
```

---

## 测试验证 / Testing Verification

### 日期格式测试 / Date Format Test
```python
from datetime import date
test_date = date(2025, 1, 1)
result = format_spanish_date_del(test_date)
# 结果: "01 de enero del 2025" ✓
```

### 勾号替换测试 / Checkmark Replacement Test
```python
test_context = {
    'cumplimiento_resumen_local_1': 'si',
    'cumplimiento_resumen_local_2': 'Si',
    'cumplimiento_resumen_local_3': 'no',
    'cumplido_local_1': 'si',
    'cumplido_local_2': 'parcial',
}
result = replace_si_with_checkmark(test_context)
# 结果:
#   cumplimiento_resumen_local_1: ✓
#   cumplimiento_resumen_local_2: ✓
#   cumplimiento_resumen_local_3: no
#   cumplido_local_1: ✓
#   cumplido_local_2: parcial
```

### 颜色配置测试 / Color Configuration Test
```python
import yaml
with open('config/yamls/pt_review/formatting.yaml', 'r') as f:
    formatting = yaml.safe_load(f)
compliance_color = formatting['enum_colors']['compliance_color']
# si: #00B050 (绿色) ✓
# no: #FFFF00 (黄色) ✓
```

---

## 注意事项 / Notes

1. **YAML布尔值问题 / YAML Boolean Issue:**
   YAML中的 `no` 会被解析为布尔值 `False`，需要使用引号 `"no"` 来保持字符串类型。

2. **向后兼容 / Backward Compatibility:**
   - `fecha_fin_fiscal` 现在提供多种格式：
     - `fecha_fin_fiscal`: 主格式 `01 de enero del 2025`
     - `fecha_fin_fiscal_formatted`: 短格式 `1 Ene 2025`
     - `fecha_fin_fiscal_dashed`: 虚线格式 `01-Ene-2025`

3. **导入导出 / Import/Export:**
   - 导出的JSON使用版本2.0格式，包含 `_list_items` 和 `_metadata` 字段
   - 导入支持v1.0和v2.0两种格式

---

## 文件修改摘要 / Files Modified Summary

| 文件 / File | 修改类型 / Change Type |
|------------|----------------------|
| `modules/context_builder.py` | 新增函数、修改方法 |
| `modules/renderer_docx.py` | 更新颜色匹配逻辑 |
| `config/yamls/pt_review/formatting.yaml` | 更新颜色配置 |
| `ui/streamlit_app/components.py` | 修复导入处理 |
| `ui/streamlit_app/form_renderer.py` | 修复表格导入处理 |

---

*生成时间 / Generated at: 2026-01-03*
