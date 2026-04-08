"""Jinja2-based template renderer for NASA UFO mission summaries."""

from __future__ import annotations

from jinja2 import Environment, PackageLoader, select_autoescape


_env = Environment(
    loader=PackageLoader("nasa_ufo", "templates"),
    autoescape=select_autoescape(default=False),
    trim_blocks=True,
    lstrip_blocks=True,
)


def render(template_name: str, **context: object) -> str:
    """Render a named template with the given context variables.

    Args:
        template_name: Filename of the template inside ``nasa_ufo/templates/``.
        **context: Variables passed into the template.

    Returns:
        Rendered string with trailing whitespace stripped.
    """
    template = _env.get_template(template_name)
    return template.render(**context).rstrip()
