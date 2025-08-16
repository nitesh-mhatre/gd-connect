# gd_connect/auth.py
# Auth helper for gd-connect
# - Uses OAuth loopback (localhost) flow (Google's recommended method)
# - Saves/loads user token from token.json
# - Desktop: opens browser normally
# - Headless: falls back to not opening a browser (prints URL); you must complete
#             the flow with a browser that can reach THIS machine's localhost port
#             (via SSH port-forward), or generate token.json on a desktop and copy it.

from __future__ import annotations

import os
from typing import Optional, Sequence

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow

DEFAULT_SCOPES = ["https://www.googleapis.com/auth/drive"]


def _load_token(token_path: str, scopes: Sequence[str]) -> Optional[Credentials]:
    if os.path.exists(token_path):
        try:
            return Credentials.from_authorized_user_file(token_path, scopes)
        except Exception:
            # Corrupt or incompatible token file; ignore and re-auth
            return None
    return None


def _save_token(creds: Credentials, token_path: str) -> None:
    # Ensure directory exists if token_path includes folders
    os.makedirs(os.path.dirname(token_path) or ".", exist_ok=True)
    with open(token_path, "w") as f:
        f.write(creds.to_json())


def get_credentials(
    cred_path: str = None,
    token_path: str = None,
    scopes: Sequence[str] = None,
    port: Optional[int] = None,
    prefer_console: bool = False,
) -> Credentials:
    """
    Return valid user credentials for Google Drive.

    Args:
        cred_path: Path to OAuth client secrets (Desktop) JSON.
                   Defaults to env GD_CONNECT_CREDENTIALS or ./credentials.json
        token_path: Path to persist the user token JSON.
                    Defaults to env GD_CONNECT_TOKEN or ./token.json
        scopes: List of OAuth scopes (defaults to Drive full access).
        port: Port for the local loopback server (0 chooses a random free port).
              Defaults to env GD_CONNECT_PORT or 0.
        prefer_console: If True, do not attempt to open a browser (still loopback).
                        Useful on servers; you must ensure a browser can reach
                        this machine's localhost port (e.g., via SSH port-forward).

    Returns:
        google.oauth2.credentials.Credentials
    """
    cred_path = cred_path or os.environ.get("GD_CONNECT_CREDENTIALS", "credentials.json")
    token_path = token_path or os.environ.get("GD_CONNECT_TOKEN", "token.json")
    scopes = list(scopes or DEFAULT_SCOPES)
    port = port if port is not None else int(os.environ.get("GD_CONNECT_PORT", "0"))

    # Try existing token first
    creds = _load_token(token_path, scopes)
    if creds and creds.valid:
        return creds
    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
        _save_token(creds, token_path)
        return creds

    # Need interactive auth
    if not os.path.exists(cred_path):
        raise FileNotFoundError(
            f"credentials.json not found at '{cred_path}'. "
            "Create an OAuth Client ID (Desktop) in Google Cloud Console and download it."
        )

    flow = InstalledAppFlow.from_client_secrets_file(cred_path, scopes)

    # First try to open the browser (desktop); if that fails, fall back to no-browser mode
    try:
        creds = flow.run_local_server(port=port, open_browser=not prefer_console)
    except Exception:
        # Final attempt: do not open a browser; print URL and wait for redirect
        print("⚠️ Browser launch failed; printing the auth URL.")
        print("   Note: the redirect must reach THIS machine's localhost port.")
        print("   If you're remote, use SSH port-forwarding, e.g.:")
        print("     ssh -L 8765:127.0.0.1:8765 <user>@<server>")
        print("   and run get_credentials(port=8765, prefer_console=True)")
        creds = flow.run_local_server(port=port, open_browser=False)

    _save_token(creds, token_path)
    return creds
