#!/usr/bin/env python3
# ui/streamlit_app/template_admin.py
"""
Template Admin Page - Upload, validate, publish, and rollback DOCX templates.

This module adds a "⚙️ Template Admin" page to the Streamlit application.
Access is protected by a password (env var TEMPLATE_ADMIN_PASSWORD, default admin123).
"""
import os
import json
import streamlit as st
from pathlib import Path
from datetime import datetime

# Add project root to path
import sys
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from modules.plugin_loader import load_plugin, list_plugins
from modules.template_validator import validate_template, generate_validation_report
from modules.template_registry import TemplateRegistry
from modules.sharepoint_publisher import (
    publish_to_sharepoint, build_metadata, POWER_AUTOMATE_URL
)


# ============================================================================
# Configuration
# ============================================================================

ADMIN_PASSWORD = os.environ.get("TEMPLATE_ADMIN_PASSWORD", "admin123")
ALLOW_PUBLISH_WITH_WARNINGS = os.environ.get("ALLOW_PUBLISH_WITH_WARNINGS", "false").lower() == "true"


# ============================================================================
# Authentication
# ============================================================================

def check_admin_auth() -> bool:
    """Check if the user is authenticated as admin."""
    return st.session_state.get("template_admin_authorized", False)


def render_login() -> None:
    """Render the admin login form."""
    st.markdown("### 🔐 Template Admin Authentication")
    st.info("Enter the admin password to access template management features.")

    password = st.text_input(
        "Admin Password",
        type="password",
        key="template_admin_password_input",
        placeholder="Enter password..."
    )

    col1, col2 = st.columns([1, 3])
    with col1:
        if st.button("Login", type="primary", use_container_width=True):
            if password == ADMIN_PASSWORD:
                st.session_state.template_admin_authorized = True
                st.success("✅ Authenticated successfully!")
                st.rerun()
            else:
                st.error("❌ Incorrect password")


def render_logout() -> None:
    """Render logout button."""
    if st.button("🚪 Exit Admin Mode", use_container_width=True):
        st.session_state.template_admin_authorized = False
        # Clear template admin state
        for key in list(st.session_state.keys()):
            if key.startswith("tpl_"):
                del st.session_state[key]
        st.rerun()


# ============================================================================
# Upload & Validate Section
# ============================================================================

def render_upload_section() -> None:
    """Render template upload and validation section."""
    st.markdown("## 📤 Upload & Validate Template")

    # Plugin selection
    available_plugins = list_plugins()
    if not available_plugins:
        st.error("No plugins found")
        return

    col1, col2 = st.columns(2)
    with col1:
        plugin_id = st.selectbox(
            "Plugin",
            options=available_plugins,
            key="tpl_plugin_id",
            help="Select the plugin this template belongs to",
        )

    with col2:
        template_name = st.text_input(
            "Template Name",
            value="template_final",
            key="tpl_template_name",
            help="Base name for the template file (without extension)",
        )

    # Metadata inputs
    col3, col4 = st.columns(2)
    with col3:
        author = st.text_input(
            "Author",
            value=os.environ.get("TEMPLATE_AUTHOR", ""),
            key="tpl_author",
            help="Your name or identifier",
        )

    with col4:
        change_log = st.text_area(
            "Change Log *",
            key="tpl_change_log",
            help="Describe the changes in this template version (required)",
            height=100,
        )

    # File upload
    uploaded_file = st.file_uploader(
        "Upload DOCX Template",
        type=["docx"],
        key="tpl_uploaded_file",
        help="Upload the new template DOCX file",
    )

    if uploaded_file is not None:
        st.info(f"📄 File: **{uploaded_file.name}** ({uploaded_file.size:,} bytes)")

        # Validate button
        if st.button("🔍 Validate Template", type="primary", use_container_width=True):
            if not change_log or not change_log.strip():
                st.error("❌ Change log is required")
                return

            with st.spinner("Validating template..."):
                _run_validation(plugin_id, uploaded_file)

    # Show validation results if available
    _render_validation_results()


