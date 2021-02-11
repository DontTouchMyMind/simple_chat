from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.views.generic.edit import FormView
from django.contrib.auth import get_user_model, authenticate, login, logout

from .forms import SignupForm, LoginForm
from .models import User


@login_required(login_url='/login/')
def index(request):
    user_list = User.objects.all()

    context = {
        'title': 'ListUser',
        'users_list': user_list,
        'username': request.user.username,
    }
    return render(request, 'home.html', context)


def room(request, group_id):
    users_list = User.objects.all()
    context = {
        'group_id': group_id,
        'title': 'ListUser',
        'users_list': users_list[1:],
        'username': request.user.username,
    }
    return render(request, 'room.html', context)


def logout_user(request):
    logout(request)
    return redirect('/')


class SignupView(FormView):
    template_name = 'signup.html'
    form_class = SignupForm
    success_url = '/'

    def form_valid(self, form):
        username = form.cleaned_data['username']
        email = form.cleaned_data['email']
        password = form.cleaned_data['password']
        user = get_user_model().objects.create_user(username=username, email=email, password=password)
        if user:
            login(self.request, user)
        return redirect('/')


class LoginView(FormView):
    template_name = 'login.html'
    form_class = LoginForm
    success_url = '/'

    def form_valid(self, form):
        username = form.cleaned_data['username']
        password = form.cleaned_data['password']
        user = authenticate(self.request, username=username, password=password)
        if user:
            login(self.request, user)
        return super().form_valid(form)
