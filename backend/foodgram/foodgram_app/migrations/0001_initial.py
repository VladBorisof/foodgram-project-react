# Generated by Django 2.2.16 on 2023-01-11 20:40

from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Ingredient',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200, verbose_name=('name',))),
                ('count', models.PositiveIntegerField(validators=[django.core.validators.MinValueValidator(1)], verbose_name=('count',))),
                ('unit', models.CharField(max_length=20, verbose_name=('unit',))),
            ],
        ),
        migrations.CreateModel(
            name='Tag',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200, unique=True, verbose_name=('name',))),
                ('color', models.CharField(default='4b0082', max_length=50, unique=True, verbose_name=('color',))),
                ('slug', models.SlugField(verbose_name=('slug',))),
            ],
            options={
                'verbose_name': ('Tag',),
                'verbose_name_plural': ('Tags',),
                'ordering': ['id'],
            },
        ),
        migrations.CreateModel(
            name='Recipe',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200, verbose_name=('name',))),
                ('image', models.ImageField(upload_to='recipes/', verbose_name=('image',))),
                ('text', models.TextField(verbose_name=('description',))),
                ('cooking_time', models.PositiveIntegerField(validators=[django.core.validators.MinValueValidator(1)], verbose_name=('cooking time',))),
                ('author', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='recipe', to=settings.AUTH_USER_MODEL, verbose_name=('author',))),
                ('ingredients', models.ManyToManyField(related_name='recipe', to='foodgram_app.Ingredient', verbose_name=('ingredients',))),
                ('tags', models.ManyToManyField(related_name='recipe', to='foodgram_app.Tag', verbose_name=('tags',))),
            ],
            options={
                'verbose_name': ('Recipe',),
                'verbose_name_plural': ('Recipes',),
            },
        ),
    ]
