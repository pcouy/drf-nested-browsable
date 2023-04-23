"""
Provides writable serializers for Django Rest Framework

Using these serializers requires a little more configuration than basic
serializers.
TODO: Mettre au propre
"""
from rest_framework.serializers import ListSerializer, ModelSerializer

class WritableNestedListSerializer(ListSerializer):
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
        self._set_parent_field_name()
        if "_parent_instance" not in dir(self) or self._parent_instance is None:
            raise AttributeError(
                "You must call"
                "`WritableNestedListSerializer.set_parent_instance(instance)`"
                "before accessing `WritableNestedListSerializer.parent_data`"
            )

        return {self._parent_field_name: self._parent_instance}

    def set_parent_instance(self, parent_instance):
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
                        **self.parent_data
                    )
                    elem = self.child.update(elem, full_elem)
                except instance.model.DoesNotExist:
                    elem = self.child.create(full_elem)
                updated_ids.append(elem.id)

            instance.exclude(id__in=updated_ids).delete()


class WritableNestedModelSerializer(ModelSerializer):
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

        super().__init__(*args, **kwargs)

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
