from statistics import mode
from django.contrib import admin
from . import models
from django import forms
from .models import Banner, Category, PrivateChatRoom, UnreadChatRoomMessages
from .models import User
from django.contrib.contenttypes.admin import GenericTabularInline
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
from .models import (
    VerificationCode, TypeModel, Attribute_verify, Attribute_value, Country, City, State, Address, Image,
    Category, Feature, Feature_category, Property, Feature_property, Attribute, ValueModel, property_value, Category_attribute, Rate, Favorite, Report,
    Review, Ticket_type, Ticket_status, Ticket, Solve_message, FriendList,
)
from import_export.admin import ImportExportModelAdmin
from import_export import resources, fields, widgets
from import_export.fields import Field
from django.core.files import File


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


class ImageInline(GenericTabularInline):
    model = Image


class Category_attributeInline(admin.TabularInline):
    model = Category_attribute


class Feature_propertyInline(admin.TabularInline):
    model = Feature_property


class CategoryAdmin(DraggableMPTTAdmin):

    mptt_indent_field = "name"
    list_display = ('tree_actions', 'indented_title',
                    'related_property_counts', 'related_property_cumulative_count')
    list_display_links = ('indented_title',)
    inlines = [
        ImageInline,
        Category_attributeInline,



    ]

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


class VerificationCodeAdmin(admin.ModelAdmin):
    list_display = ('user_phone_num', 'random_code',
                    'time_created', 'expire_date')

# Admin class for TypeModel


class TypeModelAdmin(admin.ModelAdmin):
    list_display = ('type',)

# Admin class for Attribute_verify


class AttributeVerifyAdmin(admin.ModelAdmin):
    list_display = ('attribute', 'data_type', 'type')

# Admin class for Attribute_value


class AttributeValueAdmin(admin.ModelAdmin):
    list_display = ('attribute',)


class CityAdmin(admin.ModelAdmin):
    list_display = ('name', 'country')

# Admin class for State


class StateAdmin(admin.ModelAdmin):
    list_display = ('name', 'city')


class AddressForm(forms.ModelForm):
    country = forms.ModelChoiceField(
        queryset=Country.objects.all(), label='Country')
    city = forms.ModelChoiceField(queryset=City.objects.all(), label='City')
    state = forms.ModelChoiceField(queryset=State.objects.all(), label='State')

    class Meta:
        model = Address
        fields = ['country', 'city', 'state', 'longitude', 'latitude']

# Admin class for Address


class AddressAdmin(admin.ModelAdmin):
    # list_display = ('state', 'longitude', 'latitude')
    form = AddressForm
    # list_display_links = ['id']
    fieldsets = (
        ('Location', {
            'fields': ('country', 'city', 'state')
        }),
        ('Coordinates', {
            'fields': ('longitude', 'latitude', 'line1', 'line2')
        }),
    )

    list_display = ['id', 'get_country', 'get_city',
                    'get_state', 'longitude', 'latitude']
    list_display_links = ['id']
    search_fields = ['country__name', 'city__name', 'state__name']

    def get_fields(self, request, obj=None):
        if obj:
            return ['country', 'city', 'state', 'longitude', 'latitude', 'line1', 'line2']
        else:
            return super().get_fields(request, obj)

    def add_view(self, request, form_url='', extra_context=None):
        self.fields = ['country', 'city', 'state',
                       'longitude', 'latitude', 'line1', 'line2']
        return super().add_view(request, form_url, extra_context)

    def change_view(self, request, object_id, form_url='', extra_context=None):
        self.fields = ['country', 'city', 'state',
                       'longitude', 'latitude', 'line1', 'line2']
        return super().change_view(request, object_id, form_url, extra_context)

    def get_country(self, obj):
        return obj.state.city.country.name if obj.state and obj.state.city else ''
    get_country.admin_order_field = 'state__city__country__name'
    get_country.short_description = 'Country'

    def get_city(self, obj):
        return obj.state.city.name if obj.state else ''
    get_city.admin_order_field = 'state__city__name'
    get_city.short_description = 'City'

    def get_state(self, obj):
        return obj.state.name if obj.state else ''
    get_state.admin_order_field = 'state__name'
    get_state.short_description = 'State'


# Admin class for Image
class ImageAdmin(admin.ModelAdmin):
    list_display = ('content_type', 'object_id', 'image')

# Admin class for Feature
class FeatureAttributeInline(admin.TabularInline):
    model = Feature_category
    extra = 1
class FeatureAdminForm(forms.ModelForm):
    class Meta:
        model = Feature
        fields = '__all__'
    
    # def __init__(self, *args, **kwargs):
    #     super().__init__(*args, **kwargs)
    #     # Filter the category field to display only sub-categories
    #     self.fields['category'].queryset = Category.objects.filter(level=2)

