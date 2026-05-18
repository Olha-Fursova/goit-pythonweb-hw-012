"""
Sphinx configuration file for the Contacts REST API documentation.
"""
 
import os
import sys

sys.path.insert(0, os.path.abspath("../.."))

autodoc_mock_imports = ["fastapi", "sqlalchemy", "redis", "cloudinary", "fastapi_mail", "slowapi", "jose", "passlib"]

project = 'Contacts REST API'
copyright = '2026, Olha Fursova'
author = 'Olha Fursova'
release = '0.1.0'

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
    "sphinx.ext.viewcode",
]

autodoc_default_options = {
    "members": True,
    "undoc-members": False,
    "show-inheritance": True,
}

html_theme = "alabaster"
html_static_path = ["_static"]
templates_path = ["_templates"]
exclude_patterns = []