from django.shortcuts import render, redirect
from .models import RatingsReviews, Address, Payment, Post
from .forms import SignUpForm, CheckoutForm, PaymentForm, post_form_factory, EditProfileForm, ProfilePicForm, BookFilterForm
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from .models import Book, Profile, CartItem, OrderItem, ShoppingCart, Users, Orders, Community
# , BookCategory
from django.shortcuts import get_object_or_404
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.views import View
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.core.paginator import Paginator
from .filters import BookFilter


# Home page
def home(request):
    top_review_list = RatingsReviews.objects.order_by('-rating')[:9]
    newest_releases = Book.objects.order_by('-publicationyear')[:10]
    return render(request, 'home.html', {'top_review_list':top_review_list,'newest_releases':newest_releases})


# Catalogue page
def catalogue(request):
    form = BookFilterForm(request.GET)
    queryset = Book.objects.all()
    f = BookFilter(request.GET, queryset=queryset)

    if form.is_valid():
        selected_categories = form.cleaned_data['category']
        if selected_categories:
            queryset = queryset.filter(category__in=selected_categories)

    paginator = Paginator(queryset, 9)  # Show 9 contacts per page.
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    return render(request, "catalogue.html", {"page_obj": page_obj, 'filter': f, 'form': form})

# Categories page
def categories(request):
    categories = BookCategory.objects.order_by('categoryid')
    category_list = [x for x in categories]
    for x in category_list:
        book = Book.objects.get(bookid=str(x.bookid))
        title = book.title
        x.title = title


    return render(request, 'categories.html', {'categories':categories})


# Community page
def community(request):
  if request.user.is_authenticated:
    form = post_form_factory(request.user)(request.POST or None)
    if request.method == "POST":
      if form.is_valid():
        post = form.save(commit=False)
        post.user = request.user
        post.save()
        messages.success(request, ("Your post has been made"))
        return redirect('community')

    profiles = Profile.objects.exclude(user=request.user)
    community = Community.objects.filter(members=request.user)
    posts = Post.objects.filter(community__in=community).order_by('-created_at')
    return render(request, 'community.html', {'profiles':profiles, 'posts':posts, 'form':form})
  else:
    messages.success(request, ("You must be logged in to access this page"))

    return redirect('home')


# Profile page
def profile(request, pk):
  if request.user.is_authenticated:
    profile = Profile.objects.get(user_id=pk)
    posts = Post.objects.filter(user_id=pk).order_by('-created_at')
    # Post form logic
    if request.method =="POST":
      # Get current user id
      current_user_profile = request.user.profile
      # Get form data
      action = request.POST['follow']
      # Decide to follow or unfollow
      if action == "unfollow":
        current_user_profile.follows.remove(profile)
      elif action == "follow":
        current_user_profile.follows.add(profile)
      # Save the profile
      current_user_profile.save()
    return render(request, 'profile.html', {'profile':profile, 'posts':posts})
  else:
    messages.success(request, ("You must be logged in to access this page"))
    return redirect('home')


# Edit profile
def edit_profile(request):
  if request.user.is_authenticated:
    profile_user = Profile.objects.get(user__id=request.user.id)
    user_form = EditProfileForm(request.POST or None, request.FILES or None, instance=request.user)
    profile_form = ProfilePicForm(request.POST or None, request.FILES or None, instance=profile_user)
    if user_form.is_valid() and profile_form.is_valid():
      user_form.save()
      profile_form.save()
      messages.success(request, ("Your profile has been updated"))
      return redirect('community')

    return render(request, 'edit_profile.html', {'user_form':user_form, 'profile_form':profile_form})
  else:
    messages.success(request, ("You must be logged in to access this page"))
    return redirect('home')


# My books page
def mybooks(request):
  return render(request, 'mybooks.html', {})


# Register user
def register_user(request):
  if request.user.is_authenticated:
    messages.success(request, ("You are already registered with Readinghood"))
    return redirect('home')
  else:
    if request.method == "POST":
      form = SignUpForm(request.POST)
      if form.is_valid():
        form.save()
        # After saving now authenticate and login
        username = form.cleaned_data['username']
        password = form.cleaned_data['password1']
        user = authenticate(username=username, password=password)
        login(request, user)
        messages.success(request, "You have successfully registered. Welcome to Readinghood")
        return redirect('home')
    else:
      form = SignUpForm()
      return render(request, 'signup.html', {'form': form})

  return render(request, 'signup.html', {'form': form})


