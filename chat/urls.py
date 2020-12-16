from django.urls import path

from chat.views import LoginView, SignupView, index, logout_user

urlpatterns = [
    path('', index),
    path('login/', LoginView.as_view()),
    path('logout/', logout_user),
    path('signup/', SignupView.as_view()),
]
