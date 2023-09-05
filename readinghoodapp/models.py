from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
import numpy as np
from django.urls import reverse
from viewflow.fields import CompositeKey
from django_cryptography.fields import encrypt


# Create community model
class Community(models.Model):
    name = models.CharField(max_length=100)
    members = models.ManyToManyField(User, related_name="communities")
    description = models.TextField()

    def __str__(self):
        return self.name


# Create post model
class Post(models.Model):
    user = models.ForeignKey(User, related_name="posts", on_delete=models.CASCADE)
    community = models.ForeignKey(Community, null=True, on_delete=models.CASCADE)
    body = models.CharField(max_length=250)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
     return(
        f"{self.user} "
        f"({self.created_at:%Y-%m-%d %H:%M}): "
        f"{self.body}"
    )


# Create user profile model
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    follows = models.ManyToManyField("self",
        related_name="followed_by",
        symmetrical=False,
        blank=True)

    date_modified = models.DateTimeField(User, auto_now=True)
    profile_image = models.ImageField(null=True, blank=True, upload_to="images/")
    def __str__(self):
        return self.user.username


# Create profile when new user signs up
def create_profile(sender, instance, created, **kwargs):
    if created:
        user_profile = Profile(user=instance)
        user_profile.save()
        # User follow themselves
        user_profile.follows.set([instance.profile.id])
        user_profile.save()

post_save.connect(create_profile, sender=User)


# class AuthGroup(models.Model):
#     name = models.CharField(unique=True, max_length=150)

#     class Meta:
#         managed = False
#         db_table = 'auth_group'


# class AuthGroupPermissions(models.Model):
#     id = models.BigAutoField(primary_key=True)
#     group = models.ForeignKey(AuthGroup, models.DO_NOTHING)
#     permission = models.ForeignKey('AuthPermission', models.DO_NOTHING)

#     class Meta:
#         managed = False
#         db_table = 'auth_group_permissions'
#         unique_together = (('group', 'permission'),)


# class AuthPermission(models.Model):
#     name = models.CharField(max_length=255)
#     content_type = models.ForeignKey('DjangoContentType', models.DO_NOTHING)
#     codename = models.CharField(max_length=100)

#     class Meta:
#         managed = False
#         db_table = 'auth_permission'
#         unique_together = (('content_type', 'codename'),)


# class AuthUser(models.Model):
#     password = models.CharField(max_length=128)
#     last_login = models.DateTimeField(blank=True, null=True)
#     is_superuser = models.IntegerField()
#     username = models.CharField(unique=True, max_length=150)
#     first_name = models.CharField(max_length=150)
#     last_name = models.CharField(max_length=150)
#     email = models.CharField(max_length=254)
#     is_staff = models.IntegerField()
#     is_active = models.IntegerField()
#     date_joined = models.DateTimeField()

#     class Meta:
#         managed = False
#         db_table = 'auth_user'


# class AuthUserGroups(models.Model):
#     id = models.BigAutoField(primary_key=True)
#     user = models.ForeignKey(AuthUser, models.DO_NOTHING)
#     group = models.ForeignKey(AuthGroup, models.DO_NOTHING)

#     class Meta:
#         managed = False
#         db_table = 'auth_user_groups'
#         unique_together = (('user', 'group'),)


# class AuthUserUserPermissions(models.Model):
#     id = models.BigAutoField(primary_key=True)
#     user = models.ForeignKey(AuthUser, models.DO_NOTHING)
#     permission = models.ForeignKey(AuthPermission, models.DO_NOTHING)

#     class Meta:
#         managed = False
#         db_table = 'auth_user_user_permissions'
#         unique_together = (('user', 'permission'),)


# class BookCategory(models.Model):
#     categoryid = models.OneToOneField('Categories', models.DO_NOTHING, db_column='CategoryID', primary_key=True)  # Field name made lowercase. The composite primary key (CategoryID, BookID) found, that is not supported. The first column is selected.
#     bookid = models.ForeignKey('Book', models.DO_NOTHING, db_column='BookID')  # Field name made lowercase.

#     class Meta:
#         managed = False
#         db_table = 'book_category'
#         unique_together = (('categoryid', 'bookid'),)


class Book(models.Model):
    bookid = models.AutoField(db_column='BookID', primary_key=True)
    title = models.CharField(db_column='Title', max_length=255)
    author = models.CharField(db_column='Author', max_length=255)
    publicationyear = models.IntegerField(db_column='PublicationYear')
    publisher = models.CharField(db_column='Publisher', max_length=255)
    price = models.DecimalField(db_column='Price', max_digits=10, decimal_places=2, blank=True, null=True)
    bookdescription = models.CharField(db_column='BookDescription', max_length=500, blank=True, null=True)
    image_url = models.CharField(db_column='Image_URL', max_length=255, blank=True, null=True)
    category = models.CharField(db_column='Category', max_length=255)

    def average_rating(self):
        all_ratings = map(lambda x: x.rating, self.ratingsreviews_set.all())
        valid_ratings = [rating for rating in all_ratings if not np.isnan(rating)]
        if not valid_ratings:
            return "Not rated yet"
        average = np.mean(valid_ratings)
        return f"{average:.2f}"

    def __str__(self):
        # bookid
        return str(self.title)

    def get_absolute_url(self):
        return reverse('readinghoodapp:detail', args=[self.bookid,])

    class Meta:
        managed = True
        db_table = 'book'


