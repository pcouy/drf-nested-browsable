"""
Serializers for the example models using nested serializers
"""
from drf_nested_browsable.serializers import (WritableNestedListSerializer,
                                              WritableNestedModelSerializer)
from rest_framework.serializers import (HyperlinkedModelSerializer,
                                        ModelSerializer)
from rest_framework_recursive.fields import RecursiveField

from .models import InnerModel, MiddleModel, OtherInnerModel, OuterModel, RecursiveModel


class InnerSerializer(HyperlinkedModelSerializer):
    class Meta:
        model = InnerModel
        fields = ["key", "value", "inner_parent", "url"]
        list_serializer_class = WritableNestedListSerializer
        update_keys = "key"


class OtherInnerSerializer(InnerSerializer):
    class Meta(InnerSerializer.Meta):
        model = OtherInnerModel


class MiddleSerializer(HyperlinkedModelSerializer, WritableNestedModelSerializer):
    inner_children = InnerSerializer(many=True, required=False, default=[])
    other_inner_children = OtherInnerSerializer(many=True, required=False, default=[])

    class Meta:
        model = MiddleModel
        model_related_name = "inner_parent"
        fields = [
            "key",
            "value",
            "middle_parent",
            "inner_children",
            "other_inner_children",
            "url",
        ]
        list_serializer_class = WritableNestedListSerializer
        update_keys = "key"


class OuterSerializer(WritableNestedModelSerializer):
    middle_children = MiddleSerializer(many=True, required=False, default=[])

    class Meta:
        model = OuterModel
        model_related_name = "middle_parent"
        fields = ["key", "value", "middle_children"]


class RecursiveSerializer(WritableNestedModelSerializer):
    children = RecursiveField(many=True, required=False, default=[])

    class Meta:
        model = RecursiveModel
        model_related_name = "parent"
        fields = ["key", "value", "children"]
        list_serializer_class = WritableNestedListSerializer
        update_keys = "key"