# Login user
def login_user(request):
  if request.user.is_authenticated:
    messages.success(request, ("You are already logged in"))
    return redirect('home')
  else:
    if request.method == "POST":
      username = request.POST['username']
      password = request.POST['password']
      user = authenticate(request, username=username, password=password)
      if user is not None:
        login(request, user)
        messages.success(request, "You have been logged in")
        return redirect ('home')
      else:
        messages.success(request, "There was an error logging in, try again")
        return redirect ('login')
    else:
      return render(request, 'login.html', {})


# Logout user
def logout_user(request):
  logout(request)
  messages.success(request, "You are now logged out")
  return redirect ('home')


# Home page new releases
def book_info(request):
  newest_releases = Book.objects.order_by('-publicationyear')[0:1]
  return render(request,'book.html',{'newest_releases':newest_releases})


# For review testing
def reviews_test(request):
    top_review_list = RatingsReviews.objects.order_by('-rating')[:9]
    context = {'top_review_list':top_review_list}
    return render(request, 'reviews_test.html', context)


# Search Engine
def search(request):
    query = request.GET.get('search')
    results = []
    if query is not None:
        results = Book.objects.filter(Q(isbn__icontains=query) | Q(title__icontains=query) | Q(author__icontains=query))

    return render(request, 'search.html', {'query': query, 'results': results})


# Book details page
def book_detail(request, bookid):
   book_detail = get_object_or_404(Book, pk=bookid)
   return render(request, 'book_detail.html', {'book_detail':book_detail})


#Function to check if form fields are valid (i.e. not blank)
def is_valid_form(values):
    valid = True
    for field in values:
        if field == '':
            valid = False
    return valid

# Checkout (delivery/billing address)
class CheckoutView(View):
  def get(self, *args, **kwargs):
    try:
      #form
      form = CheckoutForm()

      #cart snippet
      user = self.request.user
      current_user = Users.objects.get(userid=user.id)

      cart_qs = ShoppingCart.objects.filter(
          userid = current_user,
          ordered = False
      )

      cart_item_qs = CartItem.objects.filter(
          ordered = False,
          cartid = cart_qs[0].cartid
      )

      cart_list = [x for x in cart_item_qs]
      for x in cart_list:
          book = Book.objects.get(bookid=str(x.bookid))
          title = book.title
          author = book.author
          cover = book.image_url
          price = book.price
          x.title = title
          x.author = author
          x.cover = cover
          x.price = price

      context = {
                  'form': form,
                  'cart': cart_list,
              }

      #Check for default addresses
      shipping_address_qs = Address.objects.filter(
        user=self.request.user,
        address_type='S',
        default=True
        )
      if shipping_address_qs.exists():
        context.update(
          {'default_shipping_address': shipping_address_qs[0]})

      billing_address_qs = Address.objects.filter(
        user=self.request.user,
        address_type='B',
        default=True
        )
      if billing_address_qs.exists():
        context.update(
          {'default_billing_address': billing_address_qs[0]})

      return render(self.request, 'checkout_delivery.html', context)
    except ObjectDoesNotExist:
       messages.success(self.request, "You do not have an active order")
       return redirect ('home')

  def post(self, *args, **kwargs):
    form = CheckoutForm(self.request.POST or None)

    try:
      user = self.request.user
      current_user = Users.objects.get(userid=user.id)

      cart_qs = ShoppingCart.objects.filter(
          userid = current_user,
          ordered = False
      )

      cart_item_qs = CartItem.objects.filter(
          ordered = False,
          cartid = cart_qs[0].cartid
      )

      if form.is_valid():
        use_default_shipping = form.cleaned_data.get('use_default_shipping')
        if use_default_shipping:
          print("Use the default shipping address")
          address_qs = Address.objects.filter(
             user = self.request.user,
             address_type = 'S',
             default = True,
             )
          if address_qs.exists():
             shipping_address = address_qs[0]
             #order.shipping_address = shipping_address
             #order.save()
          else:
            messages.success(self.request, "No default shipping address available")
            return redirect ('checkout')
        else:
          print("User is entering a new shipping address")
          shipping_address1 = form.cleaned_data.get('shipping_address1')
          shipping_address2 = form.cleaned_data.get('shipping_address2')
          shipping_city = form.cleaned_data.get('shipping_city')
          shipping_state  = form.cleaned_data.get('shipping_state')
          shipping_postcode = form.cleaned_data.get('shipping_postcode')
          if is_valid_form([shipping_address1, shipping_city, shipping_postcode]):
            shipping_address = Address(
              user = self.request.user,
              address1 = shipping_address1,
              address2 = shipping_address2,
              city = shipping_city,
              state = shipping_state,
              postcode = shipping_postcode,
              address_type = 'S',
            )
            shipping_address.save()

            #order.shipping_address = shipping_address
            #order.save()
            set_default_shipping = form.cleaned_data.get('set_default_shipping')
            if set_default_shipping:
              shipping_address.default = True
              shipping_address.save()
          else:
            messages.success(self.request, "Please fill in required shipping address fields")

        use_default_billing = form.cleaned_data.get('use_default_billing')
        same_billing_address = form.cleaned_data.get('same_billing_address')

        if same_billing_address:
          billing_address = shipping_address
          billing_address.pk = None
          billing_address.save()
          billing_address.address_type = 'B'
          billing_address.save()

          #order.billing_address = billing_address
          #order.save()
        elif use_default_billing:
          print("Use the default billing address")
          address_qs = Address.objects.filter(
             user = self.request.user,
             address_type = 'B',
             default = True,
             )
          if address_qs.exists():
             billing_address = address_qs[0]
             #order.billing_address = billing_address
             # #order.save()
          else:
            messages.success(self.request, "No default billing address available")
            return redirect ('checkout')
        else:
          print("User is entering new billing address")
          billing_address1 = form.cleaned_data.get('billing_address1')
          billing_address2 = form.cleaned_data.get('billing_address2')
          billing_city = form.cleaned_data.get('billing_city')
          billing_state  = form.cleaned_data.get('billing_state')
          billing_postcode = form.cleaned_data.get('billing_postcode')

          if is_valid_form([billing_address1, billing_city, billing_postcode]):
            shipping_address = Address(
               user = self.request.user,
               address1 = billing_address1,
               address2 = billing_address2,
               city = billing_city,
               state = billing_state,
               postcode = billing_postcode,
               address_type = 'B',
               )
            shipping_address.save()

            #order.shipping_address = shipping_address
            #order.save()

            set_default_billing = form.cleaned_data.get('set_default_billing')
            if set_default_billing:
              billing_address.default = True
              billing_address.save()

          else:
             messages.success(self.request, "Please fill in required billing address fields")

        delivery_option = form.cleaned_data.get('delivery_options')
        print("Delivery option:", delivery_option)
        if delivery_option == 'S':
           #TO DO: Add delivery fee to cart
           return redirect ('payment')
        elif delivery_option == 'E':
           #TO DO: Add delivery fee to cart
           return redirect ('payment')
        else:
           messages.success(self.request, "Invalid delivery option selected")
           return redirect ('checkout')
    except ObjectDoesNotExist:
       messages.success(self.request, "You do not have an active order")
       return redirect ('home')

