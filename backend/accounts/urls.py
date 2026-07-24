from django.urls import path
from .apiviews import hello

urlpatterns = [
    path('hello/', hello, name='hello')
]
