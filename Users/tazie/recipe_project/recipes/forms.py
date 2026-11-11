from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django import forms
from django.forms import inlineformset_factory
from .models import Recipe, Ingredient, RecipeIngredient

# Форма регистрации
class RegisterForm(UserCreationForm):
    username = forms.CharField(
        label="Имя пользователя",
        help_text="",
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    password1 = forms.CharField(
        label="Пароль",
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )
    password2 = forms.CharField(
        label="Подтверждение пароля",
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('username',)

# Форма входа
class LoginForm(AuthenticationForm):
    username = forms.CharField(
        label="Имя пользователя",
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    password = forms.CharField(
        label="Пароль",
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )

# Форма создания рецепта
class RecipeForm(forms.ModelForm):
    class Meta:
        model = Recipe
        fields = ['title', 'description', 'cooking_time', 'servings', 'image']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 5}),
            'cooking_time': forms.NumberInput(attrs={'class': 'form-control'}),
            'servings': forms.NumberInput(attrs={'class': 'form-control'}),
        }
        labels = {
            'title': 'Название блюда',
            'description': 'Шаги приготовления',
            'cooking_time': 'Время приготовления (мин.)',
            'servings': 'Количество порций',
            'image': 'Фото блюда',
        }

# Форма для связи ингредиента и количества
class RecipeIngredientForm(forms.ModelForm):
    new_ingredient_name = forms.CharField(
        required=False,
        label="Или введите новый ингредиент",
        widget=forms.TextInput(attrs={'placeholder': 'Например: творог', 'class': 'form-control'})
    )

    class Meta:
        model = RecipeIngredient
        fields = ['ingredient', 'new_ingredient_name', 'amount']
        widgets = {
            'ingredient': forms.Select(attrs={'class': 'form-control'}),
            'amount': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Например: 200 г'})
        }
        labels = {
            'ingredient': 'Выберите существующий ингредиент',
            'amount': 'Количество / дозировка'
        }

# Фабрика формасетов (обязательно должна быть здесь!)
RecipeIngredientFormSet = inlineformset_factory(
    Recipe,
    RecipeIngredient,
    form=RecipeIngredientForm,
    fields=['ingredient', 'new_ingredient_name', 'amount'],
    extra=3,
    can_delete=True
)