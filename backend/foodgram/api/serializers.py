from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.shortcuts import get_object_or_404
from djoser.serializers import (UserCreateSerializer
                                as DjoserUserCreateSerializer)
from drf_extra_fields.fields import Base64ImageField
from recipes import validators
from recipes.models import (CustomUser, Ingredient, IngredientsInRecipe,
                            Recipe, Subscription, Tag)
from rest_framework import serializers

User = CustomUser
MAX = 32000
MIN = 1


class UserCreateSerializer(DjoserUserCreateSerializer):
    class Meta(DjoserUserCreateSerializer.Meta):
        model = User
        fields = (
            'id',
            'email',
            'username',
            'password',
            'first_name',
            'last_name',
        )


class UserSerializer(serializers.ModelSerializer):
    username = serializers.CharField(
        max_length=150,
        required=True,
        validators=(validators.validate_username, ),
    )
    email = serializers.EmailField(
        max_length=254,
        required=True,
    )

    is_subscribed = serializers.SerializerMethodField()

    def get_is_subscribed(self, obj):
        request = self.context['request']
        if request.user.is_authenticated:
            return request.user.follower.filter(author=obj
                                                ).exists()
        return False

    class Meta:
        model = User
        fields = (
            'id',
            'email',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',)


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = '__all__'


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = fields = '__all__'


class IngredientWriteSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField()
    amount = serializers.IntegerField()

    class Meta:
        model = Ingredient
        fields = ['id', 'amount']


class IngredientRecipeSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField()
    measurement_unit = serializers.CharField(
        source='ingredient.measurement_unit')
    name = serializers.CharField(source='ingredient.name')
    amount = serializers.IntegerField(
        validators=[MinValueValidator(MIN), MaxValueValidator(MAX)])

    class Meta:
        model = IngredientsInRecipe
        fields = ('id', 'ingredient', 'name', 'measurement_unit', 'amount',)


class RecipeGetSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True, read_only=True)
    author = UserSerializer(read_only=True)
    ingredients = IngredientWriteSerializer(many=True, read_only=True)
    image = serializers.SerializerMethodField()
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    ingredients = serializers.SerializerMethodField()
    count = serializers.SerializerMethodField()

    def get_count(self, obj):
        return 1

    def get_image(self, obj):
        if obj.image:
            return f"{settings.BASE_URL}{obj.image.url}"
        return None

    def get_is_favorited(self, obj):
        request = self.context['request']

        if request.user.is_authenticated:
            return request.user.favourites.filter(recipe=obj
                                                  ).exists()
        return False

    def get_is_in_shopping_cart(self, obj):
        request = self.context['request']

        if request.user.is_authenticated:
            return request.user.shopping_cart.filter(recipe=obj
                                                     ).exists()
        return False

    def get_ingredients(self, obj):
        qs = obj.recipe.all()
        return IngredientRecipeSerializer(qs, many=True).data

    class Meta:
        model = Recipe
        fields = '__all__'


class RecipeCreateSerializer(serializers.ModelSerializer):
    image = Base64ImageField(max_length=None, use_url=True, required=False)
    author = serializers.PrimaryKeyRelatedField(
        read_only=True,
        default=serializers.CurrentUserDefault(),
    )
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        many=True,
    )
    ingredients = serializers.ListField(
        child=IngredientWriteSerializer(),
    )
    cooking_time = serializers.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(32000)])

    class Meta:
        model = Recipe
        fields = '__all__'

    def validate(self, data):
        ingredients = self.initial_data.get('ingredients', [])
        if not ingredients:  # Пустоту можно проверить без len
            raise serializers.ValidationError(
                'Добавьте хотя бы один ингредиент'
            )
        return data

    def ingredients_create(self, ingredients, recipe):
        ingredients_in_recipe_list = []
        for ingredient in ingredients:
            ingredient_obj = get_object_or_404(Ingredient, id=ingredient['id'])
            ingredients_in_recipe_list.append(IngredientsInRecipe(
                recipe=recipe,
                ingredient=ingredient_obj,
                amount=ingredient['amount'],
            ))
        IngredientsInRecipe.objects.bulk_create(ingredients_in_recipe_list)

    def create(self, validated_data):
        ingredients_data = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        image = validated_data.get('image')

        if not image:
            raise serializers.ValidationError('Добавьте изображение')

        recipe = Recipe.objects.create(**validated_data)
        recipe.tags.set(tags)

        self.ingredients_create(ingredients_data, recipe)

        return recipe

    def update(self, instance, validated_data):
        ingredients_data = validated_data.pop('ingredients', [])
        tags = validated_data.pop('tags', [])
        instance.tags.set(tags)
        IngredientsInRecipe.objects.filter(recipe=instance).delete()
        self.ingredients_create(ingredients_data, instance)

        return super().update(instance, validated_data)

    def update(self, instance, validated_data):
        ingredients_data = validated_data.pop('ingredients', [])
        tags = validated_data.pop('tags', [])
        instance.tags.set(tags)
        IngredientsInRecipe.objects.filter(recipe=instance).delete()
        ingredients_in_recipe_list = []

        for ingredient_data in ingredients_data:
            ingredient_obj = get_object_or_404(
                Ingredient, id=ingredient_data['id'])

            ingredients_in_recipe_list.append(IngredientsInRecipe(
                recipe=instance,
                ingredient=ingredient_obj,
                amount=ingredient_data['amount'],
            ))
        IngredientsInRecipe.objects.bulk_create(ingredients_in_recipe_list)

        return super().update(instance, validated_data)


class SubscriptionCreateSerializer(serializers.ModelSerializer):

    class Meta:
        model = Subscription
        fields = ('author', )


class SubcribeListSerializer(serializers.ModelSerializer):
    email = serializers.ReadOnlyField(source='author.email')
    id = serializers.ReadOnlyField(source='author.id')
    username = serializers.ReadOnlyField(source='author.username')
    first_name = serializers.ReadOnlyField(source='author.first_name')
    last_name = serializers.ReadOnlyField(source='author.last_name')
    recipes_count = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()

    def get_recipes(self, obj):
        recipes = obj.author.recipes.all()
        return RecipeGetSerializer(recipes,
                                   many=True,
                                   context={
                                       'request': self.context[
                                           'request'
                                       ]
                                   }
                                   ).data

    def get_recipes_count(self, obj):
        return obj.author.recipes.count()

    class Meta:
        model = Subscription
        fields = ('email',
                  'id',
                  'username',
                  'first_name',
                  'last_name',
                  'recipes_count',
                  'recipes')


class FavouriteSerializer(serializers.Serializer):
    id = serializers.ReadOnlyField()
    name = serializers.ReadOnlyField()
    image = serializers.SerializerMethodField(read_only=True)
    cooking_time = serializers.ReadOnlyField()

    def get_image(self, obj):
        return f"{settings.BASE_URL}{obj.image.url}"
