# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

import sys
from pathlib import Path

from datetime import datetime
from importlib.metadata import version

from packaging.version import Version


sys.path.insert(0, Path("../..").resolve())

project = "surface-apps"
author = "Mira Geoscience Ltd."
project_copyright = "%Y, Mira Geoscience Ltd"
copyright = "Mira Geoscience Ltd"

# The full version, including alpha/beta/rc tags.
release = version("plate-simulation")
# The shorter X.Y.Z version.
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
extensions = ["sphinx.ext.autodoc"]

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
