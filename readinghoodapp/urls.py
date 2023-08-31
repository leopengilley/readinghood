from django.urls import path
from . import views




urlpatterns = [

    # Home
    path('', views.home, name='home'),

    # Books
    path('search/', views.search, name='search'),
    path('catalogue', views.catalogue, name='catalogue'),
    path('book_detail/<int:bookid>', views.book_detail, name='book_detail'),
    path('book-info', views.book_info, name='book'),
    # path('categories', views.categories, name='categories'),

    # Social
    path('community', views.community, name='community'),

    # Profile
    path('signup/', views.register_user, name='signup'),
    path('login/', views.login_user, name='login'),
    path('logout/', views.logout_user, name='logout'),
    path('profile/<int:pk>', views.profile, name='profile'),
    path('edit_profile/', views.edit_profile, name='edit_profile'),
    path('mybooks',views.mybooks, name='mybooks'),

    # Cart
    path('add_to_cart/', views.add_to_cart, name='add_to_cart'),
    path('cart/', views.show_cart, name='showcart'),
    path('remove_from_cart/', views.remove_from_cart, name='remove_from_cart'),
    path('remove_single_item_from_cart/', views.remove_single_item_from_cart, name='remove_single_item_from_cart'),

    # Payment
    path('checkout/', views.CheckoutView.as_view(), name='checkout'),
    path('payment/', views.PaymentView.as_view(), name='payment'),
    path('thankyou/', views.PaymentConfirm.as_view(), name='thankyou'),

    # Misc
    path('reviews_test/', views.reviews_test, name='reviews_test'), #For testing

]
