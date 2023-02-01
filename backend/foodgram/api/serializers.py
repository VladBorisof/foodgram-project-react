from django.contrib.auth.hashers import make_password
from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers

from recipes.models import (FavouriteRecipe,
                            Ingredient,
                            IngredientRecipe,
                            Recipe,
                            ShoppingCart,
                            Tag)
from users.models import Follow, User


class UserSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField()

    def get_is_subscribed(self, obj):
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return Follow.objects.filter(user=user, author=obj.id).exists()

    class Meta:
        model = User
        fields = '__all__'


class FollowUserSerializers(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source='author.id')
    email = serializers.ReadOnlyField(source='author.email')
    username = serializers.ReadOnlyField(source='author.username')
    first_name = serializers.ReadOnlyField(source='author.first_name')
    last_name = serializers.ReadOnlyField(source='author.last_name')
    is_subscribed = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

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
        return FollowRecipeSerializers(queryset, many=True).data

    def get_recipes_count(self, obj):
        return Recipe.objects.filter(author=obj.author).count()

    class Meta:
        model = Follow
        fields = '__all__'


class CreateUserSerializers(serializers.ModelSerializer):
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
        return super(CreateUserSerializers, self).create(validated_data)


class UserEditSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ('email', 'username', 'first_name', 'last_name')
        model = User


class SignupSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ('email', 'id', 'username',
                  'first_name', 'last_name', 'password')
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


class FollowRecipeSerializers(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug')


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ('name', 'measurement_unit')


class IngredientRecipeSerializers(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit'
    )
    amount = serializers.IntegerField()

    class Meta:
        model = IngredientRecipe
        fields = '__all__'


class RecipeSerializers(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    tag = TagSerializer(read_only=True, many=True)
    image = Base64ImageField()
    ingredients = IngredientRecipeSerializers(read_only=True, many=True)
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    def get_is_favorited(self, obj):
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return FavouriteRecipe.objects.filter(user=user,
                                              recipe=obj.id).exists()

    def get_is_in_shopping_cart(self, obj):
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return ShoppingCart.objects.filter(user=user, recipe=obj.id).exists()

    def to_representation(self, instance):
        """Convert `username` to lowercase."""
        ret = super().to_representation(instance)
        ret['username'] = ret['username'].lower()
        return ret

    def validate(self, data):
        ingredients = data.get('ingredients')
        ingredients_contain = {}
        if not ingredients:
            raise ValidationError('Добавьте ингредиент в рецепт')

        for ingredient in ingredients:
            if ingredient.get('id') in ingredients_contain:
                raise ValidationError(
                    'Ингредиент может быть добавлен только один раз')
            if int(ingredient.get('amount')) <= 0:
                raise ValidationError(
                    'Добавьте количество для ингредиента больше 0'
                )
            ingredients_contain[ingredient.get('id')] = ingredients_contain.get('amount')
        return data

    def ingredient_recipe_create(self, ingredients_set, recipe):
        objs = []
        for ingred in ingredients_set:
            ingredient = get_object_or_404(Ingredient, pk=ingred.get('id'))
            objs.append(IngredientRecipe(
                ingredient=ingredient,
                recipe=recipe,
                amount=ingred.get('amount')
            ))
        IngredientRecipe.objects.bulk_create(objs)

    def create(self, validated_data):
        image = validated_data.pop('image')
        tags = validated_data.pop('tags')
        recipe = Recipe.objects.create(image=image,
                                       author=self.context['request'].user,
                                       **validated_data)
        recipe.tags.set(tags)
        ingredients_set = self.initial_data.get('ingredients')
        self.ingredient_recipe_create(ingredients_set, recipe)
        return recipe

    def update(self, instance, validated_data):
        # instance.image = validated_data.get('image', instance.image)
        # instance.name = validated_data.get('name', instance.name)
        # instance.text = validated_data.get('text', instance.text)
        # instance.cooking_time = validated_data.get('cooking_time',
        #                                            instance.cooking_time)
        super().update(instance, validated_data)
        instance.tags.clear()
        tags = self.initial_data.get('tags')
        instance.tags.set(tags)
        instance.save()
        IngredientRecipe.objects.filter(recipe=instance).delete()
        ingredients_set = self.initial_data.get('ingredients')
        self.ingredient_recipe_create(ingredients_set, instance)
        return instance

    class Meta:
        model = Recipe
        fields = '__all__'


class FavoriteSerializers(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source='recipe.id')
    name = serializers.ReadOnlyField(source='recipe.name')
    image = serializers.ImageField(source='recipe.image')
    cooking_time = serializers.ReadOnlyField(source='recipe.cooking_time')

    class Meta:
        model = FavouriteRecipe
        fields = '__all__'


class ShoppingCardSerializers(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source='recipe.id')
    name = serializers.ReadOnlyField(source='recipe.name')
    image = serializers.ImageField(source='recipe.image')
    cooking_time = serializers.ReadOnlyField(source='recipe.cooking_time')

    class Meta:
        model = ShoppingCart
        fields = '__all__'
