from django.contrib.auth.views import LoginView, LogoutView
from django.urls import path, include

from users.views import RegisterView

urlpatterns = [
    path('signup/', RegisterView.as_view(), name='register'),
    path('', include('django.contrib.auth.urls'))
]