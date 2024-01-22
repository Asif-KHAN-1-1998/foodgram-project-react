from colorfield.fields import ColorField
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from recipes import validators
from users.models import CustomUser
from django.conf import settings

User = CustomUser


class Tag(models.Model):
    """Модель тэга."""
    name = models.CharField(
        max_length=120,
        unique=True,
        verbose_name="Название тега",
        validators=(validators.validate_username, ),
    )
    color = ColorField()
    slug = models.SlugField(
        unique=True,
        verbose_name="Slug",
        validators=(validators.validate_slug, )
    )

    class Meta:
        verbose_name = "Тег"
        verbose_name_plural = "Теги"

    def __str__(self):
        return self.slug


class Ingredient(models.Model):
    """Модель ингредиента."""
    name = models.CharField(
        max_length=120,
        verbose_name="Название ингредиента",
        validators=(validators.validate_username, ),
    )
    measurement_unit = models.CharField(
        max_length=120,
        verbose_name="Мера измерения",
    )

    class Meta:
        verbose_name = "Ингредиент"
        verbose_name_plural = "Ингредиенты"

    def __str__(self):
        return self.name


class Recipe(models.Model):
    """Модель рецепта"""
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор', related_name='recipes',
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        verbose_name='Ингредиент',
    )
    tags = models.ManyToManyField(
        Tag,
        verbose_name='Tег', related_name='recipes',
    )
    image = models.ImageField(
        blank=True,
        null=True,
        verbose_name='Картинка',
        upload_to='recipe/',
    )
    name = models.CharField(
        max_length=120,
        verbose_name='Название рецепта',
    )
    text = models.TextField(
        verbose_name='Описание рецепта',
    )
    cooking_time = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(settings.MIN_TIME,
                                      message="Минимальное время - 1 минута"),
                    MaxValueValidator(settings.MAX_TIME,
                                      message="Максимальное время - 120 минут")],
        verbose_name='Время приготовления рецепта'
    )

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        return self.name


class Favorite(models.Model):
    """Модель рецептов в избранном."""
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='favorites',
        verbose_name='Рецепт',
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='favorites',
        verbose_name='Пользователь'
    )

    class Meta:
        ordering = ['user']
        verbose_name = ('Рецепт в избранном')
        verbose_name_plural = ('Рецепты в избранном')

    def __str__(self):
        return f'Рецепт {self.recipe} добавлен в избранное.'


class IngredientsInRecipe(models.Model):
    """Модель ингредиента в рецепте."""
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        verbose_name='Ингредиент',
        related_name='ingredient',
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепт',
        related_name='recipe',
    )
    amount = models.PositiveIntegerField()

    class Meta:
        verbose_name = 'Ингредиент в рецепте'
        verbose_name_plural = 'Ингредиенты в рецепте'

    def __str__(self):
        return self.ingredient.name


class Subscription(models.Model):
    """Модель подписки пользователя."""
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower',
        verbose_name='Подписчик',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following',
        verbose_name='Автор',
    )

    class Meta:
        ordering = ['-id']
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'

    def __str__(self):
        return f'Пользователь {self.user} подписался на автора {self.author}.'


class ShoppingCart(models.Model):
    """Модель списка покупок."""
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепт',
        related_name='carts',

    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Пользователь',
        related_name='shopping_cart',
    )

    class Meta:
        verbose_name = 'Список покупок'

    def __str__(self):
        return (f'Рецепт {self.recipe} добавлен в список покупок.')
