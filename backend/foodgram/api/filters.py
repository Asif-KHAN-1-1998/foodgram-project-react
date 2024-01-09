import django_filters
from django_filters import rest_framework as filters


from posts.models import Ingredient


class IngredientFilter(filters.FilterSet):
    name = django_filters.CharFilter(
        field_name='name', lookup_expr='icontains')

    class Meta:
        model = Ingredient
        fields = ['name', 'measurement_unit']