class FeatureAdmin(admin.ModelAdmin):
    form = FeatureAdminForm
    inlines = [FeatureAttributeInline]
    

# Admin class for Feature_category


class FeatureCategoryAdmin(admin.ModelAdmin):
    list_display = ('feature', 'category')


# Admin class for Feature_property
class FeaturePropertyAdmin(admin.ModelAdmin):
    list_display = ('property', 'feature')
    inlines = [
        ImageInline,
    ]

# Admin class for Attribute
class CategoryAttributeInline(admin.TabularInline):
    model = Attribute.category.through
    extra = 1


class AttributeAdminForm(forms.ModelForm):
    
    class Meta:
        model = Attribute
        fields = '__all__'

class AttributeAdmin(admin.ModelAdmin):
    # list_display = ('name', 'data_type',)
    # fieldsets = (
    #     (None, {'fields': ("")}),

    #     ('categores', {'fields': ('categores',)}),
    # )
    # fieldsets = (
    #    (None, {'fields': ('categores',)})
    # )
    form = AttributeAdminForm
    inlines = (CategoryAttributeInline,)
    # filter_horizontal = ['category']
    # def get_form(self, request, obj=None, **kwargs):
    #     form = super().get_form(request, obj, **kwargs)
    #     form.base_fields['category'].widget.can_add_related = False  # Disable adding new categories
    #     return form
  
    def formfield_for_manytomany(self, db_field, request, **kwargs):
        print(db_field)
        if db_field.name == 'category':
            kwargs['queryset'] = Category.objects.filter(level=2)
        return super().formfield_for_manytomany(db_field, request, **kwargs)



# Admin class for ValueModel


class ValueModelAdmin(admin.ModelAdmin):
    list_display = ('attribute', 'value')

# Admin class for property_value


class PropertyValueAdmin(admin.ModelAdmin):
    list_display = ('property', 'value')

# Admin class for Category_attribute


class CategoryAttributeAdmin(admin.ModelAdmin):
    list_display = ('category', 'attribute')

# Admin class for Rate


class RateAdmin(admin.ModelAdmin):
    list_display = ('prop', 'user', 'rate', 'time_created')

# Admin class for Favorite


class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('prop', 'user', 'time_created')

# Admin class for Report


class ReportAdmin(admin.ModelAdmin):
    list_display = ('prop', 'user', 'time_created', 'note')

# Admin class for Review


class ReviewAdmin(admin.ModelAdmin):
    list_display = ('prop', 'user', 'time_created', 'review')

# Admin class for Ticket_type


class TicketTypeAdmin(admin.ModelAdmin):
    list_display = ('type',)

# Admin class for Ticket_status


class TicketStatusAdmin(admin.ModelAdmin):
    list_display = ('status',)

# Admin class for Ticket


class TicketAdmin(admin.ModelAdmin):
    list_display = ('type', 'status', 'ticket_solver',
                    'ticket_sender', 'phone_number', 'created_time', 'solved_time', 'email', 'problem_text')

# Admin class for Solve_message


class SolveMessageAdmin(admin.ModelAdmin):
    list_display = ('ticket', 'message')


# Admin class for Property
class PropertyAdmin(admin.ModelAdmin):
    # list_display = ('user', 'category', 'address',
    #                 'name', 'description', 'price', 'size', 'is_active', 'is_deleted', 'time_created', 'unique_number')
    fieldsets = (
        (
            'PropertyINFO',
            {
                'fields': ['name', 'category', 'address', 'price', 'size', 'description', 'user'],
            },


        ),
        (
            'Property Status',
            {
                'fields': ['is_active', 'is_deleted', 'for_sale']
            }

        ),


    )
    list_display = ['name', 'price', 'time_created',]
    inlines = [
        ImageInline,
    ]


class PropertyResource(resources.ModelResource):
    user = fields.Field(column_name='user', attribute='user',
                        widget=widgets.ForeignKeyWidget('auth.User'))
    image_url = fields.Field(column_name='Image URL', attribute='image_url')

    class Meta:
        model = Property
        fields = ('id', 'user', 'name', 'description', 'price',
                  'size', 'is_active', 'is_deleted', 'image_url')
        export_order = fields

    def import_obj(self, instance, data, dry_run):
        image_path = data.get('image_file')
        if image_path:
            try:
                with open(image_path, 'rb') as f:
                    image_file = File(f)
                    instance.image.save(
                        image_file.name, image_file, save=False)
            except FileNotFoundError:
                pass

        super().import_obj(instance, data, dry_run)

    def dehydrate_image_url(self, property):
        return property.image_url


