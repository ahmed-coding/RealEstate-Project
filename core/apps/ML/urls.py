from django.urls import path, include
from . import views
urlpatterns = [
    path('property-price/',views.PropertyPricePredictView.as_view())
    
]
