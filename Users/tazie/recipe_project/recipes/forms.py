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

# Форма для связи ингредиента, количества и единицы измерения
class RecipeIngredientForm(forms.ModelForm):
    new_ingredient_name = forms.CharField(
        required=False,
        label="Или введите новый ингредиент",
        widget=forms.TextInput(attrs={'placeholder': 'Например: творог', 'class': 'form-control'})
    )

    class Meta:
        model = RecipeIngredient
        fields = ['ingredient', 'new_ingredient_name', 'quantity', 'unit']
        widgets = {
            'ingredient': forms.Select(attrs={'class': 'form-control'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control', 'step': 'any', 'placeholder': 'Например: 200'}),
            'unit': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Например: г, шт, ст. л.'})
        }
        labels = {
            'ingredient': 'Выберите существующий ингредиент',
            'quantity': 'Количество (число)',
            'unit': 'Единица измерения (г, мл, шт)'
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['ingredient'].required = False  # <--- Делаем выбор из списка необязательным
        self.fields['ingredient'].empty_label = "— Не выбрано —"

    def clean(self):
        cleaned_data = super().clean()
        ingredient = cleaned_data.get('ingredient')
        new_name = cleaned_data.get('new_ingredient_name')

        # Если не выбран старый и не введен новый — это пустая строка, пропускаем
        if not ingredient and not new_name:
            return cleaned_data

        # Если что-то из двух заполнено, но не указано количество — ругаемся
        quantity = cleaned_data.get('quantity')
        if not quantity:
            self.add_error('quantity', 'Укажите количество для ингредиента.')

        return cleaned_data

# Фабрика формасетов
RecipeIngredientFormSet = inlineformset_factory(
    Recipe,
    RecipeIngredient,
    form=RecipeIngredientForm,
    fields=['ingredient', 'new_ingredient_name', 'quantity', 'unit'],
    extra=1,
    can_delete=True
)