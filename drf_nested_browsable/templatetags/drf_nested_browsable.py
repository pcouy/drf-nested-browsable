"""
Provide utility template tags for rendering nested serializers
"""
from django import template as tpl
from rest_framework.renderers import HTMLFormRenderer
from rest_framework.serializers import ListSerializer, Serializer

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


def write_only_serializer_class(serializer):
    new_fields = {}
    for field_name, field in serializer.fields.items():
        if not field.read_only:
            if isinstance(field, Serializer):
                field.__class__ = write_only_serializer_class(field)
            elif isinstance(field, ListSerializer):
                field.child.__class__ = write_only_serializer_class(field.child)
            new_fields.update({field_name: field})

    class NewSer(serializer.__class__):
        class Meta(serializer.__class__.Meta):
            fields = list(new_fields.keys())

    new_declared_fields = {}
    for field_name in NewSer._declared_fields.keys():
        new_field = new_fields.get(field_name, None)
        if new_field is not None:
            new_declared_fields.update({field_name: new_field})
    NewSer._declared_fields = new_declared_fields

    NewSer.__name__ = serializer.__class__.__name__
    return NewSer


@register.simple_tag
def render_nested(serializer, data=None, prefix=""):
    serializer_with_data = write_only_serializer_class(serializer)(
        data=data, context=serializer.context
    )
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