def _run_validation(plugin_id: str, uploaded_file) -> None:
    """Run template validation and store results in session state."""
    import tempfile

    try:
        plugin = load_plugin(plugin_id)
    except Exception as e:
        st.error(f"Failed to load plugin '{plugin_id}': {e}")
        return

    # Save uploaded file to temp location
    file_bytes = uploaded_file.read()
    uploaded_file.seek(0)  # Reset for potential re-read

    with tempfile.NamedTemporaryFile(suffix=".docx", delete=False) as tmp:
        tmp.write(file_bytes)
        tmp_path = tmp.name

    try:
        # Find sample input
        sample_input = str(PROJECT_ROOT / "tests" / "golden" / "sample_input.json")
        if not Path(sample_input).exists():
            sample_input = None

        # Run validation
        result = validate_template(
            template_path=tmp_path,
            plugin=plugin,
            sample_input_path=sample_input,
            check_anchors=True,
        )

        # Store results in session state
        st.session_state.tpl_validation_result = result
        st.session_state.tpl_validation_report = generate_validation_report(result)
        st.session_state.tpl_file_bytes = file_bytes
        st.session_state.tpl_temp_path = tmp_path

    except Exception as e:
        st.error(f"Validation failed with error: {e}")
        try:
            Path(tmp_path).unlink()
        except Exception:
            pass


def _render_validation_results() -> None:
    """Render validation results from session state."""
    result = st.session_state.get("tpl_validation_result")
    if result is None:
        return

    st.markdown("---")
    st.markdown("### Validation Results")

    # Status badge
    if result.status == "PASS":
        st.success(f"✅ **Status: PASS** — Template is valid")
    elif result.status == "WARN":
        st.warning(f"⚠️ **Status: WARN** — Template has warnings")
    else:
        st.error(f"❌ **Status: FAIL** — Template validation failed")

    # Summary metrics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Variables Found", len(result.variables_found))
    with col2:
        st.metric("Errors", len(result.errors))
    with col3:
        st.metric("Warnings", len(result.warnings))
    with col4:
        st.metric("SHA-256", result.sha256[:12] + "...")

    # Detailed issues
    if result.errors:
        with st.expander("❌ Errors", expanded=True):
            for issue in result.errors:
                st.error(f"**[{issue.category}]** {issue.message}")
                if issue.suggestion:
                    st.caption(f"💡 {issue.suggestion}")

    if result.warnings:
        with st.expander("⚠️ Warnings", expanded=True):
            for issue in result.warnings:
                st.warning(f"**[{issue.category}]** {issue.message}")
                if issue.suggestion:
                    st.caption(f"💡 {issue.suggestion}")

    # Info messages
    info_issues = [i for i in result.issues if i.level == "info"]
    if info_issues:
        with st.expander("ℹ️ Info"):
            for issue in info_issues:
                st.info(f"**[{issue.category}]** {issue.message}")

    # Variables detail
    if result.variables_found:
        with st.expander("📋 Template Variables"):
            st.code(", ".join(result.variables_found))

    if result.variables_extra:
        with st.expander("❓ Unmatched Variables"):
            st.code(", ".join(result.variables_extra))

    # Validation report download
    report = st.session_state.get("tpl_validation_report")
    if report:
        st.download_button(
            "📥 Download Validation Report (JSON)",
            data=json.dumps(report, indent=2, ensure_ascii=False),
            file_name="validation_report.json",
            mime="application/json",
        )


# ============================================================================
# Publish Section
# ============================================================================

def render_publish_section() -> None:
    """Render the publish button and handling."""
    result = st.session_state.get("tpl_validation_result")
    if result is None:
        return

    st.markdown("---")
    st.markdown("### 🚀 Publish Template")

    # Check if publishing is allowed
    can_publish = False
    if result.status == "PASS":
        can_publish = True
    elif result.status == "WARN":
        if ALLOW_PUBLISH_WITH_WARNINGS:
            can_publish = True
            st.warning("Publishing with warnings is allowed by configuration.")
        else:
            confirm = st.checkbox(
                "I acknowledge the warnings and want to proceed with publishing",
                key="tpl_confirm_warnings",
            )
            can_publish = confirm
    else:
        st.error("Cannot publish: Template validation FAILED. Fix errors and re-validate.")
        return

    if not can_publish:
        st.info("Check the warnings above and confirm to proceed.")
        return

    # Version bump type
    registry = TemplateRegistry()
    plugin_id = st.session_state.get("tpl_plugin_id", "")
    current_version = registry.get_latest_version(plugin_id)

    col1, col2 = st.columns(2)
    with col1:
        bump_type = st.selectbox(
            "Version Bump",
            options=["patch", "minor", "major"],
            key="tpl_bump_type",
            help="Select the type of version increment",
        )
    with col2:
        next_version = registry.get_next_version(plugin_id, bump_type)
        st.info(f"📌 Current: **{current_version or 'none'}** → Next: **{next_version}**")

    # Power Automate URL check
    has_pa_url = bool(POWER_AUTOMATE_URL)
    if not has_pa_url:
        st.warning(
            "⚠️ POWER_AUTOMATE_TEMPLATE_PUBLISH_URL is not configured. "
            "Publishing will save locally only (no SharePoint upload)."
        )

    # Publish button
    if st.button("🚀 Publish", type="primary", use_container_width=True):
        _execute_publish(plugin_id, next_version, has_pa_url)


