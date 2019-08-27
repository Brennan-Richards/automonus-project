from django.shortcuts import render, redirect
from django.contrib import auth
from django.contrib.auth.models import User


def signup(request):
    if request.method == 'POST':
        #User wants to sign up
        if request.POST['password'] == request.POST['confirm']:
            try:
                user = User.objects.get(username=request.POST['email'])
                return render(request, 'accounts/signup.html', {'error':'Username has already been taken.'})
            except User.DoesNotExist:
                user = User.objects.create_user(request.POST['email'], password=request.POST['password'])
                auth.login(request, user)
                return redirect('home')
        else:
            return render(request, 'accounts/signup.html', {'error':'Passwords must match.'})

    else:
        #User wants to input information
        return render(request, 'accounts/signup.html')

def login(request):
    if request.method == 'POST':
        user = auth.authenticate(username=request.POST['email'], password=request.POST['password'])
        if user :
            auth.login(request, user)
            return redirect('home')
        else:
            return render(request, 'accounts/login.html',{'error':'Username or password is incorrect.'})
    else:
        return render(request, 'accounts/login.html')

def logout(request):
    if request.method == 'POST':
        auth.logout(request)
        return redirect('home')
        # Where should users go on log out?
