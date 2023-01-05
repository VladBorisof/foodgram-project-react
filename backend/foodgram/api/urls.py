from api.authentication import signup, token
from django.urls import path

urlpatterns = [
    path('users/', signup, name='signup'),
]
