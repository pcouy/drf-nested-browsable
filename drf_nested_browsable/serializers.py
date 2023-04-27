"""
Provides abstract writable nested serializers for Django Rest Framework

These serializers require some additionnal configuration, that is done through the Meta
class of the concrete classes
"""
from rest_framework.serializers import ListSerializer, ModelSerializer


class WritableNestedListSerializer(ListSerializer):
    """
    Can be set as the `list_serializer_class` for any serializer. This will make the
    `many=True` version of the serializer writable and render an appropriate browsable
    API form.

    ```python
    class InnerSerializer(ModelSerializer):
        class Meta:
            model = InnerModel
            fields = ["key", "value", "inner_parent"]
            list_serializer_class = WritableNestedListSerializer
            update_keys = "key"
    ```

    You must use `InnerSerializer(many=True, ...)` either as the root serializer for a
    `ListAPIView` or as a field of a `WritableNestedModelSerializer`.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._parent_instance = None
        self._parent_field_name = None

        self.style.update({"template": "writable_list.html"})

        if (
            "update_keys" not in dir(self.child.Meta)
            or self.child.Meta.update_keys is None
        ):
            raise ValueError(
                "You must define `Meta.update_keys` when using "
                "`WritableNestedListSerializer`"
            )

    def _set_parent_field_name(self):
        if not isinstance(self.parent, WritableNestedModelSerializer):
            raise ValueError(
                "You must use `WritableNestedListSerializer` as a field of a"
                "`WritableNestedModelSerializer`"
            )

        self._parent_field_name = self.parent.Meta.model_related_name

    @property
    def parent_data(self):
        """
        Provides the data from the parent serializer. You must call
        `WritableNestedListSerializer.set_parent_instance(instance)`
        before accessing this property.
        """
        self._set_parent_field_name()
        if "_parent_instance" not in dir(self) or self._parent_instance is None:
            raise AttributeError(
                "You must call"
                "`WritableNestedListSerializer.set_parent_instance(instance)`"
                "before accessing `WritableNestedListSerializer.parent_data`"
            )

        return {self._parent_field_name: self._parent_instance}

    def set_parent_instance(self, parent_instance):
        """
        Must be called before acessing the `parent_data` property
        """
        self._parent_instance = parent_instance

    def create(self, validated_data):
        return super().create([{**elem, **self.parent_data} for elem in validated_data])

    def update(
        self,
        instance,
        validated_data,
    ):
        keys = self.child.Meta.update_keys
        if isinstance(keys, str):
            keys = [keys]

        try:
            partial = self.context.get("view").action == "partial_update"
        except (KeyError, AttributeError):
            partial = True

        updated_ids = []

        if not (partial and validated_data is None):
            for new_elem in validated_data:
                full_elem = {**new_elem, **self.parent_data}

                try:
                    elem = instance.get(
                        **{
                            key: new_elem[key] for key in keys if key in new_elem.keys()
                        },
                        **self.parent_data,
                    )
                    elem = self.child.update(elem, full_elem)
                except instance.model.DoesNotExist:
                    elem = self.child.create(full_elem)
                updated_ids.append(elem.id)

            instance.exclude(id__in=updated_ids).delete()


class WritableNestedModelSerializer(ModelSerializer):
    """
    Abstract class for making model serializers that can write to nested models

    ```python
    class OuterSerializer(WritableNestedModelSerializer):
        middle_children = MiddleSerializer(many=True, required=False, default=[])

        class Meta:
            model = OuterModel
            model_related_name = "middle_parent"
            fields = ["key", "value", "middle_children"]
    ```

    When using this as a base serializer, you must define `Meta.model_related_name`,
    which is the child model field name for the relationship to the parent.
    """

    class Meta:
        model_related_name = None

    def __init__(self, *args, **kwargs):
        if (
            "model_related_name" not in dir(self.Meta)
            or self.Meta.model_related_name is None
        ):
            raise ValueError(
                "You must define `model_related_name` when you inherit from"
                "`WritableNestedModelSerializer`"
            )

        for field in self._declared_fields.values():  # pylint: disable=no-member
            if (
                isinstance(field, WritableNestedListSerializer)
                and self.Meta.model_related_name in field.child.fields.keys()
            ):
                self.alter_nested_child(field)

        super().__init__(*args, **kwargs)

    def alter_nested_child(self, field):
        """
        Removes fields representing the current serializer from nested child
        serializers (if it exists).

        This uses `Meta.model_related_name`
        """
        new_fields = []
        for old_field in field.child.__class__.Meta.fields:
            if old_field != self.Meta.model_related_name:
                new_fields.append(old_field)

        class _NewChild(field.child.__class__):
            class Meta(field.child.__class__.Meta):
                fields = new_fields

        _NewChild.__name__ = field.child.__class__.__name__
        field.child.__class__ = _NewChild

    def create(self, validated_data):
        many_children = {}
        for k, ser in self.fields.items():
            if isinstance(ser, WritableNestedListSerializer):
                many_children.update({k: (ser, validated_data.pop(k, None))})
        instance = super().create(validated_data)
        for k, (ser, list_data) in many_children.items():
            ser.set_parent_instance(instance)
            ser.create(list_data)
        return instance

    def update(self, instance, validated_data):
        many_children = {}
        for k, ser in self.fields.items():
            if isinstance(ser, WritableNestedListSerializer):
                ser.set_parent_instance(instance)
                many_children.update({k: (ser, validated_data.pop(k, None))})
        instance = super().update(instance, validated_data)
        for k, (ser, list_data) in many_children.items():
            ser.update(getattr(instance, k), list_data)
        return instance
