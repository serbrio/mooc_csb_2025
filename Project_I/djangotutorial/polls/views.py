from django.shortcuts import render
from django.http import HttpResponse


# Create your views here.
def index(request):
    return HttpResponse("Hello, world. You are at the polls index.")


def shmindex(request):
    return HttpResponse("You are at polls shmindex.")
