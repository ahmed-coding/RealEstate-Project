import uuid
from django.utils.text import slugify
from django.contrib.gis.db import models as gis_models
from django.db import models
from PIL import Image as PImage
from xmlrpc.client import TRANSPORT_ERROR
from django.db import transaction
from django.core.exceptions import ObjectDoesNotExist
from django.dispatch import receiver
from django.db.models.signals import post_save
from django.db import models
# from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _
from mptt.models import MPTTModel, TreeForeignKey
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.utils import timezone


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
    user_phone_num = models.CharField(
        _("user_phone_num"), max_length=50, default="", blank=True)
    random_code = models.CharField(_("random_code"), max_length=4)
    time_created = models.DateTimeField(
        _("time_created"), auto_now=False, auto_now_add=True)
    expire_date = models.DateTimeField(
        _("expire_date"), auto_now=False, auto_now_add=True)


class TypeModel(models.Model):
    type = models.CharField(_("type"), max_length=50, default="")

    class Meta:
        db_table = 'Type'


class Attribute_verify(models.Model):
    attribute = models.CharField(_("attribute"), max_length=50)
    data_type = models.CharField(_("data_type"), max_length=50)
    type = models.ForeignKey(TypeModel, verbose_name=_(
        "type"), on_delete=models.CASCADE)


class Attribute_value(models.Model):
    attribute = models.ForeignKey(
        "app.Model", verbose_name=_(""), on_delete=models.CASCADE)

# End Custom User Manager and User Models

# Start Property Models


class Category(models.Model):
    name = models.CharField(_("category"), max_length=50)
    image = models.ImageField(_("cate_image"), upload_to="cate-image")


class Feature(models.Model):
    name = models.CharField(_("feature Name"), max_length=50)


class Feature_category(models.Model):
    feature = models.ForeignKey(Feature, verbose_name=_(
        "feature"), on_delete=models.CASCADE)
    category = models.ForeignKey(Category, verbose_name=_(
        "category"), on_delete=models.CASCADE)


class Property(models.Model):
    user = models.ForeignKey(User, verbose_name=_(
        "User"), on_delete=models.CASCADE)
    category = models.ForeignKey(Category, verbose_name=_(
        "category"), on_delete=models.CASCADE)
    address = models.ForeignKey(
        "Address", verbose_name=_(""), on_delete=models.CASCADE)
    name = models.CharField(_("Name"), max_length=50)
    description = models.TextField(_("description"))
    price = models.DecimalField(_("Price"), max_digits=10, decimal_places=2)
    size = models.IntegerField(_("size"))
    is_active = models.BooleanField(_("is_active"), default=True)
    is_deleted = models.BooleanField(_("is_deleted"), default=False)
    time_created = models.DateTimeField(
        _("time_created"), auto_now=False, auto_now_add=True)
    unique_number = models.SlugField(_("unique_number"))


class Feature_property(models.Model):
    property = models.ForeignKey(Property, verbose_name=_(
        "Property"), on_delete=models.CASCADE)
    feature = models.ForeignKey(Feature, verbose_name=_(
        "Feature"), on_delete=models.CASCADE)
    image = models.ImageField(_("image"), upload_to='feature_property')


class Attribute(models.Model):
    name = models.CharField(_("Name"), max_length=50)
    data_type = models.CharField(_("data_type"), max_length=50)


class ValueModel(models.Model):
    attribute = models.ForeignKey(
        Attribute, verbose_name=_(""), on_delete=models.CASCADE)
    value = models.CharField(_("Value"), max_length=50)

    class Meta:
        db_table = 'Value'


class property_value(models.Model):
    property = models.ForeignKey(
        Property, verbose_name=_(""), on_delete=models.CASCADE)
    value = models.ForeignKey(
        ValueModel, verbose_name=_(""), on_delete=models.CASCADE)


class Category_attribute(models.Model):
    category = models.ForeignKey(Category, verbose_name=_(
        "category"), on_delete=models.CASCADE)
    attribute = models.ForeignKey(
        Attribute, verbose_name=_(""), on_delete=models.CASCADE)


# End Property Models
