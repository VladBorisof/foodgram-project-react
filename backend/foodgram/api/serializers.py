import datetime

from django.contrib.auth.hashers import make_password
from rest_framework import serializers
from rest_framework.relations import SlugRelatedField
from rest_framework.validators import UniqueTogetherValidator

from foodgram_app.models import (
    Ingredient, IngredientRecipe, Tag, Recipe, FavouriteRecipe
)
from users.models import User


class CustomCreateUserSerializers(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True,
        required=True,
        style=dict(input_type='Пароль', placeholder='Пароль')
    )

    class Meta:
        model = User
        fields = '__all__'

    def create(self, validated_data):
        validated_data['password'] = make_password(
            validated_data.get('password')
        )
        return super(CustomCreateUserSerializers, self).create(validated_data)


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug')


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ('name', 'measurement_unit')


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        fields = ('email', 'username', 'first_name', 'last_name')
        model = User


class UserEditSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ('email', 'username', 'first_name', 'last_name')
        model = User


class SignupSerializer(serializers.ModelSerializer):

    class Meta:
        fields = ('email', 'id', 'username', 'first_name', 'last_name', 'password')
        model = User

    def validate_username(self, value):
        if value == 'me':
            raise serializers.ValidationError(
                'Создать пользователя с именем "me" не разрешено.'
            )
        return value


class TokenSerializer(serializers.ModelSerializer):
    confirmation_code = serializers.CharField(required=True)

    class Meta:
        fields = ('username', 'confirmation_code')
        model = User


class IngredientRecipeSerializers(serializers.ModelSerializer):
    id = ''
    name = ''
    measurement_unit = ''
    amount = ''

    class Meta:
        model = IngredientRecipe
        fields = '__all__'


class RecipeSerializers(serializers.ModelSerializer):
    author = ''
    tag = TagSerializer(read_only=True, many=True)
    image = ''
    ingredients = IngredientRecipeSerializers(read_only=True, many=True)
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()


# class GenreSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Genre
#         fields = ('name', 'slug')


# class TitleGetSerializer(serializers.ModelSerializer):
#     genre = GenreSerializer(many=True)
#     category = CategorySerializer()
#     rating = serializers.IntegerField()
#
#     class Meta:
#         fields = (
#             'id',
#             'name',
#             'year',
#             'description',
#             'genre',
#             'category',
#             'rating'
#         )
#         model = Title


# class TitlePostSerializer(serializers.ModelSerializer):
#     category = serializers.SlugRelatedField(
#         queryset=Category.objects.all(),
#         slug_field='slug',
#         required=True
#     )
#     genre = serializers.SlugRelatedField(
#         queryset=Genre.objects.all(),
#         slug_field='slug',
#         many=True,
#         required=True
#     )
# 
#     class Meta:
#         fields = (
#             'id',
#             'name',
#             'year',
#             'description',
#             'genre',
#             'category',
#         )
#         model = Title
# 
#     def validate_year(self, year):
#         current_year = datetime.date.today().year
#         if not (year <= current_year):
#             raise ValidationError('Произведение еще не вышло')
#         return year


# class ReviewSerializer(serializers.ModelSerializer):
#     author = SlugRelatedField(
#         read_only=True,
#         slug_field='username',
#         default=serializers.CurrentUserDefault()
#     )
#     title = serializers.HiddenField(default=GetTitle())
#
#     class Meta:
#         fields = ('id', 'text', 'score', 'author', 'pub_date', 'title')
#         model = Review
#         validators = [
#             UniqueTogetherValidator(
#                 queryset=Review.objects.all(),
#                 fields=('title', 'author'),
#                 message='Можно оставить только один отзыв'
#             )
#         ]
#
#     def validate_score(self, score):
#         if score not in range(1, 11):
#             raise ValidationError('Допустимы оценки от 1 до 10')
#         return score


# class CommentSerializer(serializers.ModelSerializer):
#     author = SlugRelatedField(
#         read_only=True, slug_field='username'
#     )
#
#     class Meta:
#         fields = ('id', 'text', 'author', 'pub_date')
#         model = Comment
