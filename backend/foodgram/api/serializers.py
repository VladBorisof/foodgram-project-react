from django.contrib.auth.hashers import make_password
from django.core.exceptions import ValidationError
from django.db.models import F
from django.shortcuts import get_object_or_404
from djoser.serializers import UserCreateSerializer, UserSerializer
from drf_extra_fields.fields import Base64ImageField
from rest_framework.serializers import (CharField,
                                        ModelSerializer,
                                        SerializerMethodField,
                                        ReadOnlyField,
                                        IntegerField, ImageField)

from recipes.models import (Favorite,
                            Ingredient,
                            IngredientRecipe,
                            Recipe,
                            ShoppingCart,
                            Tag)
from users.models import Follow, User


class UserRegistrationSerializer(UserCreateSerializer):
    class Meta:
        model = User
        fields = (
            "email",
            "id",
            "username",
            "first_name",
            "last_name",
            "password",
        )
        extra_kwargs = {"password": {"write_only": True}}

    def create(self, validated_data):
        user = super().create(validated_data)
        user.set_password(validated_data["password"])
        user.save()
        return user


class ShortRecipeSerializer(ModelSerializer):
    """Сериализатор для модели Recipe.
    Определён укороченный набор полей для некоторых эндпоинтов.
    """
    class Meta:
        model = Recipe
        fields = 'id', 'name', 'image', 'cooking_time'
        read_only_fields = '__all__',


class UsersSerializer(ModelSerializer):
    is_subscribed = SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'password',
        )
        extra_kwargs = {'password': {'write_only': True}}
        read_only_fields = 'is_subscribed',

    def get_is_subscribed(self, obj):
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return Follow.objects.filter(user=user, author=obj.id).exists()

    def create(self, validated_data):
        user = super().create(validated_data)
        user.set_password(validated_data.get('password'))
        user.save()
        return user


class UsersSubscribeSerializer(UsersSerializer):
    """Сериализатор вывода авторов на которых подписан текущий пользователь.
    """
    recipes = ShortRecipeSerializer(many=True, read_only=True)
    recipes_count = SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'recipes',
            'recipes_count',
        )
        read_only_fields = '__all__',

    def get_recipes_count(self, obj: User) -> int:
        """ Показывает общее количество рецептов у каждого автора.
        Args:
            obj (User): Запрошенный пользователь.
        Returns:
            int: Количество рецептов созданных запрошенным пользователем.
        """
        return obj.recipe.count()


class FollowUserSerializer(ModelSerializer):
    id = ReadOnlyField(source='author.id')
    email = ReadOnlyField(source='author.email')
    username = ReadOnlyField(source='author.username')
    first_name = ReadOnlyField(source='author.first_name')
    last_name = ReadOnlyField(source='author.last_name')
    is_subscribed = SerializerMethodField()
    recipes = SerializerMethodField()
    recipes_count = SerializerMethodField()

    def get_is_subscribed(self, obj):
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return Follow.objects.filter(user=user, author=obj.author).exists()

    def get_recipes(self, obj):
        request = self.context.get('request')
        recipes_limit = request.GET.get('recipes_limit')
        queryset = Recipe.objects.filter(author=obj.author)
        if recipes_limit:
            queryset = queryset[:int(recipes_limit)]
        return FollowRecipeSerializer(queryset, many=True).data

    def get_recipes_count(self, obj):
        return Recipe.objects.filter(author=obj.author).count()

    class Meta:
        model = Follow
        fields = '__all__'


