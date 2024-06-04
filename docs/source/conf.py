import sys
import os
import datetime
from importlib import metadata

from ophyd import Component, EpicsSignal, EpicsSignalRO

# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

sys.path.insert(0, os.path.abspath("../.."))

year = datetime.date.today().year
authors = metadata.metadata("sophys-common")["Author-email"]
name = metadata.metadata("sophys-common")["Name"]
version = metadata.version("sophys-common")

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
    "sphinx_design",
    "sphinx_remove_toctrees",
    "sphinx_rtd_theme",
    "sphinx_tags",
]

# HACK: This patches the sphinx_remove_toctrees setup function, so that the 'remove_from_toctrees' key
# is not added twice (sphinx_tags also uses it, for some god-forsaken reason).

# fmt: off
import sphinx_remove_toctrees  # noqa

def __patched_setup(app):  # noqa
    app.add_config_value("remove_toctrees_from", [], "html")
    app.connect("env-updated", sphinx_remove_toctrees.remove_toctrees)
    return {"parallel_read_safe": True, "parallel_write_safe": True}

sphinx_remove_toctrees.setup = __patched_setup  # noqa
# fmt: on


templates_path = ["_templates"]
exclude_patterns = []

remove_from_toctrees = ["_generated/*"]

tags_intro_text = "Type:"
tags_create_badges = True
tags_badge_colors = {
    "AreaDetector": "info",
    "Motor": "info",
}


def custom_docstring_process(app, what, name, obj, options, lines):
    def pretty_print_component(obj: Component):
        name = f"**{obj.cls.__name__}**"
        kind = f"*Kind.{getattr(obj.kind, 'name')}*"

        _mro = obj.cls.mro()
        if (EpicsSignal in _mro) and (EpicsSignalRO not in _mro):
            _r = obj.kwargs.get("read_pv", obj.suffix)
            _w = obj.kwargs.get("write_pv", obj.suffix)
            if _r != _w:
                return f"{name} --- Read = {_r} | Write = {_w} | {kind}"
        return (
            f"{name} --- Suffix = *{(obj.suffix or 'None').replace(':', '')}* | {kind}"
        )

    if what == "attribute" and isinstance(obj, Component):
        if len(lines) == 0:
            lines.append(pretty_print_component(obj))
        else:
            lines[0] = pretty_print_component(obj)


def custom_skip_member(app, what, name, obj, skip, options):
    # https://www.sphinx-doc.org/en/master/usage/extensions/autodoc.html#event-autodoc-skip-member
    if what in ("attribute", "property"):
        if not isinstance(obj, Component):
            return True
    return skip


def setup(app):
    app.connect("autodoc-process-docstring", custom_docstring_process, priority=-1)
    app.connect("autodoc-skip-member", custom_skip_member, priority=-1)


# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = "sphinx_rtd_theme"
html_static_path = ["_static"]
html_css_files = ["css/custom_theming.css"]
