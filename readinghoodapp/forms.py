from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.contrib.auth.models import User
from django import forms
from .models import Post, Profile, Book, Community

class BookFilterForm(forms.Form):
    category = forms.MultipleChoiceField(choices=[(category, category) for category in Book.objects.values_list(
            'category',
            flat=True
        ).distinct()],
        required=False,
        widget=forms.CheckboxSelectMultiple()
    )


def post_form_factory(user):
    class PostForm(forms.ModelForm):
        body = forms.CharField(required=True,
                            widget=forms.widgets.Textarea(
                                attrs={
                                    "placeholder": "Enter your post here",
                                    "class":"form-control",
                                }
                            ),
                            label="",)

        class Meta:
            model = Post
            fields = ('community', 'body')

        def __init__(self, *args, **kwargs):
            super(PostForm, self).__init__(*args, **kwargs)
            self.fields['community'].required = False
            self.fields['community'].queryset = Community.objects.filter(members=user)

    return PostForm




class ProfilePicForm(forms.ModelForm):
    profile_image = forms.ImageField(label="Profile Picture")

    class Meta:
        model = Profile
        fields = ('profile_image',)


class SignUpForm(UserCreationForm):
    username = forms.CharField(label="", max_length=150, widget=forms.TextInput(attrs={'class':'form-control'}))
    email = forms.EmailField(label="Email address", widget=forms.TextInput(attrs={'class':'form-control'}))

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')

    def __init__(self, *args, **kwargs):
        super(SignUpForm, self).__init__(*args, **kwargs)

        self.fields['username'].widget.attrs['class'] = 'form-control'
        self.fields['username'].widget.attrs['placeholder'] = ''
        self.fields['username'].label = 'Username'
        self.fields['username'].help_text = '<span class="form-text text-muted"><small>Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.</small></span>'

        self.fields['password1'].widget.attrs['class'] = 'form-control'
        self.fields['password1'].widget.attrs['placeholder'] = ''
        self.fields['password1'].label = 'Password'
        self.fields['password1'].help_text = '<ul class="form-text text-muted small"><li>Your password can\'t be too similar to your other personal information.</li><li>Your password must contain at least 8 characters.</li><li>Your password can\'t be a commonly used password.</li><li>Your password can\'t be entirely numeric.</li></ul>'

        self.fields['password2'].widget.attrs['class'] = 'form-control'
        self.fields['password2'].widget.attrs['placeholder'] = ''
        self.fields['password2'].label = 'Re-enter password'
        self.fields['password2'].help_text = '<span class="form-text text-muted"><small>Enter the same password as before, for verification.</small></span>'


class EditProfileForm(UserChangeForm):
        def __init__(self, *args, **kwargs):
            super(EditProfileForm, self).__init__(*args, **kwargs)
            del self.fields['password']

        class Meta:
            model = User
            fields = ('email', 'first_name', 'last_name')


DELIVERY_CHOICES = [
    ('S', 'Standard'),
    ('E', 'Express'),
]


STATE_CHOICES = [
    ('ACT', 'Australian Capital Territory'),
    ('NSW', 'New South Wales'),
    ('NT', 'Northern Territory'),
    ('Q', 'Queensland'),
    ('SA', 'South Australia'),
    ('TAS', 'Tasmania'),
    ('VIC', 'Victoria'),
    ('WA', 'Western Australia'),
]


class CheckoutForm(forms.Form):
    #Shipping Address
    shipping_address1 = forms.CharField(required=False, widget=forms.TextInput(attrs={
        'placeholder': 'Address Line 1'
    }))
    shipping_address2 = forms.CharField(required=False, widget=forms.TextInput(attrs={
        'placeholder': 'Address Line 2'
    }))
    shipping_city = forms.CharField(required=False, widget=forms.TextInput(attrs={
        'placeholder': 'City'
    }))
    shipping_state = forms.CharField(required=False, label='State', widget=forms.Select(choices=STATE_CHOICES))
    shipping_postcode = forms.CharField(required=False, widget=forms.TextInput(attrs={
        'placeholder': 'Postcode'
    }))

    #Billing Address
    billing_address1 = forms.CharField(required=False, widget=forms.TextInput(attrs={
        'placeholder': 'Address Line 1'
    }))
    billing_address2 = forms.CharField(required=False, widget=forms.TextInput(attrs={
        'placeholder': 'Address Line 2'
    }))
    billing_city = forms.CharField(required=False, widget=forms.TextInput(attrs={
        'placeholder': 'City'
    }))
    billing_state = forms.CharField(required=False, label='State', widget=forms.Select(choices=STATE_CHOICES))
    billing_postcode = forms.CharField(required=False, widget=forms.TextInput(attrs={
        'placeholder': 'Postcode'
    }))

    #Saving and Autofilling Options
    same_billing_address = forms.BooleanField(required=False)
    set_default_shipping = forms.BooleanField(required=False)
    use_default_shipping = forms.BooleanField(required=False)
    set_default_billing = forms.BooleanField(required=False)
    use_default_billing = forms.BooleanField(required=False)

    #Delivery Choice
    delivery_options = forms.ChoiceField(widget=forms.RadioSelect, choices=DELIVERY_CHOICES)


class PaymentForm(forms.Form):
    card_name = forms.CharField(max_length=100,
                                widget=forms.TextInput(attrs={'placeholder': 'Card Holder Name'}),
                                error_messages={'required':"Enter the card holder's name"})
    card_number = forms.CharField(min_length=16, max_length=16,
                                  widget=forms.TextInput(attrs={'placeholder': '0000 0000 0000 0000'}),
                                  error_messages={'required':"Enter the card number (must be 16 digits)."})
    expiry_date = forms.DateField(input_formats={"%m/%y", "%n/%y", "%m-%y", "%n-%y",},
                                  widget=forms.TextInput(attrs={'placeholder': 'MM/YY or MM-YY'}),
                                  error_messages={'required':"Enter a valid expiry date."})
    security_code = forms.CharField(min_length=3, max_length=3,
                                    widget=forms.TextInput(attrs={'placeholder': '000'}),
                                    error_messages={'required':"Enter a valid security code (the 3 digits can be found on the back of the card)."})
