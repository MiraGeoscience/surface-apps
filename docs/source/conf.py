# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

import os
from datetime import datetime
from importlib.metadata import version

from packaging.version import Version


project = "surface-apps"
author = "Mira Geoscience Ltd."
project_copyright = "%Y, Mira Geoscience Ltd"
copyright = "Mira Geoscience Ltd"

# The full version, including alpha/beta/rc tags.
release = version("surface-apps")
# The shorter X.Y.Z version.
pep_version = Version(release)
if pep_version.is_postrelease:
    release = pep_version.base_version

# The short X.Y.Z version.
version = Version(release).base_version

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
