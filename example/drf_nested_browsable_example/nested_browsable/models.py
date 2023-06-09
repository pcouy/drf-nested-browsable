"""
Simple nested models for demonstration purpose
"""
from django.db import models

class Model(models.Model):
    key = models.CharField(max_length=50)
    value = models.CharField(max_length=50)

    class Meta:
        abstract = True

    def __str__(self):
        return f"{self.key} => {self.value}"


class OuterModel(Model):
    """
    Contains a relationship with `MiddleModel`
    """


class MiddleModel(Model):
    """
    Contains a relationship with `InnerModel`
    """

    middle_parent = models.ForeignKey(
        OuterModel,
        on_delete=models.CASCADE,
        verbose_name="Parent instance",
        related_name="middle_children",
    )


class InnerModel(Model):
    """
    Will be used as a child model for the other models
    """

    inner_parent = models.ForeignKey(
        MiddleModel,
        on_delete=models.CASCADE,
        verbose_name="Parent instance",
        related_name="inner_children",
    )


class OtherInnerModel(Model):
    """
    Will be used as a second child model for the other models
    """

    inner_parent = models.ForeignKey(
        MiddleModel,
        on_delete=models.CASCADE,
        verbose_name="Parent instance",
        related_name="other_inner_children",
    )
