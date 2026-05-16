"""
layout.py — Shared page chrome (sidebar branding) for every page.
"""

import streamlit as st


def render_sidebar() -> None:
    """Render the dark branded sidebar with the auto page-nav hidden."""

    # Hide Streamlit's page-nav and the second sidebar column using
    # MaxBoundsAndStyle — belt-and-suspenders. We also use JavaScript
    # to physically remove the nav DOM element, since CSS isn't catching it.
    st.markdown(
        """
        <style>
        section[data-testid="stSidebar"] {
            background: #0A0A0A !important;
        }
        section[data-testid="stSidebar"] * {
            color: #F4F1EA !important;
        }
        [data-testid="stSidebarNav"],
        [data-testid="stSidebarNavItems"],
        [data-testid="stSidebarNavSeparator"],
        [data-testid="stSidebarNavLink"],
        section[data-testid="stSidebar"] nav,
        section[data-testid="stSidebar"] ul {
            display: none !important;
        }
        </style>

        <script>
        // Physically remove the nav element on every render
        const killNav = () => {
            const sels = [
                '[data-testid="stSidebarNav"]',
                '[data-testid="stSidebarNavItems"]',
                '[data-testid="stSidebarNavSeparator"]',
                '[data-testid="stSidebarNavLink"]',
            ];
            sels.forEach(s => document.querySelectorAll(s).forEach(el => el.remove()));
        };
        killNav();
        // Streamlit re-renders, so keep killing it
        const observer = new MutationObserver(killNav);
        observer.observe(document.body, { childList: true, subtree: true });
        </script>
        """,
        unsafe_allow_html=True,
    )

    with st.sidebar:
        st.markdown(
            """
            <div style="padding: 8px 0 18px; display: flex; align-items: center; gap: 10px;">
                <div style="width: 10px; height: 10px; background: #C6FF3D; border: 1.5px solid #F4F1EA;"></div>
                <span style="font-family: monospace; font-size: 10px; letter-spacing: 0.18em; text-transform: uppercase;">Road Safety / Atlas</span>
            </div>
            """,
            unsafe_allow_html=True,
        )