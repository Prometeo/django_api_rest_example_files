# coding:utf-8
from django.urls import path
from . import views

urlpatterns = [
    path(
        "api/v1/profiles-raw/",
        views.get_post_profile_raw,
        name="get_post_profiles_raw"),
    path(
        "api/v1/profiles-processed/",
        views.get_profile_processed,
        name="get_profiles_processed"),
]