class CartItem(models.Model):
    itemid = models.AutoField(db_column='ItemID', primary_key=True)  # Field name made lowercase.
    cartid = models.OneToOneField('ShoppingCart', models.DO_NOTHING, db_column='CartID')  # Field name made lowercase. The composite primary key (CartID, ItemID) found, that is not supported. The first column is selected.
    bookid = models.ForeignKey(Book, models.DO_NOTHING, db_column='BookID')  # Field name made lowercase.
    quantity = models.IntegerField(db_column='Quantity')  # Field name made lowercase.
    ordered = models.BooleanField(default=False)

    class Meta:
        managed = True
        db_table = 'cart_item'
        unique_together = (('cartid', 'itemid'),)

    #Function for checkout order_snippet
    #TO IMPLEMENT WHEN DATABASE IS POPULATED WITH PRICE DATA
    def get_total_item_price(self):
        return self.quantity * self.bookid.price


# class Categories(models.Model):
#     categoryid = models.AutoField(db_column='CategoryID', primary_key=True)  # Field name made lowercase.
#     name = models.CharField(db_column='Name', max_length=255)  # Field name made lowercase.
#     catedescription = models.CharField(db_column='CateDescription', max_length=500)  # Field name made lowercase.

#     class Meta:
#         managed = False
#         db_table = 'categories'


# class Communities(models.Model):
#     communityid = models.AutoField(db_column='CommunityID', primary_key=True)
#     description = models.CharField(db_column='Description', max_length=500)

#     class Meta:
#         managed = False
#         db_table = 'communities'


class Dates(models.Model):
    dateid = models.AutoField(db_column='DateID', primary_key=True)  # Field name made lowercase.
    date = models.DateField(db_column='Date')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'dates'


# class DjangoAdminLog(models.Model):
#     action_time = models.DateTimeField()
#     object_id = models.TextField(blank=True, null=True)
#     object_repr = models.CharField(max_length=200)
#     action_flag = models.PositiveSmallIntegerField()
#     change_message = models.TextField()
#     content_type = models.ForeignKey('DjangoContentType', models.DO_NOTHING, blank=True, null=True)
#     user = models.ForeignKey(AuthUser, models.DO_NOTHING)

#     class Meta:
#         managed = False
#         db_table = 'django_admin_log'


# class DjangoContentType(models.Model):
#     app_label = models.CharField(max_length=100)
#     model = models.CharField(max_length=100)

#     class Meta:
#         managed = False
#         db_table = 'django_content_type'
#         unique_together = (('app_label', 'model'),)


# class DjangoMigrations(models.Model):
#     id = models.BigAutoField(primary_key=True)
#     app = models.CharField(max_length=255)
#     name = models.CharField(max_length=255)
#     applied = models.DateTimeField()

#     class Meta:
#         managed = False
#         db_table = 'django_migrations'


# class DjangoSession(models.Model):
#     session_key = models.CharField(primary_key=True, max_length=40)
#     session_data = models.TextField()
#     expire_date = models.DateTimeField()

#     class Meta:
#         managed = False
#         db_table = 'django_session'


# class Forum(models.Model):
#     communityid = models.OneToOneField(Communities, models.DO_NOTHING, db_column='communityID', primary_key=True)  # Field name made lowercase. The composite primary key (communityID, ForumID) found, that is not supported. The first column is selected.
#     forumid = models.IntegerField(db_column='ForumID')  # Field name made lowercase.

#     class Meta:
#         managed = False
#         db_table = 'forum'
#         unique_together = (('communityid', 'forumid'),)


# class Friendship(models.Model):
#     userid = models.OneToOneField('Users', models.DO_NOTHING, db_column='UserID', primary_key=True)  # Field name made lowercase. The composite primary key (UserID, FriendID) found, that is not supported. The first column is selected.
#     friendid = models.ForeignKey('Users', models.DO_NOTHING, db_column='FriendID', related_name='friendship_friendid_set')  # Field name made lowercase.

#     class Meta:
#         managed = False
#         db_table = 'friendship'
#         unique_together = (('userid', 'friendid'),)


class OrderItem(models.Model):
    orderid = models.OneToOneField('Orders', models.DO_NOTHING, db_column='OrderID', primary_key=True)  # Field name made lowercase. The composite primary key (OrderID, ItemID) found, that is not supported. The first column is selected.
    itemid = models.IntegerField(db_column='ItemID')  # Field name made lowercase.
    bookid = models.ForeignKey(Book, models.DO_NOTHING, db_column='BookID')  # Field name made lowercase.
    quantity = models.IntegerField(db_column='Quantity')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'order_item'
        unique_together = (('orderid', 'itemid'),)


