from typing import Union, Type

from django.db import IntegrityError
from rest_framework import status
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from rest_framework.serializers import ValidationError
from rest_framework.viewsets import ModelViewSet

from api.serializers import RecipeInfoSerializer
from recipes.models import Recipe
from users.models import Follow


class CreateAndDeleteMixin:
    def create_and_delete_related(self: ModelViewSet,
                                  pk: int,
                                  klass: Union[Type[Follow]],
                                  create_failed_message: str,
                                  delete_failed_message: str,
                                  field_to_create_or_delete_name: str, ):
        self_qs_odj = get_object_or_404(self.get_queryset(), pk=pk)
        kwargs = {
            'user': self.request.user,
            field_to_create_or_delete_name: self_qs_odj
        }
        match self.request.method:
            case 'POST':
                try:
                    klass.objects.create(**kwargs)
                except IntegrityError:
                    raise ValidationError({'errors': create_failed_message})

                context = self.get_serializer_context()
                serializer = self.get_serializer_class()

                response = Response(
                    serializer(
                        instance=self_qs_odj, context=context
                    ).data,
                    status=status.HTTP_201_CREATED
                )

            case 'DELETE':
                klass_obj = klass.objects.filter(**kwargs).first()
                if klass_obj is None:
                    raise ValidationError({'errors': delete_failed_message})
                else:
                    klass_obj.delete()

                response = Response(status=status.HTTP_204_NO_CONTENT)

            case _:
                raise ValidationError({'errors': 'Неверный метод'})

        return response


class CustomRecipeModelViewSet(ModelViewSet):
    def add_obj(self, model, user, pk):
        recipe = get_object_or_404(Recipe, id=pk)
        if model.objects.filter(user=user, recipe=recipe).exists():
            return Response(
                {'errors': f'{recipe} уже добавлен в {model}'},
                status=status.HTTP_400_BAD_REQUEST
            )
        model.objects.create(user=user, recipe=recipe)
        serializer = RecipeInfoSerializer(recipe)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def del_obj(self, model, pk, user):
        recipe = get_object_or_404(Recipe, id=pk)
        if not model.objects.filter(user=user, recipe=recipe).exists():
            return Response(
                {'errors': f'{recipe} не добавлен в {model}'},
                status=status.HTTP_400_BAD_REQUEST
            )
        model.objects.get(user=user, recipe=recipe).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
