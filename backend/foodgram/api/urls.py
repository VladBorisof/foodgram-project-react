from django.urls import include, path

from api.views import IngredientViewSet, TagViewSet
from rest_framework.routers import DefaultRouter


router = DefaultRouter()

router.register('ingredients', IngredientViewSet, basename='ingredients')
router.register('tags', TagViewSet, basename='genres')

urlpatterns = [
    path('', include(router.urls)),
    path('', include('djoser.urls')),
    path('', include('djoser.urls.authtoken'))
]
