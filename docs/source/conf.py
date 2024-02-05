import sys
import os
import datetime
from importlib import metadata

from ophyd import Component

# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

sys.path.insert(0, os.path.abspath("../.."))

year = datetime.date.today().year
authors = metadata.metadata("common-sophys")["Author-email"]
name = metadata.metadata("common-sophys")["Name"]
version = metadata.version("common-sophys")

project = name
copyright = f"{year}, SwC/LNLS"
release = version

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.autosummary",
    "sphinx.ext.viewcode",
    "sphinx.ext.napoleon",
    "sphinx_rtd_theme",
    "sphinx_remove_toctrees",
]

templates_path = ["_templates"]
exclude_patterns = []

remove_from_toctrees = ["_generated/*"]


def custom_docstring_process(app, what, name, obj, options, lines):
    def pretty_print_component(obj: Component):
        return "**{0}** --- Suffix = *{1}* | *{2}*".format(
            obj.cls.__name__, (obj.suffix or "None").replace(":", ""), str(obj.kind)
        )

    if what == "attribute" and isinstance(obj, Component):
        if len(lines) == 0:
            lines.append(pretty_print_component(obj))
        else:
            lines[0] = pretty_print_component(obj)


def setup(app):
    app.connect("autodoc-process-docstring", custom_docstring_process, priority=-1)


# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = "sphinx_rtd_theme"
html_static_path = ["_static"]
html_css_files = ["css/custom_theming.css"]
