"""
URL configuration for drf_nested_browsable_example project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from rest_framework.routers import DefaultRouter

from .nested_browsable.views import (InnerViewSet, MiddleViewSet,
                                     OtherInnerViewSet, OuterViewSet, RecursiveViewSet)

router = DefaultRouter()
router.register(r"inner", InnerViewSet, basename="innermodel")
router.register(r"otherinner", OtherInnerViewSet, basename="otherinnermodel")
router.register(r"middle", MiddleViewSet, basename="middlemodel")
router.register(r"outer", OuterViewSet, basename="outermodel")
router.register(r"recursive", RecursiveViewSet, basename="recursivemodel")

urlpatterns = [path("admin/", admin.site.urls), *router.urls]
