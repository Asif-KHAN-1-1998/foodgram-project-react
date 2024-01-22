from rest_framework import generics, permissions, status, filters
from rest_framework.response import Response
from .serializers import *
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q
import django_filters
from .filters import TagFilter, IngredientFilter, RecipesFilter
from recipes.models import Ingredient, Recipe, Tag, Favourite, Subscription, ShoppingCart
from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from django.db.models import Sum
from rest_framework.views import APIView


class TagList(generics.ListAPIView):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None
    permission_classes = [permissions.AllowAny]
    filter_backends = [
        django_filters.rest_framework.DjangoFilterBackend, filters.SearchFilter]
    filterset_class = TagFilter
    search_fields = ['^name',]


class TagDetail(generics.RetrieveAPIView):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [permissions.AllowAny]


class IngredientList(generics.ListAPIView):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    pagination_class = None
    permission_classes = [permissions.AllowAny]
    filter_backends = [
        django_filters.rest_framework.DjangoFilterBackend, filters.SearchFilter]
    filterset_class = IngredientFilter


class IngredientDetail(generics.RetrieveAPIView):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = [permissions.AllowAny]


class RecipeListCreate(generics.ListCreateAPIView):
    queryset = Recipe.objects.all()
    serializer_class = RecipeGetSerializer
    pagination_class = PageNumberPagination
    permission_classes = [permissions.IsAuthenticatedOrReadOnly,]
    filter_backends = [
        django_filters.rest_framework.DjangoFilterBackend, filters.SearchFilter]
    filterset_class = RecipesFilter
    search_fields = ['^name',]

    def get_queryset(self):
        is_in_cart = self.request.query_params.get('is_in_shopping_cart')
        if is_in_cart:
            return Recipe.objects.all()
        tags = self.request.query_params.getlist('tags')
        return Recipe.objects.filter(tags__slug__in=tags).distinct()

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return RecipeGetSerializer
        return RecipeCreateSerializer

    def create(self, request, *args, **kwargs):
        serializer = RecipeCreateSerializer(
            data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save(author=request.user)
        sz = RecipeGetSerializer(
            serializer.instance, many=False, context={'request': request})
        return Response(sz.data, status=status.HTTP_201_CREATED)


class RecipeRetrieveUpdateDelete(generics.RetrieveUpdateDestroyAPIView):
    queryset = Recipe.objects.all()
    serializer_class = RecipeGetSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly,]

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return RecipeGetSerializer
        return RecipeCreateSerializer

    def update(self, request, *args, **kwargs):
        obj = self.get_object()
        serializer = RecipeCreateSerializer(
            instance=obj, data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save(author=request.user)
        sz = RecipeGetSerializer(
            serializer.instance, many=False, context={'request': request})
        return Response(sz.data, status=status.HTTP_200_OK)


class FavoriteListView(generics.ListAPIView):
    queryset = Favourite.objects.all()
    serializer_class = FavouriteSerializer
    pagination_class = None
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        fvs = Favourite.objects.filter(
            user=self.request.user).values_list('recipe', flat=True)
        tags = self.request.query_params.getlist('tags')
        if tags:
            return Recipe.objects.filter(Q(id__in=fvs) & Q(tags__slug__in=tags)).distinct()
        return Recipe.objects.filter(id__in=fvs)[:0]

    def list(self, request, *args, **kwargs):
        qs = self.get_queryset()
        serializer = RecipeGetSerializer(
            qs, many=True, context={'request': request})
        return Response({'results': serializer.data, 'count': self.get_queryset().count()})


class FavoriteCreateDelete(generics.CreateAPIView, generics.DestroyAPIView):
    queryset = Favourite.objects.all()
    serializer_class = FavouriteSerializer
    pagination_class = None
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'recipe'

    def create(self, request, *args, **kwargs):
        recipe = self.kwargs.get('recipe')
        if not recipe:
            return Response({"errors": "Ошибка добавления в избранное (Например, когда рецепт уже есть в избранном)"}, status=status.HTTP_400_BAD_REQUEST)
        recipe = get_object_or_404(Recipe, id=recipe)
        favourite = Favourite.objects.filter(
            user=request.user, recipe=recipe)
        if favourite.exists():
            return Response({"errors": "Ошибка добавления в избранное (Например, когда рецепт уже есть в избранном)"}, status=status.HTTP_400_BAD_REQUEST)
        favourite = Favourite.objects.create(
            user=request.user, recipe=recipe)
        serializer = FavouriteSerializer(recipe, many=False)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def destroy(self, request, *args, **kwargs):
        recipe = self.kwargs.get('recipe')
        if not recipe:
            return Response({"errors": "Ошибка удаления из избранного (Например, когда рецепт уже есть в избранном)"}, status=status.HTTP_400_BAD_REQUEST)
        recipe = get_object_or_404(Recipe, id=recipe)
        favourite = Favourite.objects.filter(
            user=request.user, recipe=recipe)
        if not favourite.exists():
            return Response({"errors": "Ошибка удаления из избранного (Например, когда рецепт уже есть в избранном)"}, status=status.HTTP_400_BAD_REQUEST)
        favourite.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class ShoppingCartCreateDelete(generics.CreateAPIView, generics.DestroyAPIView):
    queryset = ShoppingCart.objects.all()
    serializer_class = FavouriteSerializer
    pagination_class = None
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'recipe'

    def create(self, request, *args, **kwargs):
        recipe = self.kwargs.get('recipe')
        if not recipe:
            return Response({"errors": "Ошибка добавления в список покупок (Например, когда рецепт уже есть в списке покупок)"}, status=status.HTTP_400_BAD_REQUEST)
        recipe = get_object_or_404(Recipe, id=recipe)
        shopping_cart = ShoppingCart.objects.filter(
            user=request.user, recipe=recipe)
        if shopping_cart.exists():
            return Response({"errors": "Ошибка добавления в список покупок (Например, когда рецепт уже есть в списке покупок)"}, status=status.HTTP_400_BAD_REQUEST)
        shopping_cart = ShoppingCart.objects.create(
            user=request.user, recipe=recipe)
        serializer = FavouriteSerializer(recipe, many=False)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def destroy(self, request, *args, **kwargs):
        recipe = self.kwargs.get('recipe')
        if not recipe:
            return Response({"errors": "Ошибка удаления из списка покупок (Например, когда рецепт уже есть в списке покупок)"}, status=status.HTTP_400_BAD_REQUEST)
        recipe = get_object_or_404(Recipe, id=recipe)
        shopping_cart = ShoppingCart.objects.filter(
            user=request.user, recipe=recipe)
        if not shopping_cart.exists():
            return Response({"errors": "Ошибка удаления из списка покупок (Например, когда рецепт уже есть в списке покупок)"}, status=status.HTTP_400_BAD_REQUEST)
        shopping_cart.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class DownloadShoppingCart(APIView):
    queryset = ShoppingCart.objects.all()
    serializer_class = FavouriteSerializer
    pagination_class = None
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        ingredients = IngredientsInRecipe.objects.filter(
            recipe__carts__user=request.user
        ).values(
            'ingredient__name', 'ingredient__measurement_unit'
        ).annotate(ingredient_amount=Sum('amount'))
        shopping_list = ['Список покупок:\n']
        for ingredient in ingredients:
            name = ingredient['ingredient__name']
            unit = ingredient['ingredient__measurement_unit']
            amount = ingredient['ingredient_amount']
            shopping_list.append(f'\n{name} - {amount}, {unit}')
        response = HttpResponse(shopping_list, content_type='text/plain')
        response['Content-Disposition'] = \
            'attachment; filename="shopping_cart.txt"'
        return response


class SubscribeList(generics.ListAPIView):
    queryset = Subscription.objects.all()
    serializer_class = SubcribeList
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [
        django_filters.rest_framework.DjangoFilterBackend, filters.SearchFilter]

    def get_queryset(self):
        recipes_limit = self.request.query_params.get('recipes_limit')
        if recipes_limit:
            return Subscription.objects.filter(user=self.request.user)[:int(recipes_limit)]
        user = self.request.user
        return Subscription.objects.filter(user=user)


class SubscribeCreateDelete(generics.CreateAPIView, generics.DestroyAPIView):
    queryset = Subscription.objects.all()
    serializer_class = SubscriptionCreateSerializer
    pagination_class = None
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'author'

    def create(self, request, *args, **kwargs):
        author = self.kwargs.get('author')
        if not author:
            return Response({"errors": "Not author"}, status=status.HTTP_400_BAD_REQUEST)
        author = get_object_or_404(User, id=author)
        subscribe = Subscription.objects.filter(
            user=request.user, author=author)
        if subscribe.exists():
            return Response({"errors": "Ошибка подписки (Например, когда подписка уже существует)"}, status=status.HTTP_400_BAD_REQUEST)
        subscribe = Subscription.objects.create(
            user=request.user, author=author)
        serializer = SubcribeList(
            subscribe, many=False, context={'request': request})
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)
