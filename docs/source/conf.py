# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

import os
from datetime import datetime
from importlib.metadata import version as get_version

from packaging.version import Version


project = "surface-apps"
author = "Mira Geoscience Ltd."
project_copyright = "%Y, Mira Geoscience Ltd"
copyright = "Mira Geoscience Ltd"

# The public version, including alpha/beta/rc tags.
full_version = Version(get_version("surface-apps"))
release = full_version.public
if full_version.is_postrelease:
    release = release.rsplit(".post", 1)[0]

# The short X.Y.Z version.
version = full_version.base_version

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

autodoc_mock_imports = [
    "numpy",
    "geoh5py",
    "scipy",
    "skimage",
    "geoapps_utils",
    "pydantic",
    "tqdm",
]
extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.autosummary",
    "sphinx.ext.intersphinx",
    "sphinx.ext.todo",
    "sphinx.ext.viewcode",
    "sphinx_issues",
    "sphinxcontrib.googleanalytics",
]

intersphinx_mapping = {
    "numpy": ("https://numpy.org/doc/stable/", None),
    "python": ("https://docs.python.org/3.14/", None),
}
todo_include_todos = True
googleanalytics_id = os.environ.get("GOOGLE_ANALYTICS_ID", "")
googleanalytics_enabled = bool(googleanalytics_id)
issues_github_path = "MiraGeoscience/surface-apps"

templates_path = ["_templates"]
exclude_patterns = []


# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output
html_theme = "alabaster"
html_theme_options = {
    "description": f"version {release}",
}
html_static_path = []


def get_copyright_notice():
    return f"Copyright {datetime.now().strftime(project_copyright)}"


rst_epilog = f"""
.. |copyright_notice| replace:: {get_copyright_notice()}.
"""
