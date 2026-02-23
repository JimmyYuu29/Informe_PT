你是一个资深 Python 全栈工程师（Streamlit + FastAPI + SharePoint/Power Automate 集成），要在一个已完成的“配置驱动 Word 报告生成平台”上新增「方案2：模板管理（上传-校验-发布-元数据-回滚）」功能。

项目背景（已存在能力）：
- 系统是 configuration-driven document generation：JSON 输入 + YAML plugin pack + DOCX 模板（docxtpl placeholders / Jinja2）生成报告。
- 架构：modules/ 核心引擎；ui/streamlit_app/ 是 Streamlit UI；ui/api/backend/ 是 FastAPI。
- 已有 validate_plugin / golden tests 等 CI-ready 验证思路。
- 当前模板（默认）为 template_final.docx，里面有大量 {{变量}}、{% if %}、{% for %}、{%tr for %} 等结构；必须保证上传模板修改后不会破坏可渲染性与变量一致性。
（项目结构与能力以 README.md 为准）

目标：实现“模板管理 UI（方案2）”
1) 在 Streamlit UI 中新增一个页面（例如：⚙️ Template Admin），只有输入正确密码才可访问上传/发布功能。
   - 密码校验：默认密码 admin123，但不得硬编码在源码中；应支持从环境变量 TEMPLATE_ADMIN_PASSWORD 读取，若未设置则默认 admin123（初期）。
   - 会话级授权：用户输入一次正确密码后，session_state 记录授权状态；可显式“退出管理模式”。

2) 模板上传流程（无 Grupo IT 权限前提）：
   - 用户在 Template Admin 页面上传 DOCX（用于某个 plugin_id，如 pt_review），并填写元数据：
     - plugin_id（下拉：从现有 plugins 列表读取）
     - template_name（默认 template_final.docx 或 “template”）
     - change_log（必填）
     - author（可从当前用户输入或环境变量/配置读取）
   - 点击“Validate”后在服务器侧执行模板校验（必须做到可解释的报错）：
     A. Jinja2/docxtpl 语法可解析（至少能 compile）
     B. 变量一致性：从模板中提取到的变量集合 vs plugin pack schema/fields.yaml/contract_models 的可用字段集合（若现有系统没有“可用字段集合API”，请实现一个）
     C. 渲染冒烟测试：使用一份 sample input（优先 tests/golden/sample_input.json 或 plugin 内置 golden）渲染一遍，确保：
        - 渲染不报错
        - 输出 docx 不包含残留的 "{{" 或 "{%"（可简单搜索文本）
     D. Anchor/关键结构保护（可选但推荐）：支持检查某些关键占位符是否存在（例如 “Contactos”段落/签字/标题关键字），若缺失给 warning 或 fail（以配置开关控制）
   - 校验结果输出为：PASS/WARN/FAIL，显示错误列表（逐条，带定位建议），并生成 validation_report.json（包含变量列表、规则、时间戳、hash）。

3) 版本化发布（通过 Power Automate 回传到 SharePoint）：
   - 校验 PASS（或 PASS+WARN 在用户确认后）才能点击 “Publish”。
   - Publish 会生成一个新版本号（SemVer 或递增 build）。要求：
     - 每个 plugin_id 单独维护版本序列；
     - 版本号写入元数据，并生成一份 metadata.json（或 yaml）：
       {
         plugin_id,
         template_name,
         version,
         created_at,
         author,
         change_log,
         sha256,
         variables: [...],
         validation: {status, errors, warnings},
         previous_version (如有)
       }
   - 由于没有 Grupo IT 权限，写入 SharePoint 必须通过 Power Automate Flow：
     - 你要在 FastAPI backend 新增一个 endpoint，例如 POST /template/publish
     - 它会把 docx（base64）+ metadata.json（base64 或 json）+ 目标 SharePoint folder path + 文件命名规则 发给 Power Automate HTTP trigger URL。
     - Power Automate 负责将文件保存到 SharePoint 指定文件夹（如：/Templates/Released/<plugin_id>/），并把保存后的 sharepoint_file_url / item_id 回传给 API。
   - API 收到回传后，把 “发布记录”写入本地一个 registry（JSON 文件或 SQLite）。注意：不需要 IT 权限，应用可写自己目录下 data/ 或 .appdata/。
   - Streamlit UI 展示发布成功信息：版本号、SharePoint 链接、sha256、可回滚按钮。

