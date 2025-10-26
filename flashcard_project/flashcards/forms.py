from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Deck, Card, UserProfile

class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=100)
    last_name = forms.CharField(max_length=100)
    
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'password1', 'password2']

class DeckForm(forms.ModelForm):
    class Meta:
        model = Deck
        fields = ['name', 'description']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Deck Name'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Description (optional)', 'rows': 3}),
        }

class CardForm(forms.ModelForm):
    class Meta:
        model = Card
        fields = ['front', 'back']
        widgets = {
            'front': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Front of the card', 'rows': 4}),
            'back': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Back of the card', 'rows': 4}),
        }

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['cards_per_day']
        widgets = {
            'cards_per_day': forms.NumberInput(attrs={'class': 'form-control', 'min': 1, 'max': 200}),
        }
