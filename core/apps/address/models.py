from django.db import models
from django.contrib.contenttypes.fields import GenericRelation
from django.utils.translation import gettext_lazy as _


class Country(models.Model):
    """Country model."""

    name = models.CharField(_("Name"), max_length=50)

    class Meta:
        db_table = "Country"

    def __str__(self):
        return self.name


class City(models.Model):
    """City model."""

    name = models.CharField(_("Name"), max_length=50)
    country = models.ForeignKey(
        Country,
        verbose_name=_("Country"),
        on_delete=models.CASCADE,
        related_name="cities",
    )

    class Meta:
        db_table = "City"

    def __str__(self):
        return self.name


class State(models.Model):
    """State model."""

    name = models.CharField(_("Name"), max_length=50)
    city = models.ForeignKey(
        City, verbose_name=_("City"), on_delete=models.CASCADE, related_name="states"
    )

    class Meta:
        db_table = "State"

    def __str__(self) -> str:
        return self.name


class Address(models.Model):
    """Address model."""

    state = models.ForeignKey(
        State,
        verbose_name=_("State "),
        on_delete=models.CASCADE,
        related_name="addresses",
    )
    longitude = models.FloatField(_("Longitude"))
    latitude = models.FloatField(_("Latitude"))
    line1 = models.CharField(_("Line 1"), max_length=255, default="", blank=True)
    line2 = models.CharField(_("Line 2"), max_length=255, default="", blank=True)

    def __str__(self) -> str:
        return (
            f"{self.state.name} {self.state.city.name} {self.state.city.country.name}"
        )

    class Meta:
        db_table = "Address"