def _execute_publish(plugin_id: str, version: str, has_pa_url: bool) -> None:
    """Execute the publish operation."""
    with st.spinner("Publishing template..."):
        result = st.session_state.get("tpl_validation_result")
        report = st.session_state.get("tpl_validation_report")
        file_bytes = st.session_state.get("tpl_file_bytes")
        template_name = st.session_state.get("tpl_template_name", "template_final")
        author = st.session_state.get("tpl_author", "unknown")
        change_log = st.session_state.get("tpl_change_log", "")

        if not file_bytes:
            st.error("No template file found. Please upload and validate again.")
            return

        # Build metadata
        metadata = build_metadata(
            plugin_id=plugin_id,
            template_name=template_name,
            version=version,
            author=author,
            change_log=change_log,
            sha256=result.sha256,
            variables=result.variables_found,
            validation_status=result.status,
            validation_errors=[e.message for e in result.errors],
            validation_warnings=[w.message for w in result.warnings],
            previous_version=TemplateRegistry().get_latest_version(plugin_id),
        )

        # Attempt SharePoint publish
        sp_url = None
        sp_metadata_url = None
        sp_validation_url = None

        if has_pa_url:
            try:
                sp_response = publish_to_sharepoint(
                    plugin_id=plugin_id,
                    template_name=template_name,
                    version=version,
                    template_bytes=file_bytes,
                    metadata_json=metadata,
                    validation_report_json=report,
                )

                if sp_response.ok:
                    sp_url = sp_response.template_file_url
                    sp_metadata_url = sp_response.metadata_file_url
                    sp_validation_url = sp_response.validation_file_url
                    st.success("✅ Published to SharePoint successfully!")
                else:
                    st.warning(
                        f"⚠️ SharePoint upload failed: {sp_response.error_message}\n\n"
                        f"Template will be saved locally only."
                    )
            except ValueError as e:
                st.warning(f"⚠️ {e}")
            except Exception as e:
                st.warning(f"⚠️ SharePoint publish error: {e}")

        # Save to local registry
        registry = TemplateRegistry()
        tv = registry.publish(
            plugin_id=plugin_id,
            template_name=template_name,
            version=version,
            author=author,
            change_log=change_log,
            sha256=result.sha256,
            variables=result.variables_found,
            validation_status=result.status,
            validation_errors=[e.message for e in result.errors],
            validation_warnings=[w.message for w in result.warnings],
            template_bytes=file_bytes,
            sharepoint_url=sp_url,
            sharepoint_metadata_url=sp_metadata_url,
            sharepoint_validation_url=sp_validation_url,
        )

        # Display success
        st.success(f"🎉 Template **v{version}** published successfully!")

        # Show publish details
        with st.expander("📋 Publish Details", expanded=True):
            col1, col2 = st.columns(2)
            with col1:
                st.markdown(f"**Plugin:** {plugin_id}")
                st.markdown(f"**Version:** {version}")
                st.markdown(f"**Author:** {author}")
                st.markdown(f"**SHA-256:** `{result.sha256[:16]}...`")
            with col2:
                st.markdown(f"**Template:** {template_name}")
                st.markdown(f"**Cache:** `{tv.cache_path}`")
                if sp_url:
                    st.markdown(f"**SharePoint:** [Open]({sp_url})")
                else:
                    st.markdown("**SharePoint:** Not uploaded")

        # Clean temp file
        tmp_path = st.session_state.get("tpl_temp_path")
        if tmp_path:
            try:
                Path(tmp_path).unlink()
            except Exception:
                pass

        # Clear validation state
        for key in ["tpl_validation_result", "tpl_validation_report",
                     "tpl_file_bytes", "tpl_temp_path"]:
            if key in st.session_state:
                del st.session_state[key]


