from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import AuthenticationForm
from django.forms import inlineformset_factory
from .models import Recipe, RecipeIngredient, Ingredient

# 1. Форма регистрации
class RegisterForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}), label="Пароль")
    
    class Meta:
        model = User
        fields = ['username', 'email', 'password']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
        }
        labels = {
            'username': 'Имя пользователя',
            'email': 'Электронная почта',
        }

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])
        if commit:
            user.save()
        return user


# 2. Форма входа (авторизации)
class LoginForm(AuthenticationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}))


# 3. Форма самого рецепта (название, описание, время, порции, фото)
class RecipeForm(forms.ModelForm):
    class Meta:
        model = Recipe
        fields = ['title', 'description', 'cooking_time', 'servings', 'image']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Например: Шакшука на скорую руку'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 5, 'placeholder': 'Опишите шаги приготовления...'}),
            'cooking_time': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'В минутах'}),
            'servings': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Количество порций'}),
            'image': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }
        labels = {
            'title': 'Название рецепта',
            'description': 'Описание и шаги',
            'cooking_time': 'Время приготовления (мин.)',
            'servings': 'Количество порций',
            'image': 'Фотография рецепта',
        }


# 4. Форма для ингредиента в рецепте (с поддержкой автодополнения datalist)
class RecipeIngredientForm(forms.ModelForm):
    ingredient_name = forms.CharField(
        label="Ингредиент",
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'list': 'ingredients-datalist',
            'placeholder': 'Например: Творог или яйца'
        })
    )

    class Meta:
        model = RecipeIngredient
        fields = ['quantity', 'unit']
        widgets = {
            'quantity': forms.NumberInput(attrs={'class': 'form-control', 'step': 'any', 'placeholder': '200'}),
            'unit': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'г, шт, ст. л.'})
        }
        labels = {
            'quantity': 'Количество (число)',
            'unit': 'Единица измерения'
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk and self.instance.ingredient:
            self.initial['ingredient_name'] = self.instance.ingredient.name


# 5. Фабрика формасета для динамических ингредиентов
RecipeIngredientFormSet = inlineformset_factory(
    Recipe,
    RecipeIngredient,
    form=RecipeIngredientForm,
    fields=['quantity', 'unit'],
    extra=1,
    can_delete=True
)