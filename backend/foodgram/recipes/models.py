from django.core.validators import MinValueValidator
from django.db import models

from users.models import User


class Tag(models.Model):
    name = models.CharField(
        max_length=200,
        unique=True,
        verbose_name='name'
    )
    color = models.CharField(
        max_length=50,
        default='4b0082',
        unique=True,
        verbose_name='color'
    )
    slug = models.SlugField(
        verbose_name='slug'
    )

    class Meta:
        verbose_name = 'Tag'
        verbose_name_plural = 'Tags'
        ordering = ('id',)

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    name = models.CharField(
        max_length=200,
        verbose_name='name'
    )
    measurement_unit = models.CharField(
        max_length=20,
        verbose_name='measurement_unit',
        default='',
    )

    class Meta:
        verbose_name = 'Ingredient'
        verbose_name_plural = 'Ingredients'
        ordering = ('id',)


class Recipe(models.Model):
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipe',
        verbose_name='author'
    )
    name = models.CharField(
        max_length=200,
        verbose_name='name'
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through='IngredientRecipe',
        related_name='recipes',
        verbose_name='ingredients',
    )
    image = models.ImageField(
        verbose_name='image',
        upload_to='recipes/'
    )
    text = models.TextField(
        verbose_name='description'
    )
    tags = models.ManyToManyField(
        Tag,
        related_name='recipe',
        verbose_name='tags'
    )
    cooking_time = models.PositiveIntegerField(
        validators=[MinValueValidator(1)],
        verbose_name='cooking time'
    )

    class Meta:
        verbose_name = 'Recipe'
        verbose_name_plural = 'Recipes'

    def __str__(self):
        return self.name


class IngredientRecipe(models.Model):
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        verbose_name='ingredient'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='ingredients_list',
        verbose_name='recipe'
    )
    amount = models.PositiveIntegerField(
        verbose_name='amount'
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['ingredient', 'recipe'],
                name='unique_ingredient_recipe',
            )
        ]
        verbose_name = 'Ingredient'
        verbose_name_plural = 'Ingredients'


class Favorite(models.Model):
    user = models.ForeignKey(
        User,
        related_name='favourite_recipes',
        on_delete=models.CASCADE,
        verbose_name='user'
    )
    recipe = models.ForeignKey(
        Recipe,
        related_name='in_favourites',
        on_delete=models.CASCADE,
        verbose_name='recipe'
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_favorite_recipe',
            )
        ]
        verbose_name = 'Favorite'
        verbose_name_plural = 'Favorites'

    def __str__(self):
        return f'{self.user.username} - {self.recipe.name}'


class ShoppingCart(models.Model):
    user = models.ForeignKey(
        User,
        related_name='shopping_cart',
        on_delete=models.CASCADE,
        verbose_name='user'
    )
    recipe = models.ForeignKey(
        Recipe,
        related_name='in_shoping_cart',
        on_delete=models.CASCADE,
        verbose_name='recipe'
    )
    added_to_shoping_cart = models.DateTimeField(
        auto_now_add=True,
        verbose_name='added at'
    )

    class Meta:
        ordering = ('-id',)
        verbose_name = 'ShopingCart'
        verbose_name_plural = 'ShopingCarts'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_shoping_cart',
            )
        ]