# Checkout (payment)
class PaymentView(View):
  def get(self, *args, **kwargs):
    #Form
    form = PaymentForm()

    #Cart snippet
    user = self.request.user
    current_user = Users.objects.get(userid=user.id)

    cart_qs = ShoppingCart.objects.filter(
        userid = current_user,
        ordered = False
    )

    cart_item_qs = CartItem.objects.filter(
        ordered = False,
        cartid = cart_qs[0].cartid
    )

    cart_list = [x for x in cart_item_qs]
    for x in cart_list:
        book = Book.objects.get(bookid=str(x.bookid))
        title = book.title
        author = book.author
        cover = book.image_url
        price = book.price
        x.title = title
        x.author = author
        x.cover = cover
        x.price = price

    #Check delivery form has billing address
    shipping_address_qs = Address.objects.filter(
        user=self.request.user,
        address_type='B',
        )

    if shipping_address_qs.exists():
       context = {
          'form': form,
          'cart': cart_list,
       }
       return render(self.request, 'checkout_payment.html', context)
    else:
       messages.success(self.request, "You have not provided a billing address")
       return redirect ("checkout")

  def post(self, *args, **kwargs):
    form = PaymentForm(self.request.POST or None)

    if form.is_valid():
      card_name = form.cleaned_data.get('card_name')
      card_number = form.cleaned_data.get('card_number')
      expiry_date = form.cleaned_data.get('expiry_date')
      security_code = form.cleaned_data.get('security_code')

      card_info = Payment(
         user = self.request.user,
         card_name = card_name,
         card_number = card_number,
         expiry_date = expiry_date,
         security_code = security_code,
         )
      card_info.save()

      #TO DO: save shoppingcart as order in orders table
      #(for order history) and connect orderid to payment info

      messages.success(self.request, "Your order was successful!")
      return redirect ('thankyou')
    else:
      messages.success(self.request, "Unfortunately your form has errors. Please try again")
      return redirect ('payment')

