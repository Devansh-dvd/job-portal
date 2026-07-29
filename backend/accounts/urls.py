from django.urls import path
from .apiviews import register

urlpatterns = [
    path('register/', register),
]
