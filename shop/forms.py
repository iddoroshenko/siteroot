from django import forms


class LoginForm(forms.Form):
    username = forms.CharField(label='Username', max_length=64)
    password = forms.CharField(label='Password', max_length=128, widget=forms.PasswordInput)


class RegistrationForm(forms.Form):
    username = forms.CharField(label='Username', max_length=64)
    email = forms.EmailField(label='E-Mail', max_length=128)
    password = forms.CharField(label='Password', min_length=3, max_length=128, widget=forms.PasswordInput)
    password_again = forms.CharField(label='Password, again', min_length=3, max_length=128, widget=forms.PasswordInput)


class RatingForm(forms.Form):
    rating = forms.ChoiceField(widget=forms.RadioSelect, choices=[
                                ('1', 'terrible'),
                                ('2', 'bad'),
                                ('3', 'average'),
                                ('4', 'good'),
                                ('5', 'perfect')])


class MainPageSortForm(forms.Form):
    sort_by = forms.ChoiceField(widget=forms.RadioSelect, choices=[('1', 'title'), ('2', 'rating')], initial='1')
