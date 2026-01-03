# Informe PT - 修改日志 / Changes Log

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
