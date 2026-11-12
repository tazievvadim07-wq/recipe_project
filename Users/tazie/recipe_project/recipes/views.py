from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from .forms import RegisterForm, LoginForm, RecipeForm, RecipeIngredientFormSet
from .models import Recipe, Ingredient, Favorite, RecipeIngredient

def recipe_list(request):
    all_ingredients = Ingredient.objects.all().order_by('name')
    
    # Получаем выбранные ID ингредиентов из GET-запроса
    selected_ids = request.GET.getlist('ingredients')
    selected_ids = [int(i) for i in selected_ids if i.isdigit()]
    
    # Читаем состояние галочки "докупать"
    allow_missing = request.GET.get('allow_missing') == 'on'
    
    recipes_qs = Recipe.objects.prefetch_related('recipe_ingredients__ingredient').all()
    filtered_recipes = []
    
    for recipe in recipes_qs:
        recipe_ingredients = recipe.recipe_ingredients.all()
        recipe_ing_ids = {ri.ingredient.id for ri in recipe_ingredients}
        selected_set = set(selected_ids)
        
        if not selected_ids:
            # Если ничего не выбрано, показываем все рецепты
            filtered_recipes.append({
                'recipe': recipe,
                'recipe_ingredients': recipe_ingredients,
                'missing_ids': set()
            })
        else:
            # Ингредиенты рецепта, которых у пользователя нет
            missing_ids = recipe_ing_ids - selected_set
            # Проверяем, есть ли вообще пересечение с тем, что выбрал пользователь
            has_common = not recipe_ing_ids.isdisjoint(selected_set)
            
            if has_common:
                if not allow_missing and len(missing_ids) > 0:
                    # Если галочка выключена, а в рецепте есть недостающие — пропускаем
                    continue
                filtered_recipes.append({
                    'recipe': recipe,
                    'recipe_ingredients': recipe_ingredients,
                    'missing_ids': missing_ids
                })
                
    return render(request, 'recipes/recipe_list.html', {
        'filtered_recipes': filtered_recipes,
        'all_ingredients': all_ingredients,
        'selected_ids': selected_ids,
        'allow_missing': allow_missing,
    })

def recipe_detail(request, pk):
    recipe = get_object_or_404(Recipe, pk=pk)
    return render(request, 'recipes/recipe_detail.html', {'recipe': recipe})

# Регистрация
def register_view(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('recipe_list')
    else:
        form = RegisterForm()
    return render(request, 'recipes/register.html', {'form': form})

# Вход
def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('recipe_list')
    else:
        form = LoginForm()
    return render(request, 'recipes/login.html', {'form': form})

# Выход
def logout_view(request):
    logout(request)
    return redirect('recipe_list')

# Добавление рецепта (доступно только вошедшим пользователям)
@login_required(login_url='login')
def add_recipe_view(request):
    if request.method == 'POST':
        form = RecipeForm(request.POST, request.FILES)
        formset = RecipeIngredientFormSet(request.POST)
        
        if form.is_valid() and formset.is_valid():
            recipe = form.save(commit=False)
            recipe.author = request.user
            recipe.save()
            
            for form_item in formset:
                if not form_item.cleaned_data or form_item.cleaned_data.get('DELETE', False):
                    continue
                
                ing_name = form_item.cleaned_data.get('ingredient_name')
                if not ing_name:
                    continue
                
                instance = form_item.save(commit=False)
                instance.recipe = recipe
                
                # Ищем или создаем ингредиент в базе по введенному тексту
                ingredient_obj, created = Ingredient.objects.get_or_create(
                    name=ing_name.strip().capitalize()
                )
                instance.ingredient = ingredient_obj
                instance.save()
                    
            return redirect('recipe_detail', pk=recipe.pk)
    else:
        form = RecipeForm()
        formset = RecipeIngredientFormSet()
        
    all_ingredients = Ingredient.objects.all()
    
    return render(request, 'recipes/add_recipe.html', {
        'form': form,
        'formset': formset,
        'all_ingredients': all_ingredients
    })
    
    return render(request, 'recipes/add_recipe.html', {
        'form': form,
        'formset': formset,
        'all_ingredients': all_ingredients
    })   
    
# Добавить/Удалить из избранного
@login_required(login_url='login')
def toggle_favorite(request, pk):
    recipe = get_object_or_404(Recipe, pk=pk)
    favorite, created = Favorite.objects.get_or_create(user=request.user, recipe=recipe)
    if not created:
        favorite.delete()
    return redirect('recipe_detail', pk=pk)

# Страница избранных рецептов пользователя
@login_required(login_url='login')
def favorites_list_view(request):
    favorites = Favorite.objects.filter(user=request.user).select_related('recipe')
    recipes = [fav.recipe for fav in favorites]
    return render(request, 'recipes/favorites.html', {'recipes': recipes})


def recipe_detail(request, pk):
    recipe = get_object_or_404(Recipe, pk=pk)
    
    # Проверяем, в избранном ли рецепт у текущего пользователя
    is_favorite = False
    if request.user.is_authenticated:
        is_favorite = Favorite.objects.filter(user=request.user, recipe=recipe).exists()
        
    return render(request, 'recipes/recipe_detail.html', {
        'recipe': recipe,
        'is_favorite': is_favorite
    })