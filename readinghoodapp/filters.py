import django_filters
from .models import Book
from django import forms

class BookFilter(django_filters.FilterSet):
    category = django_filters.ModelMultipleChoiceFilter(
        field_name='category',
        queryset=Book.objects.values_list('category', flat=True).distinct(),
        widget=forms.CheckboxSelectMultiple()
    )

    class Meta:
        model = Book
        fields = ['category']
