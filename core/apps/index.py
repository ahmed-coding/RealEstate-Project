from algoliasearch_django import AlgoliaIndex
from algoliasearch_django.decorators import register
from .models import Property, Feature, Feature_property, Attribute, ValueModel, property_value


@register(Property)
class PropertyIndex(AlgoliaIndex):
    fields = [
        'id', 'name', 'description', 'price', 'review', 'is_featured', 'for_sale', 'for_rent',
        'address', 'category', 'user_id', 'feature_property', 'property_value', 'image_url', 'unique_number', 'is_active', 'size',
    ]
    settings = {
        'searchableAttributes': [
            'name', 'description', 'address', 'category', 'user_id', 'is_featured', 'for_sale', 'for_rent', 'unique_number', 'is_active', 'size',
            'feature_property.feature.name', 'property_value.value', 'review.rate_review', 'image_url'
        ]
    }
    index_name = 'property_index'


@register(Feature)
class FeatureIndex(AlgoliaIndex):
    fields = ('id', 'name')
    settings = {'searchableAttributes': ['name']}
    index_name = 'feature_index'


@register(Feature_property)
class FeaturePropertyIndex(AlgoliaIndex):
    fields = ('id', 'feature', 'image')
    settings = {'searchableAttributes': ['feature.name']}
    index_name = 'feature_property_index'


@register(Attribute)
class AttributeIndex(AlgoliaIndex):
    fields = ('id', 'name')
    settings = {'searchableAttributes': ['name']}
    index_name = 'attribute_index'


@register(ValueModel)
class ValueIndex(AlgoliaIndex):
    fields = ('id', 'value', 'attribute')
    settings = {'searchableAttributes': ['value', 'attribute.name']}
    index_name = 'value_index'


@register(property_value)
class PropertyValueIndex(AlgoliaIndex):
    fields = ('id', 'value')
    settings = {'searchableAttributes': ['value']}
    index_name = 'property_value_index'
