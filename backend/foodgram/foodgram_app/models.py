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
    ingredients = models.ManyToManyField(
        Ingredient,
        related_name='recipe',
        verbose_name='ingredients'
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


class FavouriteRecipe(models.Model):
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
    is_in_shopping_cart = models.BooleanField(
        default=False,
        verbose_name='is in shopping cart'
    )
    is_favorited = models.BooleanField(
        default=False,
        verbose_name='is in favorites'
    )
    added_to_favorites = models.DateTimeField(
        auto_now_add=True,
        verbose_name='added at'
    )
    added_to_shopping_cart = models.DateTimeField(
        auto_now_add=True,
        verbose_name='added at'
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_favorite_recipe',
            )
        ]
        verbose_name = ('Favorites',)
        verbose_name_plural = ('Favorites',)
        ordering = ['-added_to_favorites', '-added_to_shopping_cart']

    def __str__(self):
        return f'{self.user.username} - {self.recipe.name}'
