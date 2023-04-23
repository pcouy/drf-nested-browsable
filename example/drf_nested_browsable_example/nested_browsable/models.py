"""
Simple nested models for demonstration purpose
"""
from django.db import models

class Model(models.Model):
    class Meta:
        abstract = True

    def __str__(self):
        return f"{self.key} => {self.value}"


class OuterModel(Model):
    """
    Contains a relationship with `MiddleModel`
    """

    key = models.CharField(max_length=50)
    value = models.CharField(max_length=50)


class MiddleModel(Model):
    """
    Contains a relationship with `InnerModel`
    """

    key = models.CharField(max_length=50)
    value = models.CharField(max_length=50)
    parent = models.ForeignKey(
        OuterModel,
        on_delete=models.CASCADE,
        verbose_name="Parent instance",
        related_name="middle_children",
    )


class InnerModel(Model):
    """
    Will be used as a child model for the other models
    """

    key = models.CharField(max_length=50)
    value = models.CharField(max_length=50)
    parent = models.ForeignKey(
        MiddleModel,
        on_delete=models.CASCADE,
        verbose_name="Parent instance",
        related_name="inner_children",
    )
