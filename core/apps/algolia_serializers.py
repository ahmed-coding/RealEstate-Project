
from rest_framework import serializers
from .models import Property

from .property.serializers import PropertyDetailsSerializers


# class PropertyAlgoliaSerializer(serializers.ModelSerializer):
#     rate_review = serializers.SerializerMethodField()
#     in_favorite = serializers.SerializerMethodField()
#     address = serializers.CharField(
#         source='address.full_address', read_only=True)
#     category = serializers.CharField(source='category.name', read_only=True)
#     user_id = serializers.IntegerField(source='user.id', read_only=True)
#     feature_property = serializers.SerializerMethodField()
#     property_value = serializers.SerializerMethodField()
#     review = serializers.SerializerMethodField()
#     image_url = serializers.SerializerMethodField()

#     def get_rate_review(self, obj):
#         ratings = obj.review.all().values_list('rate_review', flat=True)
#         if ratings:
#             average_rating = sum(ratings) / len(ratings)
#             return round(average_rating, 1)
#         else:
#             return 0.0

#     def get_in_favorite(self, obj):
#         user = self.context.get('user')
#         return obj.favorites.filter(user=user).exists() if user else False

#     def get_feature_property(self, obj):
#         return [{'name': fp.feature.name, 'images': [img.url for img in fp.image.all()]} for fp in obj.feature_property.all()]

#     def get_property_value(self, obj):
#         return [{'value': pv.value.value, 'attribute': pv.value.attribute.name} for pv in obj.property_value.all()]

#     def get_review(self, obj):
#         return [{'rate_review': rev.rate_review, 'review': rev.review} for rev in obj.review.all()]

#     def get_image_url(self, obj):
#         return [image.image.url for image in obj.image.all()]

#     class Meta:
#         model = Property
#         fields = [
#             'id', 'name', 'description', 'price', 'rate_review', 'in_favorite', 'address',
#             'category', 'user_id', 'feature_property', 'property_value', 'image_url', 'unique_number',
#             'is_active', 'size', 'review'
#         ]


class PropertyAlgoliaSerializer(PropertyDetailsSerializers):
    pass
