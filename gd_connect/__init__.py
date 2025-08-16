# gd_connect/__init__.py
from .auth import get_credentials
from .drive import GoogleDrive

__all__ = ["get_credentials", "GoogleDrive"]
__version__ = "0.1.0"