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
