from django.contrib import admin
from . import models
from django import forms
# Register your models here.


class SendNotification(forms.Form):
    content = forms.CharField(label="notification content", max_length=255)


@admin.register(models.Notification)
class NotificationAdmin(admin.ModelAdmin):
    add_form_templat = "admin/custom_add_form.html"
    list_display = ('content',)


admin.site.register(model_or_iterable=[
    models.City,
    models.Category,
    models.User,
    models.Category_attribute,
    models.property_value,
    models.Property,
    models.Feature_property,
    models.Country,
    models.Address,
    models.Feature_category
])