class PropertyAdminImport(ImportExportModelAdmin):
    resource_class = PropertyResource
    fieldsets = (
        (
            'PropertyINFO',
            {
                'fields': ['name', 'category', 'address', 'price', 'size', 'description', 'user'],
            },


        ),
        (
            'Property Status',
            {
                'fields': ['is_active', 'is_deleted', 'is_featured', 'for_sale']
            }

        ),


    )
    list_display = ['name', 'price', 'time_created',]
    inlines = [
        ImageInline,
    ]
# # Admin class for Feature_property
# class FeaturePropertyAdmin(admin.ModelAdmin):
#     list_display = ('property', 'feature')

# Admin class for Attribute


# class AttributeAdmin(admin.ModelAdmin):
#     list_display = ('name', 'data_type', 'categores')

# Admin class for ValueModel


class ValueModelAdmin(admin.ModelAdmin):
    list_display = ('attribute', 'value')

# Admin class for property_value


class PropertyValueAdmin(admin.ModelAdmin):
    list_display = ('property', 'value')

# Admin class for Category_attribute


class CategoryAttributeAdmin(admin.ModelAdmin):
    list_display = ('category', 'attribute')

# Admin class for Rate


class RateAdmin(admin.ModelAdmin):
    list_display = ('prop', 'user', 'rate', 'time_created')
    list_filter = ['rate',]

# Admin class for Favorite


class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('prop', 'user', 'time_created')

# Admin class for Report


class ReportAdmin(admin.ModelAdmin):
    list_display = ('prop', 'user', 'time_created', 'note')
    search_fields = ['prop',]
    list_filter = ['time_created', 'user',]
    date_hierarchy = 'time_created'


# Admin class for Review
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('prop', 'user', 'time_created', 'review')
    list_filter = ['time_created',]

# Admin class for Ticket_type


class TicketTypeAdmin(admin.ModelAdmin):
    list_display = ('type',)

# Admin class for Ticket_status


class TicketStatusAdmin(admin.ModelAdmin):
    list_display = ('status',)

# Admin class for Ticket


class TicketAdmin(admin.ModelAdmin):
    list_display = ('type', 'status', 'ticket_solver',
                    'ticket_sender', 'phone_number', 'created_time', 'solved_time', 'email', 'problem_text')

# Admin class for Solve_message


class SolveMessageAdmin(admin.ModelAdmin):
    list_display = ('ticket', 'message')


class FriendListAdmin(admin.ModelAdmin):
    pass


class PrivateChatRoomAdmin(admin.ModelAdmin):
    pass


class UnradChateMessageAdmin(admin.ModelAdmin):
    pass


class BannerAdmin(admin.ModelAdmin):
    # pass
    list_display = ['title', 'end_time', 'start_time', 'is_active']

    # pass


admin.site.register(Banner, BannerAdmin)
admin.site.register(UnreadChatRoomMessages, UnradChateMessageAdmin)
admin.site.register(PrivateChatRoom, PrivateChatRoomAdmin)

admin.site.register(FriendList, FriendListAdmin)

# Register admin classes
admin.site.register(VerificationCode, VerificationCodeAdmin)
admin.site.register(TypeModel, TypeModelAdmin)
admin.site.register(Attribute_verify, AttributeVerifyAdmin)
admin.site.register(Attribute_value, AttributeValueAdmin)
# admin.site.register(Country, CountryAdmin)
admin.site.register(Country)
admin.site.register(City, CityAdmin)
admin.site.register(State, StateAdmin)
admin.site.register(Address, AddressAdmin)
admin.site.register(Image, ImageAdmin)
# admin.site.register(Category, CategoryAdmin)
admin.site.register(Feature, FeatureAdmin)
# admin.site.register(Feature_category, FeatureCategoryAdmin)
admin.site.register(Property, PropertyAdminImport)
admin.site.register(Feature_property, FeaturePropertyAdmin)
admin.site.register(Attribute, AttributeAdmin)
admin.site.register(ValueModel, ValueModelAdmin)
admin.site.register(property_value, PropertyValueAdmin)
# admin.site.register(Category_attribute, CategoryAttributeAdmin)
admin.site.register(Rate, RateAdmin)
admin.site.register(Favorite, FavoriteAdmin)
admin.site.register(Report, ReportAdmin)
admin.site.register(Review, ReviewAdmin)
admin.site.register(Ticket_type, TicketTypeAdmin)
admin.site.register(Ticket_status, TicketStatusAdmin)
admin.site.register(Ticket, TicketAdmin)
admin.site.register(Solve_message, SolveMessageAdmin)
