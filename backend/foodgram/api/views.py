from django.db.models import Sum
from rest_framework import status, viewsets, permissions
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from api.filters import RecipeFilter
from api.pagination import LimitPagePagination
from api.permissions import (IsRoleAdmin, AuthorOrReadOnly)
from api.serializers import (IngredientSerializer,
                             FavoriteSerializers,
                             TagSerializer,
                             UserEditSerializer,
                             UserSerializer,
                             RecipeSerializers,
                             ShoppingCardSerializers)
from api.mixins import CustomRecipeModelViewSet
from foodgram_app.models import (Ingredient,
                                 IngredientRecipe,
                                 FavouriteRecipe,
                                 Tag,
                                 Recipe,
                                 ShoppingCart)
from users.models import User


class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = permissions.AllowAny


class IngredientViewSet(viewsets.ModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = permissions.AllowAny


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    pagination_class = PageNumberPagination
    permission_classes = (IsRoleAdmin,)
    lookup_field = 'username'

    @action(
        methods=[
            'GET',
            'PATCH',
        ],
        detail=False,
        url_path='me',
        permission_classes=(IsAuthenticated,),
        serializer_class=UserEditSerializer,
    )
    def users_own_profile(self, request):
        user = request.user
        if request.method == 'GET':
            serializer = self.get_serializer(user)
            return Response(serializer.data, status=status.HTTP_200_OK)
        if request.method == 'PATCH':
            serializer = self.get_serializer(
                user,
                data=request.data,
                partial=True
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)


class RecipeViewSet(CustomRecipeModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializers
    pagination_class = LimitPagePagination
    filter_backends = DjangoFilterBackend
    filter_class = RecipeFilter
    permission_classes = AuthorOrReadOnly

    @action(detail=True,
            methods=['post', 'delete'],
            permission_classes=permissions.IsAuthenticated)
    def favorite(self, request, pk=None):
        match request.method:
            case 'POST':
                return self.add_object(
                    model=FavouriteRecipe,
                    pk=pk,
                    serializers=FavoriteSerializers,
                    user=request.user
                )
            case 'DELETE':
                return self.del_object(
                    model=FavouriteRecipe,
                    pk=pk,
                    user=request.user
                )
            case _:
                return None

    @action(detail=True,
            methods=['post', 'delete'],
            permission_classes=permissions.IsAuthenticated)
    def shopping_cart(self, request, pk=None):
        match request.method:
            case 'POST':
                return self.add_object(
                    model=ShoppingCart,
                    pk=pk,
                    serializers=ShoppingCardSerializers,
                    user=request.user
                )
            case 'DELETE':
                return self.del_object(
                    model=ShoppingCart,
                    pk=pk,
                    user=request.user
                )
            case _:
                return Response(
                    'Не разрешено',
                    status=status.HTTP_405_METHOD_NOT_ALLOWED
                )

    @action(detail=False, permission_classes=[permissions.IsAuthenticated])
    def download_shopping_cart(self, request):
        user = request.user
        ingredients = IngredientRecipe.objects.filter(
            recipe__shopping_carts__user=user).values(
            'ingredient__name',
            'ingredient__measurement_unit').order_by(
            'ingredient__name').annotate(amount=Sum('amount')
        )

