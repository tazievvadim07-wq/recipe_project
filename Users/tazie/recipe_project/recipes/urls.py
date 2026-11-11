from django.urls import path
from .views import (
    recipe_list, 
    recipe_detail, 
    register_view, 
    login_view, 
    logout_view,
    add_recipe_view,
    toggle_favorite,
    favorites_list_view
)

urlpatterns = [
    path('', recipe_list, name='recipe_list'),
    path('recipe/<int:pk>/', recipe_detail, name='recipe_detail'),
    path('recipe/add/', add_recipe_view, name='add_recipe'),
    path('recipe/<int:pk>/favorite/', toggle_favorite, name='toggle_favorite'),
    path('favorites/', favorites_list_view, name='favorites_list'),
    path('register/', register_view, name='register'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
]