from django.contrib import admin
from django.contrib.auth.models import Group, User
from .models import *


# Combine profile into user info
class ProfileInline(admin.StackedInline):
    model = Profile


class UserAdmin(admin.ModelAdmin):
    model = User
    readonly_fields = ('id',)
    inlines = [ProfileInline]

class BookAdmin(admin.ModelAdmin):
    model = Book
    list_display = ('title', 'bookid', 'price', 'average_rating','publisher')
    search_fields = ['isbn','title']

class AddressAdmin(admin.ModelAdmin):
    model = Address
    list_display = ('user', 'city', 'state', 'postcode')

class CartItemAdmin(admin.ModelAdmin):
    list_display = ('cartid', 'bookid', 'quantity', 'ordered')

class CartItemInline(admin.TabularInline):
    model = CartItem

class ShoppingCartAdmin(admin.ModelAdmin):
    model = ShoppingCart
    list_display = ('cartid', 'userid', 'ordered')
    inlines = [
        CartItemInline,
    ]

# class BookCategoryAdmin(admin.ModelAdmin):
#     list_display = ('categoryid', 'bookid')

# class BookCategoryInline(admin.TabularInline):
#     model = BookCategory

# class CategoriesAdmin(admin.ModelAdmin):
#     model = Categories
#     list_display = ('name', 'catedescription')

#     inlines = [
#         BookCategoryInline,
#     ]

admin.site.unregister(User)

# Register tables

admin.site.register(User, UserAdmin)
admin.site.register(Book, BookAdmin)
admin.site.register(Community)
admin.site.register(RatingsReviews)
admin.site.register(Address, AddressAdmin)
admin.site.register(Payment)
admin.site.register(Post)
admin.site.register(Users)

# admin.site.register(Categories, CategoriesAdmin)
# admin.site.register(BookCategory, BookCategoryAdmin)

admin.site.register(ShoppingCart, ShoppingCartAdmin)
admin.site.register(CartItem, CartItemAdmin)
