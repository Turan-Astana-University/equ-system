from django import forms


class CustomLoginForm(forms.Form):
    username = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'u-custom-font u-font-roboto-slab u-input u-input-rectangle',
            'placeholder': 'Логин',
            'id': 'username'
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'u-custom-font u-font-roboto-slab u-input u-input-rectangle',
            'placeholder': 'Пароль',
            'id': 'password'
        })
    )