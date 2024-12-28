from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, UserChangeForm
from django.contrib.auth.models import User
from django import forms
from django.forms.widgets import PasswordInput, TextInput
from .models import subscription
#-- 
class subs_form():
    class Meta:
        model = subscription
        fields = ['monthly_free_credit', 'purchased_credit_balance', 'pay_as_you_go']
# - update user form
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
    