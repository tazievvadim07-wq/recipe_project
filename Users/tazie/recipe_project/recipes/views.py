from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from .forms import RegisterForm, LoginForm, RecipeForm, RecipeIngredientFormSet
from .models import Recipe, Favorite, RecipeIngredient

def recipe_list(request):
    recipes = Recipe.objects.all()
    return render(request, 'recipes/recipe_list.html', {'recipes': recipes})

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
            
            # Сохраняем ингредиенты и обрабатываем новые
            instances = formset.save(commit=False)
            for instance in instances:
                instance.recipe = recipe
                
                # Если пользователь ввел название нового ингредиента вручную
                new_name = formset.cleaned_data[formset.forms.index(instance.form)].get('new_ingredient_name')
                if new_name:
                    # Создаем ингредиент в базе или берем существующий с таким же именем
                    ingredient_obj, created = Ingredient.objects.get_or_create(name=new_name.strip().capitalize())
                    instance.ingredient = ingredient_obj
                
                if instance.ingredient: # Сохраняем связь только если ингредиент выбран/создан
                    instance.save()
                    
            for obj in formset.deleted_objects:
                obj.delete()
                
            return redirect('recipe_detail', pk=recipe.pk)
    else:
        form = RecipeForm()
        formset = RecipeIngredientFormSet()
        
    return render(request, 'recipes/add_recipe.html', {
        'form': form,
        'formset': formset
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