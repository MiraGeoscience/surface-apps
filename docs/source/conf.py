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

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.autosummary",
    "sphinx.ext.intersphinx",
    "sphinx.ext.viewcode",
    "sphinx_issues",
    "sphinxcontrib.googleanalytics",
]

intersphinx_mapping = {
    "geoh5py": ("https://mirageoscience-geoh5py.readthedocs-hosted.com/en/stable/", None),
    "numpy": ("https://numpy.org/doc/stable/", None),
    "pydantic": ("https://docs.pydantic.dev/latest/", None),
    "python": ("https://docs.python.org/3.14/", None),
}
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


def resolve_external_type(app, env, node, contnode):
    from docutils import nodes

    if node.get("refdomain") != "py":
        return None

    source_links = {
        "annotated_types.Gt": "https://github.com/annotated-types/annotated-types/blob/main/annotated_types/__init__.py",
        "geoapps_utils.base.Driver": "https://github.com/MiraGeoscience/geoapps-utils/blob/release/ga-4.9/geoapps_utils/base.py#L53",
        "geoapps_utils.base.Options": "https://github.com/MiraGeoscience/geoapps-utils/blob/release/ga-4.9/geoapps_utils/base.py#L227",
    }
    target = node.get("reftarget")
    if target in source_links:
        return nodes.reference("", "", contnode, refuri=source_links[target])

    aliases = {
        "Path": "pathlib.Path",
        "UIJsonGroup": "geoh5py.groups.uijson.UIJsonGroup",
        "Data": "geoh5py.data.data.Data",
        "Surface": "geoh5py.objects.surface.Surface",
        "Points": "geoh5py.objects.points.Points",
        "CellObject": "geoh5py.objects.cell_object.CellObject",
        "GridObject": "geoh5py.objects.grid_object.GridObject",
    }
    if target in aliases:
        node["reftarget"] = aliases[target]
    return None


def setup(app):
    app.connect("missing-reference", resolve_external_type, priority=400)
