from django.shortcuts import render, redirect
from .models import Lock

def index(request):
    context = {
        'locks': Lock.objects.all()
    }
    # return render(request, 'main/index.html', context)
    return redirect('admin/')
