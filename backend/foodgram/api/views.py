from django.db.models import Sum
from django.http import HttpResponse
from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import DjangoModelPermissions
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from api.filters import IngredientsSearchFilter
from api.mixins import CustomRecipeModelViewSet
from api.pagination import LimitPagePagination
from api.permissions import (AuthorOrReadOnly)
from api.serializers import (FollowUserSerializer,
                             IngredientSerializer,
                             TagSerializer,
                             UserEditSerializer,
                             UsersSubscribeSerializer,
                             CreateRecipeSerializer)
from recipes.models import (Favorite,
                            Ingredient,
                            IngredientRecipe,
                            Tag,
                            Recipe,
                            ShoppingCart)
from users.models import Follow, User


class TagViewSet(ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (AllowAny,)
    pagination_class = None


class IngredientViewSet(ModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (AllowAny,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = IngredientsSearchFilter
    pagination_class = None


class UsersViewSet(UserViewSet):
    queryset = User.objects.all()
    add_serializer = UsersSubscribeSerializer
    pagination_class = PageNumberPagination
    permission_classes = (DjangoModelPermissions,)
    # lookupfield = 'username'

    @action(
        methods=[
            'GET',
            'PATCH',
        ],
        detail=False,
        permission_classes=(IsAuthenticated,),
        serializer_class=UserEditSerializer,
    )
    def me(self, request):
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

    @action(detail=False, permission_classes=(IsAuthenticated,))
    def subscriptions(self, request):
        queryset = Follow.objects.filter(user=request.user)
        page = self.paginate_queryset(queryset)
        serializer = FollowUserSerializer(page, many=True,
                                           context={'request': request})
        return self.get_paginated_response(serializer.data)

    @action(
        detail=True, methods=('GET', 'POST',),
        permission_classes=[IsAuthenticated]
    )
    def subscribe(self, request, id=None):
        user = request.user
        author = get_object_or_404(User, id=id)
        if user == author:
            return Response({'errors': 'Вы не можете подписаться на себя.'},
                            status=status.HTTP_400_BAD_REQUEST)
        if Follow.objects.filter(user=user, author=author).exists():
            return Response({'errors': 'Вы уже подписались на автора.'},
                            status=status.HTTP_400_BAD_REQUEST)
        queryset = Follow.objects.create(user=user, author=author)
        serializer = FollowUserSerializer(queryset,
                                           context={'request': request})
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @subscribe.mapping.delete
    def subscribe_del(self, request, id=None):
        user = request.user
        author = get_object_or_404(User, id=id)
        if not Follow.objects.filter(user=user, author=author).exists():
            return Response({'errors': 'Подписки не существует.'},
                            status=status.HTTP_400_BAD_REQUEST)
        Follow.objects.get(user=user, author=author).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class RecipeViewSet(CustomRecipeModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = CreateRecipeSerializer
    pagination_class = LimitPagePagination
    # filter_backends = DjangoFilterBackend
    # filter_class = RecipeFilter
    permission_classes = (AuthorOrReadOnly,)

    @action(detail=True,
            methods=['post', 'delete'],
            permission_classes=(IsAuthenticated,))
    def favorite(self, request, pk):
        match request.method:
            case 'POST':
                return self.add_obj(
                    model=Favorite,
                    pk=pk,
                    # serializers=FavoriteSerializers,
                    user=request.user
                )
            case 'DELETE':
                return self.del_obj(
                    model=Favorite,
                    pk=pk,
                    user=request.user
                )
            case _:
                return None

    @action(detail=True,
            methods=['post', 'delete'],
            permission_classes=(IsAuthenticated,))
    def shopping_cart(self, request, pk=None):
        match request.method:
            case 'POST':
                return self.add_obj(
                    model=ShoppingCart,
                    pk=pk,
                    # serializers=ShoppingCardSerializers,
                    user=request.user
                )
            case 'DELETE':
                return self.del_obj(
                    model=ShoppingCart,
                    pk=pk,
                    user=request.user
                )
            case _:
                return Response(
                    'Не разрешено',
                    status=status.HTTP_405_METHOD_NOT_ALLOWED
                )

    @action(detail=False, permission_classes=(IsAuthenticated,))
    def download_shopping_cart(self, request):
        user = request.user
        if not user.shopping_cart.exists():
            return Response(status=status.HTTP_400_BAD_REQUEST)
        ingredients = IngredientRecipe.objects.filter(
            recipe__shopping_carts__user=user).values(
            'ingredient__name',
            'ingredient__measurement_unit').order_by(
            'ingredient__name').annotate(count=Sum('amount'))

        today = timezone.now()
        shopping_list = (
            f'Список покупок для: {user.get_full_name()}\n\n'
            f'Дата: {today:%Y-%m-%d}\n\n'
        )
        shopping_list += '\n'.join([
            f'- {ingredient["ingredient__name"]} '
            f'({ingredient["ingredient__measurement_unit"]})'
            f' - {ingredient["count"]}'
            for ingredient in ingredients
        ])

        filename = f'{user.username}_shopping_list.txt'
        response = HttpResponse(shopping_list, content_type='text/plain')
        response['Content-Disposition'] = f'attachment; filename={filename}'

        return response