class CreateUserSerializer(ModelSerializer):
    password = CharField(
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
        return super(CreateUserSerializer, self).create(validated_data)


class UserEditSerializer(ModelSerializer):
    class Meta:
        fields = ('email', 'username', 'first_name', 'last_name')
        model = User


class SignupSerializer(ModelSerializer):
    class Meta:
        fields = ('email', 'id', 'username',
                  'first_name', 'last_name', 'password')
        model = User

    def validate_username(self, value):
        if value == 'me':
            raise ValidationError(
                'Создать пользователя с именем "me" не разрешено.'
            )
        return value


class TokenSerializer(ModelSerializer):
    confirmation_code = CharField(required=True)

    class Meta:
        fields = ('username', 'confirmation_code')
        model = User


class FollowRecipeSerializer(ModelSerializer):
    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class TagSerializer(ModelSerializer):
    class Meta:
        model = Tag
        fields = '__all__'


class IngredientSerializer(ModelSerializer):
    class Meta:
        model = Ingredient
        fields = '__all__'


class RecipeInfoSerializer(ModelSerializer):
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = '__all__'


class RecipeListSerializer(ModelSerializer):
    tags = TagSerializer(many=True, read_only=True)
    ingredients = SerializerMethodField()
    author = UserSerializer(read_only=True)
    image = Base64ImageField()
    is_in_shopping_cart = SerializerMethodField(read_only=True)
    is_favorited = SerializerMethodField(read_only=True)

    class Meta:
        model = Recipe
        fields = '__all__'

    def get_ingredients(self, recipe: Recipe):
        ingredients = recipe.ingredients.values(
            'id', 'name', 'measurement_unit',
            amount=F('ingredientrecipe__amount')
        )
        return ingredients

    def get_is_favorited(self, recipe):
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return Favorite.objects.filter(user=user, recipe=recipe.id).exists()

    def get_is_in_shopping_cart(self, recipe):
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return ShoppingCart.objects.filter(user=user, recipe=recipe.id).exists()


class IngredientRecipeSerializer(ModelSerializer):
    id = IntegerField(write_only=True)

    class Meta:
        model = IngredientRecipe
        fields = ('id', 'amount')


class CreateRecipeSerializer(ModelSerializer):
    author = UserSerializer(read_only=True)
    tag = TagSerializer(read_only=True, many=True)
    image = Base64ImageField()
    ingredients = IngredientRecipeSerializer(many=True)
    is_favorited = SerializerMethodField()
    is_in_shopping_cart = SerializerMethodField()

    class Meta:
        model = Recipe
        fields = '__all__'

    def to_representation(self, instance):
        return RecipeListSerializer(
            instance,
            context={
                'request': self.context.get('request'),
            }
        ).data

    def validate_ingredients(self, value):
        if not value:
            raise ValidationError('Добавьте ингредиент в рецепт')

        ingredients_contain = {}
        for ingredient in value:
            if ingredient.get('id') in ingredients_contain:
                raise ValidationError(
                    'Ингредиент может быть добавлен только один раз')
            if int(ingredient.get('amount')) <= 0:
                raise ValidationError(
                    'Добавьте количество для ингредиента больше 0'
                )
            ingredients_contain[ingredient.get('id')] = ingredient.get('amount')
        return value

    @staticmethod
    def create_ingredients(ingredients_set, recipe):
        ingredients = []
        for ingredient in ingredients_set:
            ingredient_name = get_object_or_404(
                Ingredient,
                pk=ingredient.get('id')
            )
            ingredients.append(
                IngredientRecipe(
                    recipe=recipe,
                    ingredient=ingredient_name,
                    amount=ingredient.get('amount')
                )
            )
        IngredientRecipe.objects.bulk_create(ingredients)

    def create(self, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        validated_data['author'] = self.context.get('request').user
        recipe = super().create(validated_data)
        recipe.tags.set(tags)
        self.create_ingredients(ingredients, recipe)
        return recipe

    def update(self, instance, validated_data):
        ingredients = validated_data.pop('ingredients')
        IngredientRecipe.objects.filter(recipe=instance).delete()
        self.create_ingredients(ingredients, instance)
        return super().update(instance, validated_data)


class FavoriteSerializer(ModelSerializer):
    id = ReadOnlyField(source='recipe.id')
    name = ReadOnlyField(source='recipe.name')
    image = ImageField(source='recipe.image')
    cooking_time = ReadOnlyField(source='recipe.cooking_time')

    class Meta:
        model = Favorite
        fields = '__all__'


class ShoppingCardSerializer(ModelSerializer):
    id = ReadOnlyField(source='recipe.id')
    name = ReadOnlyField(source='recipe.name')
    image = ImageField(source='recipe.image')
    cooking_time = ReadOnlyField(source='recipe.cooking_time')

    class Meta:
        model = ShoppingCart
        fields = '__all__'
