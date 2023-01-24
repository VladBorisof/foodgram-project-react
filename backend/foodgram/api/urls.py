from api.views import IngredientViewSet, RecipeViewSet, TagViewSet
from django.urls import include, path
from rest_framework.routers import DefaultRouter


router = DefaultRouter()

router.register('ingredients', IngredientViewSet, basename='ingredients')
router.register('tags', TagViewSet, basename='tags')
router.register('recipes', RecipeViewSet, basename='recipes')

urlpatterns = [
    path('', include(router.urls)),
    path('', include('djoser.urls')),
    path('', include('djoser.urls.authtoken'))
]
