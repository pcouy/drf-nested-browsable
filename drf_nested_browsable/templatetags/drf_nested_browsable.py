"""
Provide utility template tags for rendering nested serializers
"""
from django import template as tpl
from rest_framework.renderers import HTMLFormRenderer
from rest_framework.serializers import ListSerializer, Serializer

register = tpl.Library()


class NestedHTMLFormRenderer(HTMLFormRenderer):
    """Custom renderer that manages field prefixes"""

    def __init__(self, *args, **kwargs):
        self._prefix = kwargs.pop("prefix", "")
        super().__init__(*args, **kwargs)

    def render_field(self, field, parent_style):
        field._prefix = self._prefix  # pylint: disable=protected-access
        return super().render_field(field, parent_style)


@register.filter
def get_value(data, key):
    """Wrapper filter to access dict value from a key in templates"""
    return data.get(key)


@register.filter
def addstr(a_1, a_2):
    """Wrapper filter to concatenate strings in templates"""
    return str(a_1) + str(a_2)


@register.filter
def fieldname_to_placeholder(fieldname):
    """
    Filter that makes a variable-length placeholder based on the current
    nesting depth :
    Placeholders are made of a pair of curly braces containing a variable
    number of the letter "i".

    These placeholders are inserted in new element templates, which are used in
    the JS from `writable_list.html` : when converting a nested form template to
    a new list item, the JS will (in the following order) :

    - Turn any occurence of `{i}` into an appropriate index number
    - Turn any occurence of `{ii` into `{i`
    """
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
    return "{" + ("i" * depth) + "}"


def render_form(serializer, template_pack=None, prefix=""):
    """
    Very similar to DRF's `render_form` tag with prefix management added
    """
    style = {"template_pack": template_pack} if template_pack else {}
    renderer = NestedHTMLFormRenderer(prefix=prefix)
    return renderer.render(serializer.data, None, {"style": style})


def _write_only_serializer_class(serializer):
    # pylint: disable=protected-access
    new_fields = {}
    for field_name, field in serializer.fields.items():
        if not field.read_only:
            if isinstance(field, Serializer):
                field.__class__ = _write_only_serializer_class(field)
            elif isinstance(field, ListSerializer):
                field.child.__class__ = _write_only_serializer_class(field.child)
            new_fields.update({field_name: field})

    class _NewSer(serializer.__class__):
        class Meta(serializer.__class__.Meta):
            fields = list(new_fields.keys())

    new_declared_fields = {}
    for field_name in _NewSer._declared_fields:
        new_field = new_fields.get(field_name, None)
        if new_field is not None:
            new_declared_fields.update({field_name: new_field})
    _NewSer._declared_fields = new_declared_fields

    _NewSer.__name__ = serializer.__class__.__name__
    return _NewSer


@register.simple_tag
def render_nested(serializer, data=None, prefix=""):
    """
    Tag used in the `writable_list.html` template to render nested list items.
    This will instanciate a serializer with data and call a variation of the
    stock DRF `render_form` that manages nested serializer prefixes
    The prefix represents the nesting path.
    """
    serializer_with_data = _write_only_serializer_class(serializer)(
        data=data, context=serializer.context
    )
    serializer_with_data.is_valid()
    rendered_form = render_form(
        serializer_with_data, template_pack="rest_framework/horizontal", prefix=prefix
    )
    return rendered_form


@register.filter
def to_dict(data):
    """Wrapper filter to provide `dir` built-in in templates"""
    return dir(data)


@register.filter
def typeof(data):
    """Wrapper filter to provide `type` built-in in templates"""
    return type(data)
