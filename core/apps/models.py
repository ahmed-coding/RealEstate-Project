from django.contrib.contenttypes.fields import GenericRelation
from django.contrib.contenttypes.fields import GenericForeignKey
from mptt.models import MPTTModel, TreeForeignKey
from django.utils import timezone
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.utils.translation import gettext_lazy as _
from django.contrib.contenttypes.models import ContentType
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction
from xmlrpc.client import TRANSPORT_ERROR
from PIL import Image as PImage
from django.db import models
from django.contrib.gis.db import models as gis_models
from django.utils.text import slugify
import uuid
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
import string
import random
# from django.contrib.auth.models import User


def generit_random_code(code_lenth):
    list_code = string.digits
    lenth = len(list_code)
    count = 0
    code = ''
    while count < code_lenth:
        index = random.randint(0, lenth-1)
        code += list_code[index]
        count += 1
    # print(len(str(int(code))))
    if len(str(int(code))) != code_lenth:
        generit_random_code(code_lenth)
    return int(code)

# Custom User Manager and User Models


class MyUserManager(BaseUserManager):
    """
    Custom User Manager
    """

    def _create_user(self,  email, username,  password, **extra_fields):
        """
        Create and save a user with the given username, email, and password.
        """
        if not email:
            raise ValueError("The given email must be set")
        email = self.normalize_email(email)
        # Lookup the real model class from the global app registry so this
        # manager method can be used in migrations. This is fine because
        # managers are by definition working on the real model.
        # GlobalUserModel = apps.get_model(
        #     self.model._meta.app_label, self.model._meta.object_name
        # )
        # username = GlobalUserModel.normalize_username(username)
        user = self.model(email=email,  username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, username=None, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(email, username, password, **extra_fields)

    def create_superuser(self, email, username=None,  password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self._create_user(email, username, password, **extra_fields)


# ==========


class User(AbstractBaseUser, PermissionsMixin):
    """
    Custome User to create and login user with email and auth_provider like google, facebook or Email.\n
    Auth_provider is default by email.\n

    To Use Choices in auth_provider use  User.EMAIL or User.GOOGLE etc...\n

    AUTHENTICATION:\n
        We use JWT auth for this project
    """
    # Choices
    EMAIL = 'email'
    GOOGLE = 'google'
    FACEBOOB = 'facebook'
    username = models.CharField(
        _("username"),
        max_length=150,
        # unique=True,
        null=True,
        help_text=_(
            "Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only."
        ),
        blank=True,
        error_messages={
            "unique": _("A user with that username already exists."),
        }
    )
    # auth_provider = models.CharField(
    #     max_length=20, blank=True, null=False, default=EMAIL)
    name = models.CharField(
        _('Full name'), max_length=60, default='', blank=True)
    # first_name = models.CharField(
    #     _("first name"), max_length=55, blank=True, default='')
    # last_name = models.CharField(
    #     _("last name"), max_length=55, blank=True, default='')
    # age = models.IntegerField(_('age'), blank=True, null=True)
    # =============
    email = models.EmailField(_("email address"), unique=True)
    phone_number = models.CharField(
        _("phone number"),  max_length=50, default='', null=True)
    register_data = models.CharField(max_length=20, default='')
    is_staff = models.BooleanField(
        _("staff status"),
        default=False,
        help_text=_(
            "Designates whether the user can log into this admin site."),
    )
    is_active = models.BooleanField(
        _("active"),
        default=True,
        help_text=_(
            "Designates whether this user should be treated as active. "
            "Unselect this instead of deleting accounts."
        ),
    )
    is_deleted = models.BooleanField(_('Deleted'), default=False,)
    date_joined = models.DateTimeField(
        _("date joined"), default=timezone.now, )
    image = models.ImageField(
        upload_to='user_image',
        # default='user_image/MicrosoftTeams-image.png',
        blank=True,
        null=True
    )
    unique_no = models.SlugField(_("unique_no"), unique=True, blank=True,)
    is_seller = models.BooleanField(_("Is Seller?"), default=False)

    ########## ManyToMAny Fileds ###########
    # product_view = models.ManyToManyField("Product_item", through='View')
    # wishlist = models.ManyToManyField(
    #     'Product_item', through='Wishlist')
    # favorite = models.ManyToManyField('Product_item', through='Favorite')
    # cart = models.ManyToManyField('Product_item', through='Cart')
    # add_rate = models.ManyToManyField('Product_item', through='Rate')

    objects = MyUserManager()
    # EMAIL_FIELD = "email"
    USERNAME_FIELD = "email"
    # REQUIRED_FIELDS = ["email"]

    def get_full_name(self):
        """
        Return the name, with a space in between.
        """
        full_name = "%s " % (self.name)
        return full_name.strip()

    def get_short_name(self):
        """Return the short name for the user."""
        return self.name

    def save(self, *args, **kwargs):
        if not self.id:
            self.unique_no = f"{generit_random_code(8)}"
        return super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        """
        Overrid delete method to delete Image first then delete user
        not will be show in admin panle and aothre thinks like auth

        """

        try:
            self.image.delete()
            self.is_deleted = True
            self.is_active = False
            self.is_superuser = False
            self.save()
            return True
        except:
            self.is_deleted = True
            self.save()
            return True

        # return super().delete(*args, **kwargs)
    def get(self,  **kwargs):
        user = self.objects.get(**kwargs, is_delete=False) or None
        if user:
            return user
        raise self.DoesNotExist()

    def __str__(self) -> str:
        return f" {self.pk} |{self.email}:{self.name}"

    # Start Method for Class

    def add_cart(self, item_id: int, count: int):
        try:
            return self.cart.create(product_id=item_id, qty=count)
        except:
            ins = self.cart.get(product_id=item_id)
            ins.qty = count
            return ins.save()

    def add_favorite(self, item_id: int):
        try:
            data = self.favorites.get_or_create(product_id=item_id)
            return data[0]
        except:
            return False

    def remove_favorite(self, item_id: int):
        pass
        # End Method for Class

    class Meta:
        db_table = 'User'


class VerificationCode(models.Model):
    """
    Verification_Code model .
    -------------------------
    It use to verify the account by the code
    """
    user_phone_num = models.CharField(
        _("user_phone_num"), max_length=50, default="", blank=True)
    random_code = models.CharField(_("random_code"), max_length=4)
    time_created = models.DateTimeField(
        _("time_created"), auto_now=False, auto_now_add=True)
    expire_date = models.DateTimeField(
        _("expire_date"), auto_now=False, auto_now_add=True)

    class Meta:
        db_table = 'VerificationCode'


class TypeModel(models.Model):
    """
    Type model .
    --------------------------

    """
    type = models.CharField(_("type"), max_length=50, default="")

    class Meta:
        db_table = 'Type'


class Attribute_verify(models.Model):
    """
    Attribute_verify model .
    ---------------------------

    """
    attribute = models.CharField(_("attribute"), max_length=50)
    data_type = models.CharField(_("data_type"), max_length=50)
    type = models.ForeignKey(TypeModel, verbose_name=_(
        "type"), on_delete=models.CASCADE)

    class Meta:
        db_table = 'Attribute_verify'


class Attribute_value(models.Model):
    """
    Attribute_value
    ---------------------------

    """
    attribute = models.ForeignKey(
        'Attribute', verbose_name=_("attribute_value"), on_delete=models.CASCADE)

    class Meta:
        db_table = 'Attribute_value'

# End Custom User Manager and User Models
# Start Address


class Country(models.Model):
    """
    Country model . 
    ---------------------------

    """
    name = models.CharField(_("Name"), max_length=50)

    class Meta:
        db_table = 'Country'


class City(models.Model):
    """
    City model .
    ---------------------------

    """
    name = models.CharField(_("Name"), max_length=50)
    country = models.ForeignKey(
        Country, verbose_name=_("Country"), on_delete=models.CASCADE, related_name='city')

    class Meta:
        db_table = 'City'


class State(models.Model):
    """
    State model .
    ---------------------------

    """
    name = models.CharField(_("Name"), max_length=50)
    city = models.ForeignKey(
        City, verbose_name=_("City"), on_delete=models.CASCADE, related_name='state')

    class Meta:
        db_table = 'State'


class Address(models.Model):
    """
    Address model .
    ---------------------------

    """
    state = models.ForeignKey(
        State, verbose_name=_("State "), on_delete=models.CASCADE, related_name='address')
    longitude = models.CharField(_("longitude"), max_length=50)
    latitude = models.CharField(_("latitude"), max_length=50)

    class Meta:
        db_table = 'Address'

# End Address
# Start Property Models


def generate_upload_to_path(instance, filename):
    if instance.content_type:
        return f'{instance.content_type.name}-images/{filename}'
    return f'images/unknown/{filename}'


class Image(models.Model):

    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey()
    image = models.ImageField(_("Image"), upload_to=generate_upload_to_path)
    # def save(self, *args, **kwargs):

    #     if self.content_type:
    #         self.image.upload_to = f'{self.content_type.name}/'
    #     return super().save(*args, **kwargs)


class Category(MPTTModel):
    """
    model for Main category , category and Sub-category in one model
    ----------------
    use parent and level attributes to access who category is returned
    """
    parent = TreeForeignKey(
        'self', on_delete=models.CASCADE, blank=True, related_name='children', null=True)
    name = models.CharField(max_length=50)
    image = GenericRelation(Image, related_query_name='category')

    class MPTTMeta:
        # level_attr = 'parint'
        order_insertion_by = ['name']

    def __str__(self):
        return f"name: {self.name} parent {self.parent} id {self.id} "

    class Meta:
        db_table = 'Category'


# class Image_Category(models.Model):
#     """
#     Image_Category model .
#     ---------------------------

#     """
#     category = models.ForeignKey(Category, verbose_name=_(
#         "Category"), on_delete=models.CASCADE, related_name='image')
#     image = models.ImageField(_("cate_image"), upload_to="cate-image")

#     class Meta:
#         db_table = 'Image_Category'


class Feature(models.Model):
    """
    Feature model .
    ---------------------------

    """
    name = models.CharField(_("feature Name"), max_length=50)

    class Meta:
        db_table = 'Feature'


class Feature_category(models.Model):
    """
    Feature_Category model .
    ---------------------------

    """
    feature = models.ForeignKey(Feature, verbose_name=_(
        "feature"), on_delete=models.CASCADE, related_name='feature_category')
    category = models.ForeignKey(Category, verbose_name=_(
        "category"), on_delete=models.CASCADE, related_name='feature_category')

    class Meta:
        db_table = 'Feature_category'


class Property(models.Model):
    """
    Property model .
    ---------------------------

    """
    user = models.ForeignKey(User, verbose_name=_(
        "User"), on_delete=models.CASCADE, related_name='property')
    category = models.ForeignKey(Category, verbose_name=_(
        "category"), on_delete=models.CASCADE, related_name='property')
    address = models.ForeignKey(
        Address, verbose_name=_("Address"), on_delete=models.CASCADE, related_name='property')
    name = models.CharField(_("Name"), max_length=50)
    description = models.TextField(_("description"))
    price = models.DecimalField(_("Price"), max_digits=10, decimal_places=2)
    size = models.IntegerField(_("size"))
    is_active = models.BooleanField(_("is_active"), default=True)
    is_deleted = models.BooleanField(_("is_deleted"), default=False)
    time_created = models.DateTimeField(
        _("time_created"), auto_now=False, auto_now_add=True)
    unique_number = models.SlugField(_("unique_number"), editable=False)
    image = GenericRelation(Image, related_query_name='property')

    def save(self, *args, **kwargs):
        if not self.id:
            self.unique_no = f"{generit_random_code(10)}"
        return super().save(*args, **kwargs)

    class Meta:
        db_table = 'Property'


# class Image_Property(models.Model):
#     """
#     Image_Property model .
#     ---------------------------

#     """
#     property = models.ForeignKey(Property, verbose_name=_(
#         "Property"), on_delete=models.CASCADE, related_name='image')
#     image = models.ImageField(_("image"), upload_to="ticket",)

#     class Meta:
#         db_table = 'Image_Property'


class Feature_property(models.Model):
    """
    Feature_property model .
    ---------------------------

    """
    property = models.ForeignKey(Property, verbose_name=_(
        "Property"), on_delete=models.CASCADE, related_name='feature_property')
    feature = models.ForeignKey(Feature, verbose_name=_(
        "Feature"), on_delete=models.CASCADE, related_name='feature_property')
    image = GenericRelation(Image, related_query_name='featuer_property')

    class Meta:
        db_table = 'Feature_property'


# class Image_Feature_property(models.Model):
#     """
#     Image_Feature_property model .
#     ---------------------------

#     """
#     feature_property = models.ForeignKey(Feature_property, verbose_name=_(
#         "feature_property"), on_delete=models.CASCADE, related_name='image')
#     image = models.ImageField(_("image"), upload_to='feature_property')

#     class Meta:
#         db_table = 'Image_Feature_property'


class Attribute(models.Model):
    """
    Attribute model .
    ---------------------------

    """
    name = models.CharField(_("Name"), max_length=50)
    data_type = models.CharField(_("data_type"), max_length=50)

    def __str__(self) -> str:
        return self.name

    class Meta:
        db_table = 'Attribute'


class ValueModel(models.Model):
    """
    Value model .
    ---------------------------

    """
    attribute = models.ForeignKey(
        Attribute, verbose_name=_("attribute"), on_delete=models.CASCADE, related_name='value_attribute')
    value = models.CharField(_("Value"), max_length=50)

    def __str__(self):
        return f"{self.attribute.name} - {self.value}"

    class Meta:
        db_table = 'Value'


class property_value(models.Model):
    """
    property_value model .
    ---------------------------

    """
    property = models.ForeignKey(
        Property, verbose_name=_("property"), on_delete=models.CASCADE, related_name='property_value')
    value = models.ForeignKey(
        ValueModel, verbose_name=_("value"), on_delete=models.CASCADE, related_name="property_value")

    class Meta:
        db_table = 'property_value'


class Category_attribute(models.Model):
    """
    Category_attribute model .
    ---------------------------

    """
    category = models.ForeignKey(Category, verbose_name=_(
        "category"), on_delete=models.CASCADE, related_name='category_attribute')
    attribute = models.ForeignKey(
        Attribute, verbose_name=_("attribute"), on_delete=models.CASCADE, related_name='category_attribute')

    class Meta:
        db_table = 'Category_attribute'

# End Property Models

# Start Interaction Models


class Rate(models.Model):
    """
    Rate model .
    ---------------------------

    """
    prop = models.ForeignKey(
        Property, verbose_name=_("prperty"), on_delete=models.CASCADE, related_name='rate')
    user = models.ForeignKey(
        "apps.User", verbose_name=_("user"), on_delete=models.CASCADE, related_name='rate')
    rate = models.FloatField(_("Rating Number"), default=0.0)
    time_created = models.DateTimeField(
        _("time_created"), auto_now=False, auto_now_add=True)

    class Meta:
        db_table = 'Rate'


class Favorite(models.Model):
    """
    Favorite model .
    ---------------------------

    """
    prop = models.ForeignKey(
        Property, verbose_name=_("prop"), on_delete=models.CASCADE, related_name='favorites')
    user = models.ForeignKey(
        "apps.User", verbose_name=_("user"), on_delete=models.CASCADE, related_name='favorites')
    time_created = models.DateTimeField(
        _("time_created"), auto_now=False, auto_now_add=True)

    class Meta:
        db_table = 'Favorite'


class Report(models.Model):
    """
    Report model .
    ---------------------------

    """
    prop = models.ForeignKey(
        Property, verbose_name=_("property"), on_delete=models.CASCADE, related_name='report')
    user = models.ForeignKey(
        "apps.User", verbose_name=_("user"), on_delete=models.CASCADE, related_name='report')
    time_created = models.DateTimeField(
        _("time_created"), auto_now=False, auto_now_add=True)
    note = models.TextField(_("Note"))

    class Meta:
        db_table = 'Report'


class Review(models.Model):
    """
    Review model .
    ---------------------------

    """
    prop = models.ForeignKey(
        Property, verbose_name=_("Property"), on_delete=models.CASCADE, related_name='review')
    user = models.ForeignKey(
        "apps.User", verbose_name=_("user"), on_delete=models.CASCADE, related_name='review')
    time_created = models.DateTimeField(
        _("time_created"), auto_now=False, auto_now_add=True)
    review = models.TextField(_("Note"))

    class Meta:
        db_table = 'Review'

# End Interaction Models
# Start TICKET Models


class Ticket_type(models.Model):
    """
    Ticket_type model .
    ---------------------------

    """
    type = models.CharField(_("type"), max_length=50)

    class Meta:
        db_table = 'Ticket_type'


class Ticket_status(models.Model):
    """
    Ticket_status model .
    ---------------------------

    """
    status = models.CharField(_("Status"), max_length=50)

    class Meta:
        db_table = 'Ticket_status'


class Ticket(models.Model):
    """
    Ticket model .
    ---------------------------

    """

    type = models.ForeignKey(Ticket_type, verbose_name=_(
        "type"), on_delete=models.DO_NOTHING, related_name='ticket')
    status = models.ForeignKey(
        Ticket_status, verbose_name=_("Ticket_status"), on_delete=models.CASCADE, related_name='ticket', null=True, blank=True)
    solver = models.ForeignKey(User, verbose_name=_(
        "solver"), on_delete=models.CASCADE, related_name="solver", null=True, blank=True)
    sender = models.ForeignKey(User, verbose_name=_(
        "sender"), on_delete=models.CASCADE, related_name="sender")
    phone_number = models.CharField(_("phone_number"), max_length=50)
    created_time = models.DateTimeField(
        _("created_time"), auto_now=False, auto_now_add=True)
    solved_time = models.DateTimeField(
        _("solved_time"), auto_now=False, auto_now_add=False)
    email = models.EmailField(_("email"), max_length=254)
    problem_text = models.TextField(_("problem_text"))
    image = GenericRelation(Image, related_query_name='ticket')

    class Meta:
        db_table = 'Ticket'


# class Image_Ticket(models.Model):
#     """
#     Image_Ticket model .
#     ---------------------------

#     """
#     ticket = models.ForeignKey(Ticket, verbose_name=_(
#         "Ticket"), on_delete=models.CASCADE)
#     image = models.ImageField(_("image"), upload_to="ticket",)

#     class Meta:
#         db_table = 'Image_Ticket'


class Solve_message(models.Model):
    """
    Solve_message model .
    ---------------------------

    """
    ticket = models.ForeignKey(
        Ticket, verbose_name=_("ticket"), on_delete=models.CASCADE, related_name='solve_message')
    message = models.TextField(_("message"))

    class Meta:
        db_table = 'Solve_message'

# End TICKET Models
# Start Notifications Models


class Notification(models.Model):
    """
    Notification model .
    ---------------------------

    """
    content = models.TextField(_("content"))
    time_created = models.DateTimeField(
        _("time_created"), auto_now=False, auto_now_add=True)

    def save(self, *args, **kwargs):
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            'notifications',
            {
                'type': 'send_notifications',
                'content': self.content
            },
        )
        return super().save(*args, **kwargs)

    class Meta:
        db_table = 'Notification'


class User_notification(models.Model):
    """
    User_notification model .
    ---------------------------

    """
    user = models.ForeignKey(User, verbose_name=_(
        "user"), on_delete=models.CASCADE, related_name='notifications')
    notification = models.ForeignKey(
        Notification, verbose_name=_("notification"), on_delete=models.CASCADE, related_name='user_notification')

    class Meta:
        db_table = 'User_notification'

# End Notifications Models
