from rest_framework import serializers
from ..models import Property
from ..categorie.serializers import CategorySerializers


class SinglePropertySerializers(serializers.ModelSerializer):
    rate = serializers.SerializerMethodField(read_only=True)
    in_favorite = serializers.SerializerMethodField(read_only=True)

    def get_in_favorite(self, obj) -> bool:
        user = self.context.get('user' or None)
        # if isinstance(user, User) else False
        return obj.favorites.filter(user=user).exists()

    def get_rate(self, obj):
        # user = self.context.get('user' or None)
        rat = obj.rate.all()
        sub = 0.0
        if rat.exists():
            try:
                for s in rat:
                    sub += s.rate
                return round(sub / rat.count(), 1)
            except:
                sub = 0
                return round(sub, 1)
        else:
            return round(sub, 1)

    class Meta:
        model = Property
        fields = '__all__'


class PropertyDetailsSerializers(serializers.ModelSerializer):
    class Meta:
        model = Property
        fields = '__all__'
