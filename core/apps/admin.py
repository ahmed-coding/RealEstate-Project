from statistics import mode
from django.contrib import admin
from . import models
from django import forms
from .models import Category
# Register your models here.
from mptt.admin import DraggableMPTTAdmin


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
    models.User,
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
])