class Orders(models.Model):
    orderid = models.AutoField(db_column='OrderID', primary_key=True)  # Field name made lowercase.
    userid = models.ForeignKey('Users', models.DO_NOTHING, db_column='UserID')  # Field name made lowercase.
    orderdate = models.ForeignKey(Dates, models.DO_NOTHING, db_column='OrderDate')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'orders'


class Publishers(models.Model):
    publisherid = models.AutoField(db_column='PublisherID', primary_key=True)  # Field name made lowercase.
    name = models.CharField(db_column='Name', max_length=255)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'publishers'

    def __str__(self):
        return self.name


class ShoppingCart(models.Model):
    cartid = models.AutoField(db_column='CartID', primary_key=True)  # Field name made lowercase.
    userid = models.ForeignKey('Users', models.DO_NOTHING, db_column='UserID')  # Field name made lowercase.
    ordered = models.BooleanField(default=False)

    class Meta:
        managed = True
        db_table = 'shopping_cart'

    #Function for checkout order_snippet
    #TO IMPLEMENT WHEN DATABASE IS POPULATED WITH PRICE DATA
    # def get_total(self):
    #     total = 0
    #     for order_item in self.cartid:
    #         total += order_item.get_total_item_price()
    #     return total

# class UserCommunity(models.Model):
#     communityid = models.OneToOneField(Communities, models.DO_NOTHING, db_column='CommunityID', primary_key=True)  # Field name made lowercase. The composite primary key (CommunityID, UserID) found, that is not supported. The first column is selected.
#     userid = models.ForeignKey('Users', models.DO_NOTHING, db_column='UserID')  # Field name made lowercase.

#     class Meta:
#         managed = False
#         db_table = 'user_community'
#         unique_together = (('communityid', 'userid'),)

CHOICES = [
    ('Y', 'Yes'),
    ('N', 'No'),
    ]


class Users(models.Model):
    userid = models.AutoField(db_column='UserID', primary_key=True)  # Field name made lowercase.
    username = models.CharField(db_column='Username', max_length=255, blank=True, null=True)  # Field name made lowercase.
    password = models.CharField(db_column='Password', max_length=20, blank=True, null=True)  # Field name made lowercase.
    #firstname = models.CharField(max_length=50, blank=True, null=True)
    #lastname = models.CharField(max_length=50, blank=True, null=True)
    emailaddress = models.CharField(db_column='EmailAddress', max_length=255, blank=True, null=True)  # Field name made lowercase.
    phone = models.IntegerField(db_column='Phone', blank=True, null=True)  # Field name made lowercase.
    location = models.CharField(db_column='Location', max_length=255, blank=True, null=True)  # Field name made lowercase.
    age = models.IntegerField(db_column='Age', blank=True, null=True)  # Field name made lowercase.
    address = models.CharField(db_column='Address', max_length=255, blank=True, null=True)
    approvedauthor = models.CharField(db_column='ApprovedAuthor', max_length=3, choices=CHOICES, blank=True, null=True)  # Field name made lowercase.
    activated = models.CharField(db_column='Activated', max_length=3, choices=CHOICES, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'users'

    def __str__(self):
        return str(self.userid)


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

ADDRESS_CHOICES = [
    ('B', 'Billing'),
    ('S', 'Shipping'),
]


class Address(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    address1 = models.CharField(max_length=100)
    address2 = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100, choices=STATE_CHOICES)
    postcode = models.CharField(max_length=10)
    address_type = models.CharField(max_length=1, choices=ADDRESS_CHOICES)
    default = models.BooleanField(default=False)

    def __str__(self):
        return str(self.user.username)

    class Meta:
        verbose_name_plural = 'Addresses'


class Payment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    card_name = models.CharField(max_length=100)
    card_number = models.CharField(max_length=100)
    expiry_date = models.CharField(max_length=100)
    security_code = models.CharField(max_length=100)

    def __str__(self):
        return str(self.user.username)

RATING_CHOICES = (
        (0, '0'),
        (1, '1'),
        (2, '2'),
        (3, '3'),
        (4, '4'),
        (5, '5'),
        (6, '6'),
        (7, '7'),
        (8, '8'),
        (9, '9'),
        (10, '10'),
    )


class RatingsReviews(models.Model):
    id = CompositeKey(columns=['userid','bookid'])
    userid = models.OneToOneField(Users, on_delete=models.CASCADE, db_column='UserID')  # Field name made lowercase. The composite primary key (UserID, BookID) found, that is not supported. The first column is selected.
    bookid = models.ForeignKey(Book, on_delete=models.CASCADE, db_column='BookID')  # Field name made lowercase.
    ratedate = models.DateTimeField(auto_now_add=True)  # Field name made lowercase.
    rating = models.PositiveSmallIntegerField(db_column='Rating', choices=RATING_CHOICES)  # Field name made lowercase.
    review = models.TextField(db_column='Review', max_length=3000, blank=True, null=True)  # Field name made lowercase.
    #likes = models.PositiveIntegerField(default=0)
    #unlikes = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"Rating for BookID: {self.bookid_id}, UserID: {self.userid_id}"

    class Meta:
        managed = False
        db_table = 'ratings_reviews'
        unique_together = (('userid', 'bookid'),)
