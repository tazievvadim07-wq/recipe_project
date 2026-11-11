from django.contrib import admin
from .models import Ingredient, Recipe, RecipeIngredient

class RecipeIngredientInline(admin.TabularInline):
    model = RecipeIngredient
    extra = 1
    
@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'cooking_time', 'servings', 'created_at')
    search_fields = ('title', 'description', 'author__username')
    list_filter = ('author', 'created_at')
    inlines = [RecipeIngredientInline]
    
@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)
