"""
Views using the demo serializers
"""
from rest_framework.viewsets import ModelViewSet

from .models import InnerModel, MiddleModel, OtherInnerModel, OuterModel, RecursiveModel
from .serializers import (
    InnerSerializer,
    MiddleSerializer,
    OtherInnerSerializer,
    OuterSerializer,
    RecursiveSerializer,
)


class InnerViewSet(ModelViewSet):
    queryset = InnerModel.objects.all()
    serializer_class = InnerSerializer


class OtherInnerViewSet(ModelViewSet):
    queryset = OtherInnerModel.objects.all()
    serializer_class = OtherInnerSerializer


class MiddleViewSet(ModelViewSet):
    queryset = MiddleModel.objects.all()
    serializer_class = MiddleSerializer


class OuterViewSet(ModelViewSet):
    queryset = OuterModel.objects.all()
    serializer_class = OuterSerializer


class RecursiveViewSet(ModelViewSet):
    queryset = RecursiveModel.objects.all()
    serializer_class = RecursiveSerializer
