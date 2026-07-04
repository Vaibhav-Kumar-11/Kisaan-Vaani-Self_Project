"""Secret loading shared by every pipeline module.

Reads from env vars first (used by tests and local scripts), then falls
back to st.secrets (used on Streamlit Community Cloud). Keeping this in
one place means pipeline modules never import streamlit directly, which
keeps them importable/testable without a Streamlit runtime.
"""
import os


def get_secret(key: str, default: str | None = None) -> str | None:
    if key in os.environ:
        return os.environ[key]

    try:
        import streamlit as st
        return st.secrets[key]
    except Exception:
        return default


def require_secret(key: str) -> str:
    value = get_secret(key)
    if not value:
        raise RuntimeError(
            f"Missing required secret '{key}'. Set it as an environment "
            f"variable locally, or in Streamlit Cloud's app secrets."
        )
    return value