# Payment confirmation
class PaymentConfirm(View):
  def payment_confirm(self, request, *args, **kwargs):

    shipping_address_qs = Address.objects.filter(
          user=self.request.user,
          address_type='S',
          )

    context = {
      'address': shipping_address_qs,

    }

    return render(request, 'purchase_confirmation.html')


# Cart
@login_required
def add_to_cart(request):

    user = request.user
    current_user = Users.objects.get(userid=user.id)

    if request.GET.get('bookid'):
        book_id = request.GET.get('bookid')
        book = Book.objects.get(bookid=book_id)
    else:
        book_id = request.GET.get('data')
        book = Book.objects.get(bookid=book_id)

    cart_qs = ShoppingCart.objects.filter(
        userid = current_user,
        ordered = False
    )

    if cart_qs.exists():
        cart_item_qs = CartItem.objects.filter(
            ordered = False,
            bookid = book,
            cartid = cart_qs[0].cartid
        )

        cart_check = cart_qs[0]
        cart_id = cart_check.cartid
        if cart_item_qs.exists():
            cart_item_check = cart_item_qs[0]
            cart_item_check.quantity += 1
            cart_item_check.save()
            messages.success(request, "Item quantity successfully increased.")
            if request.GET.get('bookid'):
                return redirect ('home')
            else:
                return redirect ('showcart')
        else:
            quantity = request.GET.get('quantity')
            cartItem = CartItem(cartid=cart_check, bookid=book, quantity=quantity)
            cartItem.save()
            messages.success(request, "Item successfully added.")
            return redirect ('home')
    else:
        cart = ShoppingCart(userid=current_user)
        cart.save()
        cartItem = CartItem(cartid=cart, bookid=book, quantity=1)
        cartItem.save()
        messages.success(request, "Item and cart successfully added.")
        return redirect ('home')


@login_required
def remove_from_cart(request):
    user = request.user
    current_user = Users.objects.get(userid=user.id)

    book_id = request.GET.get('data')
    book = Book.objects.get(bookid=book_id)

    cart_qs = ShoppingCart.objects.filter(
        userid = current_user,
        ordered = False
    )

    cart_item_qs = CartItem.objects.filter(
        ordered = False,
        bookid = book,
        cartid = cart_qs[0].cartid
    )

    if cart_qs.exists():
        cart_check = cart_qs[0]
        cart_id = cart_check.cartid
        if cart_item_qs.exists():
            cart_item_check = cart_item_qs[0]
            cart_item_check.delete()
            messages.success(request, "This item was removed from your cart.")
            return redirect ("showcart")
        else:
            messages.success(request, "This item was not in your cart")
            return redirect ("showcart")
    else:
        messages.success(request, "You do not have an active order")
        return redirect ("showcart")



@login_required
def remove_single_item_from_cart(request):
    user = request.user
    current_user = Users.objects.get(userid=user.id)

    book_id = request.GET.get('data')
    book = Book.objects.get(bookid=book_id)

    cart_qs = ShoppingCart.objects.filter(
        userid = current_user,
        ordered = False
    )

    cart_item_qs = CartItem.objects.filter(
        ordered = False,
        bookid = book,
        cartid = cart_qs[0].cartid
    )

    if cart_qs.exists():
        cart_check = cart_qs[0]
        cart_id = cart_check.cartid
        if cart_item_qs.exists():
            cart_item_check = cart_item_qs[0]
            if cart_item_check.quantity > 1:
                cart_item_check.quantity -= 1
                cart_item_check.save()
                messages.success(request, "Item quantity successfully decreased.")
                return redirect ('showcart')
            else:
                cart_item_check.delete()
            messages.success(request, "This item quantity was updated.")
            return redirect ('showcart')
        else:
            messages.success(request, "This item was not in your cart.")
            return redirect ('showcart')
    else:
        messages.success(request, "You do not have an active order.")
        return redirect ('showcart')


def show_cart(request):
    user = request.user
    current_user = Users.objects.get(userid=user.id)

    if ShoppingCart.objects.filter(userid = current_user, ordered = False):
        cart_qs = ShoppingCart.objects.filter(
            userid = current_user,
            ordered = False
        )

        cart_item_qs = CartItem.objects.filter(
            ordered = False,
            cartid = cart_qs[0].cartid
        )

        cart_list = [x for x in cart_item_qs]
        for x in cart_list:
            book = Book.objects.get(bookid=str(x.bookid))
            title = book.title
            x.title = title

        return render(request, 'cart.html', {'cart':cart_list})

    else:
        messages.success(request, "You do not have any items in your cart.")
        return redirect ('home')
