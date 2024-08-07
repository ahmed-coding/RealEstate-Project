from django.urls import path, include
from . import views

urlpatterns = [
    path("", views.PropertyViewsets.as_view({"get": "list"})),
    path("high-rate/", views.PropertyViewsets.as_view({"get": "get_high_rate"})),
    path("bast-seller/", views.BastSellerViewsets.as_view({"get": "list"})),
    path("by-state/", views.PropertyViewsets.as_view({"get": "get_by_state"})),
    path("create/", views.PropertyCreateAPIView.as_view({"post": "create"})),
    path("filter/", views.PropertyFilterViewSet.as_view({"post": "filter"})),
    path("update-list/", views.PropertyCreateAPIView.as_view({"post": "update_list"})),
    path("<int:pk>/", views.PropertyViewsets.as_view({"get": "retrieve"})),
    path(
        "<int:pk>/delete/", views.PropertyCreateAPIView.as_view({"delete": "destroy"})
    ),
    path(
        "<int:pk>/update/",
        views.PropertyCreateAPIView.as_view(
            {"put": "partial_update", "patch": "partial_update"}
        ),
    ),
    path("<int:pkprop>/reviews/", include("apps.review.urls")),
    path(
        "<int:pk>/by-address/",
        views.PropertyViewsets.as_view({"get": "get_by_address"}),
    ),
    # feature Method
    path("feature/create/", views.FeaturePropertyView.as_view({"post": "create"})),
    path(
        "feature/<int:pk>/update/",
        views.FeaturePropertyView.as_view(
            {"put": "partial_update", "patch": "partial_update"}
        ),
    ),
    path(
        "feature/<int:pk>/delete/",
        views.FeaturePropertyView.as_view({"delete": "destroy"}),
    ),
    #     Attribute Method
    path("attribute/create/", views.AttributePropertyView.as_view({"post": "create"})),
    path(
        "attribute/<int:pk>/update/",
        views.AttributePropertyView.as_view(
            {"put": "partial_update", "patch": "partial_update"}
        ),
    ),
    path(
        "attribute/<int:pk>/delete/",
        views.AttributePropertyView.as_view({"delete": "destroy"}),
    ),
    path(
        "attribute/update-property-value/",
        views.UpdateOrCreatePropertyValueView.as_view(),
        name="update_property_value",
    ),
]
