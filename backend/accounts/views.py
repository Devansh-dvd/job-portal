from django.http import HttpResponse
from django.shortcuts import render
from .models import User

def home(request):
    
    employees = User.objects.all()

    for emp in employees:
        print(emp.name, emp.email)
    return HttpResponse("terminal running")