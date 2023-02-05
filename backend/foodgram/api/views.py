from io import BytesIO

from django.db.models import Sum
from django.http import FileResponse, HttpResponse
from django_filters.rest_framework import DjangoFilterBackend
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen.canvas import Canvas
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from api.filters import RecipeFilter
from api.mixins import CustomRecipeModelViewSet
from api.pagination import LimitPagePagination
from api.permissions import (AuthorOrReadOnly, IsRoleAdmin)
from api.serializers import (FollowUserSerializers,
                             FavoriteSerializers,
                             IngredientSerializer,
                             TagSerializer,
                             UserEditSerializer,
                             UserSerializer,
                             RecipeSerializers,
                             ShoppingCardSerializers)
from recipes.models import (FavouriteRecipe,
                            Ingredient,
                            IngredientRecipe,
                            Tag,
                            Recipe,
                            ShoppingCart)
from users.models import Follow, User


class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (permissions.AllowAny,)


class IngredientViewSet(viewsets.ModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (permissions.AllowAny,)


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

    @action(detail=False, permission_classes=[IsAuthenticated])
    def subscriptions(self, request):
        queryset = Follow.objects.filter(user=request.user)
        page = self.paginate_queryset(queryset)
        serializer = FollowUserSerializers(page, many=True,
                                           context={'request': request})
        return self.get_paginated_response(serializer.data)

    @action(detail=True, methods=['post'])
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
        serializer = FollowUserSerializers(queryset,
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
    serializer_class = RecipeSerializers
    pagination_class = LimitPagePagination
    # filter_backends = DjangoFilterBackend
    # filter_class = RecipeFilter
    permission_classes = (AuthorOrReadOnly,)

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
            'ingredient__name').annotate(amount=Sum('amount'))

        buffer = BytesIO()
        canvas = Canvas(buffer)
        pdfmetrics.registerFont(
            TTFont('Country', 'Country.ttf', 'UTF-8'))
        canvas.setFont('Country', size=36)
        canvas.drawString(70, 800, 'Продуктовый помощник')
        canvas.drawString(70, 760, 'список покупок:')
        canvas.setFont('Country', size=18)
        canvas.drawString(70, 700, 'Ингредиенты:')
        canvas.setFont('Country', size=16)
        canvas.drawString(70, 670, 'Название:')
        canvas.drawString(220, 670, 'Количество:')
        canvas.drawString(350, 670, 'Единица измерения:')
        height = 630
        for ingredient in ingredients:
            canvas.drawString(70, height, f"{ingredient['ingredient__name']}")
            canvas.drawString(250, height,
                              f"{ingredient['amount']}")
            canvas.drawString(380, height,
                              f"{ingredient['ingredient__measurement_unit']}")
            height -= 25
        canvas.save()
        buffer.seek(0)
        response = FileResponse(buffer, as_attachment=True,
                            filename='Shoppinglist.pdf')

        text = f"{ingredient['ingredient__name']} - {ingredient['amount']}"
        filename = 'shop.txt'
        response = HttpResponse(text, content_type='text/plain')
        response['Content-Disposition'] = f'attachment; filenamr={filename}'
        return response
