from django import forms
from .models import Users

class UserRegisterForm(forms.ModelForm):
    """
    A form that creates a user in the Users table (mySQL database: readinghood), with no privileges, 
    from the given username and password.
    """
    error_messages = {
        'password_mismatch': ("The two password fields didn't match."),
    }
    username = forms.CharField(label=("Username"),
                               widget=forms.TextInput)
    password1 = forms.CharField(label=("Password"),
                                widget=forms.PasswordInput)
    password2 = forms.CharField(label=("Password confirmation"),
                                widget=forms.PasswordInput,
                                help_text=("Enter the same password as above, for verification."))
    emailaddress = forms.EmailField(label=("Email Address"), 
                             widget=forms.EmailInput)

    class Meta:
        model = Users
        fields = ["username", ]

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError(
                self.error_messages['password_mismatch'],
                code='password_mismatch',
            )
        return password2

    def save(self, commit=True):
        username = self.cleaned_data.get("username")
        password = self.cleaned_data.get("password1")
        emailaddress = self.cleaned_data.get("emailaddress")
        user = Users.objects.create(username=username, password=password, emailaddress=emailaddress)
        #user.set_password(self.cleaned_data["password1"])
        #if commit:
            #user.save()
        return user
    
    