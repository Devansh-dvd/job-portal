from django.urls import path
from .apiviews import register , login

urlpatterns = [
    path('register/', register),
    path('login/', login),
]
