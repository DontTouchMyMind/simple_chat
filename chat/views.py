from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.views.generic.edit import FormView
from django.contrib.auth import get_user_model, authenticate, login, logout

from .forms import SignupForm, LoginForm
from .models import User, ChatGroup, GroupParticipant


@login_required(login_url='/login/')
def index(request):
    user_list = User.objects.all()
    new_group_id = len(ChatGroup.objects.all()) + 1

    context = {
        'users_list': user_list,
        'username': request.user.username,
        'new_group_id': new_group_id,
    }
    return render(request, 'home.html', context)


def room(request, group_id):
    users_list = User.objects.all().exclude(pk=request.user.id)
    group_name = ChatGroup.objects.filter(pk=group_id).first()
    group_users_id = list(GroupParticipant.objects.filter(group=group_id).values_list('user', flat=True))
    group_users_name = [user.username for user in users_list if user.id in group_users_id]

    context = {
        'group_id': group_id,
        'group_name': group_name,
        'group_users': group_users_name,
        'users_list': users_list,
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