# ============================================================================
# Version History & Rollback Section
# ============================================================================

def render_version_history() -> None:
    """Render version history and rollback UI."""
    st.markdown("## 📜 Version History & Rollback")

    available_plugins = list_plugins()
    if not available_plugins:
        st.warning("No plugins found")
        return

    plugin_id = st.selectbox(
        "Select Plugin",
        options=available_plugins,
        key="tpl_history_plugin_id",
    )

    registry = TemplateRegistry()
    versions = registry.list_versions(plugin_id)
    active_version = registry.get_active_version(plugin_id)

    if not versions:
        st.info("No template versions published yet for this plugin.")
        return

    st.markdown(f"**Active Version:** `{active_version or 'none (using default)'}`")
    st.markdown(f"**Total Versions:** {len(versions)}")

    # Version table
    for tv in versions:
        is_active = tv.version == active_version
        status_badge = "🟢" if is_active else "⚪"
        validation_badge = {
            "PASS": "✅", "WARN": "⚠️", "FAIL": "❌"
        }.get(tv.validation_status, "❓")

        with st.expander(
            f"{status_badge} v{tv.version} — {tv.created_at[:10]} "
            f"by {tv.author} {validation_badge}",
            expanded=is_active,
        ):
            col1, col2 = st.columns(2)
            with col1:
                st.markdown(f"**Version:** {tv.version}")
                st.markdown(f"**Author:** {tv.author}")
                st.markdown(f"**Created:** {tv.created_at}")
                st.markdown(f"**Template:** {tv.template_name}")
            with col2:
                st.markdown(f"**Validation:** {tv.validation_status}")
                st.markdown(f"**SHA-256:** `{tv.sha256[:16]}...`")
                if tv.sharepoint_url:
                    st.markdown(f"**SharePoint:** [Open]({tv.sharepoint_url})")
                if tv.cache_path:
                    st.markdown(f"**Cache:** `{tv.cache_path}`")

            st.markdown(f"**Change Log:** {tv.change_log}")

            if tv.validation_errors:
                st.error("Errors: " + "; ".join(tv.validation_errors[:3]))
            if tv.validation_warnings:
                st.warning("Warnings: " + "; ".join(tv.validation_warnings[:3]))

            # Rollback button (only for non-active versions)
            if not is_active:
                if st.button(
                    f"🔄 Rollback to v{tv.version}",
                    key=f"rollback_{plugin_id}_{tv.version}",
                ):
                    _execute_rollback(plugin_id, tv.version)


def _execute_rollback(plugin_id: str, target_version: str) -> None:
    """Execute a rollback to a specific version."""
    registry = TemplateRegistry()

    # Check that cached template exists
    cache_path = registry.get_cached_template_path(plugin_id, target_version)
    if not cache_path:
        st.error(
            f"Cannot rollback: cached template for v{target_version} not found. "
            "The template file may have been removed."
        )
        return

    # Perform rollback
    tv = registry.rollback(plugin_id, target_version)
    if tv:
        st.success(f"✅ Rolled back to **v{target_version}** successfully!")
        st.info(
            f"New active template: {tv.template_name} v{tv.version}\n\n"
            f"Cache: `{tv.cache_path}`"
        )
        st.rerun()
    else:
        st.error(f"Rollback failed: version {target_version} not found in registry")


# ============================================================================
# Main Page Renderer
# ============================================================================

def render_template_admin() -> None:
    """Main entry point for the Template Admin page."""
    st.title("⚙️ Template Admin")
    st.caption("Upload, validate, publish, and rollback DOCX templates")

    # Authentication gate
    if not check_admin_auth():
        render_login()
        return

    # Show logout button in sidebar
    with st.sidebar:
        st.divider()
        st.markdown("### 🔧 Admin Mode")
        st.success("Authenticated as admin")
        render_logout()

    # Main content
    tab1, tab2 = st.tabs(["📤 Upload & Publish", "📜 Version History"])

    with tab1:
        render_upload_section()
        render_publish_section()

    with tab2:
        render_version_history()
