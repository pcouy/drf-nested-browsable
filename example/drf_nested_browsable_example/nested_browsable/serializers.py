"""
Serializers for the example models using nested serializers
"""
from drf_nested_browsable.serializers import (WritableNestedListSerializer,
                                              WritableNestedModelSerializer)
from rest_framework.serializers import (HyperlinkedIdentityField,
                                        ModelSerializer)

from .models import InnerModel, MiddleModel, OuterModel


class InnerSerializer(ModelSerializer):
    class Meta:
        model = InnerModel
        fields = ["key", "value", "parent"]
        list_serializer_class = WritableNestedListSerializer
        update_keys = "key"


class MiddleSerializer(WritableNestedModelSerializer):
    inner_children = InnerSerializer(many=True, required=False, default=[])

    class Meta:
        model = MiddleModel
        model_related_name = "parent"
        fields = ["key", "value", "parent", "inner_children"]
        list_serializer_class = WritableNestedListSerializer
        update_keys = "key"


class OuterSerializer(WritableNestedModelSerializer):
    middle_children = MiddleSerializer(many=True, required=False, default=[])

    class Meta:
        model = OuterModel
        model_related_name = "parent"
        fields = ["key", "value", "middle_children"]
