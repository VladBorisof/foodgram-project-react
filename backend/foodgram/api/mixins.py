from rest_framework import status, viewsets
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response

from recipes.models import Recipe


class CustomRecipeModelViewSet(viewsets.ModelViewSet):
    def add_object(self, serializers, model, user, pk):
        recipe = get_object_or_404(Recipe, id=pk)
        if model.objects.filter(user=user, recipe=recipe).exists():
            return Response(
                {'errors': f'{recipe} уже добавлен в {model}'},
                status=status.HTTP_400_BAD_REQUEST
            )
        queryset = model.objects.create(user=user, recipe=recipe)
        serializer = serializers(queryset)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def del_object(self, model, pk, user):
        recipe = get_object_or_404(Recipe, id=pk)
        if not model.objects.filter(user=user, recipe=recipe).exists():
            return Response(
                {'errors': f'{recipe} не добавлен в {model}'},
                status=status.HTTP_400_BAD_REQUEST
            )
        model.objects.get(user=user, recipe=recipe).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
