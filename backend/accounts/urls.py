from django.urls import path                          
from .apiviews import employees                     

urlpatterns = [
    path("employees/", employees),                     
]
