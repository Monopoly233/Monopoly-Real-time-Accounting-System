from django.shortcuts import render
from django.http import HttpResponse
# Create your views here.
from django.http import JsonResponse
def home(request):
    content = "<h1>welcome to here</h1>"
    return HttpResponse(content)

def sayhello(request):
    content = "<h1>Hello, World!</h1>"
    return HttpResponse(content)

def drinks(request, drink_name):
    drink = {
        'mocha' : 'type of coffee',
        'tea' : 'type of hot beverage',
        'lemonade': 'type of refreshment'
    }
    choice_of_drink = drink[drink_name]
    return HttpResponse(f"<h2>{drink_name}</h2> " + choice_of_drink)

def about(request):
    return HttpResponse("About us")

def menu(request):
    return HttpResponse("Menu for Little Lemon")

def book(request):
    return HttpResponse("Make a booking")