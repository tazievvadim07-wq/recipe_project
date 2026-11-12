from django.db import models
from django.contrib.auth.models import User

# 1. Ингредиент
class Ingredient(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name="Название ингредиента")

    def __str__(self):
        return self.name

# 2. Рецепт
class Recipe(models.Model):
    title = models.CharField(max_length=200, verbose_name="Название блюда")
    description = models.TextField(verbose_name="Шаги приготовления")
    cooking_time = models.PositiveIntegerField(verbose_name="Время приготовления (минут)")
    servings = models.PositiveIntegerField(verbose_name="Количество порций")
    image = models.ImageField(upload_to='recipes/', blank=True, null=True, verbose_name="Фото блюда")
    
    # Автор рецепта (теперь любой залогиненный юзер станет автором)
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='recipes', verbose_name="Автор")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")

    def __str__(self):
        return self.title

# 3. Связь рецепта и ингредиента с указанием количества
class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(Recipe, related_name='recipe_ingredients', on_delete=models.CASCADE)
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE)
    quantity = models.FloatField(default=1.0) # Числовое количество (например: 200)
    unit = models.CharField(max_length=30, blank=True, default='') # Единица измерения (например: г, шт, мл)

    def __str__(self):
        return f"{self.ingredient.name} — {self.quantity} {self.unit}"

# 4. Избранные рецепты (Сохраненные пользователем)
class Favorite(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='favorites', verbose_name="Пользователь")
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, related_name='favorited_by', verbose_name="Рецепт")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'recipe') # Чтобы пользователь не мог сохранить один рецепт дважды

    def __str__(self):
        return f"{self.user.username} -> {self.recipe.title}"