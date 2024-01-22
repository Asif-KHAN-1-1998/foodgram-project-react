from django.urls import path
from .views import *

urlpatterns = [
    path('tags/', TagList.as_view()),
    path('tags/<int:pk>/', TagDetail.as_view()),
    path('recipes/', RecipeListCreate.as_view()),
    path('recipes/<int:pk>/', RecipeRetrieveUpdateDelete.as_view()),
    path('recipes/<int:recipe>/favorite/', FavoriteCreateDelete.as_view()),
    path('recipes/<int:recipe>/shopping_cart/',
         ShoppingCartCreateDelete.as_view()),
    path('recipes/download_shopping_cart/', DownloadShoppingCart.as_view()),
    path('ingredient/', IngredientList.as_view()),
    path('ingredient/<int:pk>/', IngredientDetail.as_view()),
    path('subscriptions/', SubscribeList.as_view()),
    path('users/<int:author>/subscribe/', SubscribeCreateDelete.as_view()),
    path('favourites/', FavoriteListView.as_view()),
]
