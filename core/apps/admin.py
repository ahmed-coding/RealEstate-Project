from statistics import mode
from django.contrib import admin
from . import models
from django import forms
from .models import Category
from .models import User
# Register your models here.
from django.utils.translation import gettext_lazy as _
from mptt.admin import DraggableMPTTAdmin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import (
    AdminPasswordChangeForm,
    UserChangeForm,
    UserCreationForm,
    ReadOnlyPasswordHashField,
    UsernameField,
)  # Register your models here.


class CustomUserChangeForm(forms.ModelForm):
    """
    Custom UserChangForm For AdminUser registertions
    """
    password = ReadOnlyPasswordHashField(
        label=_("Password"),
        help_text=_(
            "Raw passwords are not stored, so there is no way to see this "
            "user’s password, but you can change the password using "
            '<a href="{}">this form</a>.'
        ),
    )

    class Meta:
        model = User
        fields = ("name", "phone_number", "email", "is_active", "is_staff",
                  "is_superuser",  "groups", "username",)
        # field_classes = {"email": forms.EmailField}


class CustomUserCreationForm(UserCreationForm):
    """
        Custom UserChangForm For AdminUser registertions
    """
    class Meta:
        model = User
        fields = ("name", "phone_number", "email", "is_active", "is_staff",
                  "is_superuser",  "groups", "username",)
        # field_classes = {'email': forms.EmailField}


class CustomAdminUser(UserAdmin):
    """
        Custom CustomUSerAdmin For User registertions to add grops and Custom Disgan

    """
    fieldsets = (
        (None, {"fields": ("username", "password")}),
        (_("Personal info"), {
         "fields": ("name", "phone_number", "email", 'image', "unique_no")}),
        (
            _("Permissions"),
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                    "is_deleted",
                    "is_seller"
                ),
            },
        ),
        (_("Important dates"), {"fields": ("last_login", "date_joined")}),
    )
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("username", "email", "password1", "password2", 'name', 'phone_number'),
            },
        ),
    )
    form = CustomUserChangeForm
    # add_form = CustomUserCreationForm
    change_password_form = AdminPasswordChangeForm
    list_display = ("email", "name",
                    "phone_number", "is_staff", 'is_deleted', 'is_active')
    list_filter = ("is_staff", "is_superuser",
                   "is_active", "groups",  'is_deleted', 'is_active')
    search_fields = ("username",
                     "phone_number", "name", "email")
    ordering = ("id",)
    filter_horizontal = (
        "groups",
        "user_permissions",
    )

    def get_queryset(self, request):

        qs = self.model._default_manager.get_queryset()
        # TODO: this should be handled by some parameter to the ChangeList.
        ordering = self.get_ordering(request)
        if ordering:
            qs = qs.all()
        return qs


admin.site.register(User, CustomAdminUser)


class CategoryAdmin(DraggableMPTTAdmin):
    mptt_indent_field = "name"
    list_display = ('tree_actions', 'indented_title',
                    'related_property_counts', 'related_property_cumulative_count')
    list_display_links = ('indented_title',)

    def get_queryset(self, request):
        qs = super().get_queryset(request)

        # Add cumulative product count
        qs = Category.objects.add_related_count(
            qs,
            models.Property,
            'category',
            'property_cumulative_count',
            cumulative=True)

        # Add non cumulative product count
        qs = Category.objects.add_related_count(qs,
                                                models.Property,
                                                'category',
                                                'property_counts',
                                                cumulative=False)
        return qs

    def related_property_counts(self, instance):
        return instance.property_counts
    related_property_counts.short_description = 'Related property (for this specific category)'

    def related_property_cumulative_count(self, instance):
        return instance.property_cumulative_count
    related_property_cumulative_count.short_description = 'Related property (in tree)'


admin.site.register(models.Category, CategoryAdmin)


class SendNotification(forms.Form):
    content = forms.CharField(label="notification content", max_length=255)


@admin.register(models.Notification)
class NotificationAdmin(admin.ModelAdmin):
    add_form_templat = "admin/custom_add_form.html"
    list_display = ('verb',)


admin.site.register(model_or_iterable=[
    models.City,
    models.Category_attribute,
    models.property_value,
    models.Property,
    models.Feature_property,
    models.Country,
    models.Address,
    models.Feature_category,
    models.State,
    models.Feature,
    models.ValueModel,
    models.Attribute_value,
    models.Attribute,
    models.Image,
    models.Review,
    models.Rate,
    models.Favorite,
    models.Report,
    models.Ticket,
    models.Ticket_status,
    models.Ticket_type,
    models.Solve_message,
    models.FriendList,
    models.FriendRequest,
    models.RoomChatMessage,
    models.PrivateChatRoom,
    models.UnreadChatRoomMessages,
])
