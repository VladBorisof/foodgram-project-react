from api.authentication import signup, token
from django.urls import path

urlpatterns = [
    path('v1/auth/signup/', signup, name='signup'),
]
