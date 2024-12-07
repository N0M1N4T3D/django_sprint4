from django.shortcuts import render, redirect
from .forms import RegistrationForm
from django.contrib.auth.forms import *
from django.contrib.auth import login


def registration(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('/')
    else:
        form = RegistrationForm()
    return render(request, 'registration/registration_form.html', {'form': form})
