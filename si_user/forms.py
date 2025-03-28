from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, UserChangeForm
from django.contrib.auth.models import User
from django import forms
from django.forms import ModelForm
from django.forms.widgets import PasswordInput, TextInput
from . models import UserDetail
# - update user form
class UserDetailForm(forms.ModelForm):
    class Meta:
        model = UserDetail
        fields = ['phone']


class UpdateUserForm(UserChangeForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']


# - register a user
class CreateUserForm(UserCreationForm):
    
    class Meta:

        model = User
        fields = ['username', 'email', 'password1', 'password2']

# - login authentication
class LoginForm(AuthenticationForm):

    username = forms.CharField(widget=TextInput())
    password = forms.CharField(widget=PasswordInput())
    


