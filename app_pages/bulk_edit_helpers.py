"""Bulk edit helpers for config tables.

Provides Excel/CSV upload, download, and paste-from-clipboard utilities
to make editing large config tables faster. Works with any st.data_editor.
"""

import io
from typing import Optional

import pandas as pd
import streamlit as st


def render_bulk_edit_bar(
    table_key: str,
    current_df: pd.DataFrame,
    label: str = "table",
) -> Optional[pd.DataFrame]:
    """Render upload/download/paste controls above a data editor.

    Call this BEFORE the st.data_editor. If it returns a DataFrame,
    use that instead of the current one (user uploaded/pasted new data).

    Args:
        table_key: Unique key prefix for widgets
        current_df: The current DataFrame being edited
        label: Human-readable table name for UI labels

    Returns:
        Replacement DataFrame if user uploaded/pasted, else None
    """
    replacement_df = None

    with st.expander(f"Bulk edit: upload, download, or paste for {label}", expanded=False):
        st.caption(
            "**Tip:** You can also select cells in the table below and press "
            "**Ctrl+V** to paste directly from Excel/Google Sheets."
        )

        col_dl, col_ul, col_paste = st.columns(3)

        # Download current table as CSV
        with col_dl:
            csv_data = current_df.to_csv(index=False)
            st.download_button(
                "Download CSV",
                data=csv_data,
                file_name=f"{table_key}.csv",
                mime="text/csv",
                use_container_width=True,
                key=f"bulk_dl_{table_key}",
            )

        # Upload CSV or Excel
        with col_ul:
            uploaded = st.file_uploader(
                "Upload CSV/Excel",
                type=["csv", "xlsx", "xls"],
                key=f"bulk_ul_{table_key}",
                label_visibility="collapsed",
            )
            if uploaded is not None:
                try:
                    if uploaded.name.endswith((".xlsx", ".xls")):
                        replacement_df = pd.read_excel(uploaded)
                    else:
                        replacement_df = pd.read_csv(uploaded)
                    st.success(f"Loaded {len(replacement_df)} rows from {uploaded.name}")
                except Exception as e:
                    st.error(f"Failed to parse file: {e}")

        # Paste from clipboard (tab-separated)
        with col_paste:
            pasted = st.text_area(
                "Paste from Excel (tab-separated)",
                height=100,
                key=f"bulk_paste_{table_key}",
                label_visibility="collapsed",
                placeholder="Paste tab-separated data here (with headers)...",
            )
            if pasted and pasted.strip():
                try:
                    replacement_df = pd.read_csv(io.StringIO(pasted), sep="\t")
                    st.success(f"Parsed {len(replacement_df)} rows from pasted data")
                except Exception as e:
                    st.error(f"Failed to parse pasted data: {e}")

    return replacement_df
