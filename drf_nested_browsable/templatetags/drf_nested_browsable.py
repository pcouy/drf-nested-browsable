"""
Provide utility template tags for rendering nested serializers
"""
from django import template as tpl
from rest_framework.renderers import HTMLFormRenderer

register = tpl.Library()


class NestedHTMLFormRenderer(HTMLFormRenderer):
    def __init__(self, *args, **kwargs):
        self._prefix = kwargs.pop("prefix", "")
        super().__init__(*args, **kwargs)

    def render_field(self, field, parent_style):
        field._prefix = self._prefix
        return super().render_field(field, parent_style)


@register.filter
def get_value(data, key):
    return data.get(key)


@register.filter
def addstr(a1, a2):
    return str(a1) + str(a2)


@register.filter
def fieldname_to_placeholder(fieldname):
    depth = 1
    last_matched_char = None
    for char in fieldname:
        if last_matched_char is None and char == "{":
            last_matched_char = char
        elif last_matched_char in ["{", "i"] and char == "i":
            last_matched_char = char
        elif last_matched_char == "i" and char == "}":
            last_matched_char = None
            depth += 1
    return "{" + ('i'*depth) + "}"



def render_form(serializer, template_pack=None, prefix=""):
    style = {"template_pack": template_pack} if template_pack else {}
    renderer = NestedHTMLFormRenderer(prefix=prefix)
    return renderer.render(serializer.data, None, {"style": style})


@register.simple_tag
def render_nested(serializer, data=None, prefix=""):
    serializer_with_data = type(serializer)(data=data)
    serializer_with_data.is_valid()
    rendered_form = render_form(
        serializer_with_data, template_pack="rest_framework/horizontal", prefix=prefix
    )
    return rendered_form


@register.filter
def to_dict(data):
    return dir(data)


@register.filter
def typeof(data):
    return type(data)
