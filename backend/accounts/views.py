from django.http import HttpResponse
from django.shortcuts import render
from .models import employee

def home(request):
    
    employees = employee.objects.all()

    for emp in employees:
        print(emp.name, emp.email)
    return HttpResponse("terminal running")