4) 回滚（Rollback）：
   - 在 Template Admin 页面提供某 plugin_id 的版本列表（从本地 registry 读取；也可扩展为从 SharePoint 列目录，但优先简单可用）。
   - 用户选择某一版本点击 “Rollback to this version”：
     - 本质是把该版本标记为 active（在 registry 中设置 active_version），并在生成文档时默认使用 active_version 对应的模板（模板从 SharePoint 拉取或由 PA 再回传到本地缓存）。
   - 若你不想引入“从 SharePoint 读取”的复杂认证：
     - 采取“发布时同时写入本地缓存模板文件”的策略：即 Publish 成功后，把 docx 保存到本地缓存目录 data/templates_cache/<plugin_id>/<version>.docx，这样回滚无需访问 SharePoint。
     - 但仍保留 SharePoint 作为权威备份与审计。

5) 生成流程接入点（生产使用哪份模板）：
   - 当前生成使用的是 config/ 下的 template_final.docx（或 config/templates/<plugin_id>/template_final.docx）。需要改成：
     - 默认：使用 registry 的 active_version 模板（本地缓存优先）；
     - 若 registry 不存在或无 active_version：回退到 repo 内默认模板（保持向后兼容）。
   - 要保证不会破坏现有 scripts/run_generate.py 和 API /plugins/{id}/generate。

6) 配置与环境变量（必须）：
   - TEMPLATE_ADMIN_PASSWORD（默认 admin123）
   - POWER_AUTOMATE_TEMPLATE_PUBLISH_URL（必填）
   - SHAREPOINT_TARGET_ROOT（例如：/Templates/Released/）
   - TEMPLATE_REGISTRY_PATH（默认 data/template_registry.json）
   - TEMPLATE_CACHE_DIR（默认 data/templates_cache/）
   - 可选：ALLOW_PUBLISH_WITH_WARNINGS（默认 false）

7) 文件改动要求（输出必须给我具体到文件与关键函数签名）：
   - Streamlit：新增页面/组件（ui/streamlit_app/），例如 template_admin.py，并在 app.py 导航中挂载。
   - FastAPI：新增 routes（ui/api/backend/），例如 template_admin_routes.py，注册到 main.py。
   - modules：新增 template_registry.py、template_validator.py、sharepoint_publisher.py（HTTP 调 PA）
   - tests：为 template_validator 增加最少 2 个测试（一个 PASS 一个 FAIL），可使用现有 template_final.docx 作为 PASS 基准；FAIL 可用人为破坏的样例（生成临时docx或mock）
   - 文档：README 增加一节“Template Admin & Versioning”。

8) 验收标准（必须满足）：
   - 未输入正确密码无法上传/发布/回滚（UI 不展示敏感按钮或操作会被拦截）
   - 上传后点击 Validate 能得到明确结果（PASS/WARN/FAIL），且 FAIL 时不允许 Publish
   - Publish 成功会调用 Power Automate URL，并拿到回传的 SharePoint 链接
   - registry 记录完整元数据、可展示版本列表
   - 回滚后，新生成的报告确实使用回滚版本模板（写一个简单标记验证，例如模板里某个固定文本差异能反映出来，或在 audit log 中记录 template_version）
   - 不需要任何 SharePoint App Registration / Graph 权限（所有 SharePoint 写入都经由 Power Automate）

Power Automate 接口契约（你需要在代码中固定并文档化）：
- Request（FastAPI -> Power Automate）:
  {
    "plugin_id": "pt_review",
    "template_name": "template_final",
    "version": "1.2.0",
    "target_folder": "/Templates/Released/pt_review/",
    "files": [
      {"filename": "template_final__1.2.0.docx", "content_base64": "...", "content_type": "application/vnd.openxmlformats-officedocument.wordprocessingml.document"},
      {"filename": "metadata__1.2.0.json", "content_base64": "...", "content_type": "application/json"},
      {"filename": "validation_report__1.2.0.json", "content_base64": "...", "content_type": "application/json"}
    ]
  }
- Response（Power Automate -> FastAPI）:
  {
    "ok": true,
    "sharepoint": {
      "folder": "...",
      "template_file_url": "...",
      "metadata_file_url": "...",
      "validation_file_url": "...",
      "item_ids": {...}
    }
  }
- 错误响应：
  { "ok": false, "error": {"code": "...", "message": "...", "details": "..."} }

输出格式要求：
- 你需要直接给出可运行的代码改动（按上述文件拆分），并确保 imports/路径正确。
- 如果发现现有工程中某些函数/入口不同（例如生成逻辑、模板路径、插件加载），你要先阅读代码，再以最小侵入方式接入（保持向后兼容）。
- 请给出必要的代码注释与错误处理（尤其是 Power Automate 调用失败、超时、返回非 200、回传格式不符）。
- 请在 Streamlit UI 里给出清晰的交互：上传->Validate->(显示结果)->Publish->(显示链接/版本信息)，以及版本列表->Rollback。