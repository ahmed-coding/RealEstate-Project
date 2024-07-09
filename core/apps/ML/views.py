from rest_framework import status
from rest_framework.decorators import APIView
from rest_framework.request import Request
from rest_framework.response import Response
from . import serializers
from joblib import load
from django.conf import settings
import numpy as np

model = load(settings.ML_MODELS_PATH / "model.joblib")


class PropertyPricePredictView(APIView):
    """
    Property Price Predict model
    Argament:
        `query`: query to get Predicting Price  For Property in `POST Method`
    """
    serializer_class = serializers.PropertyPricePredictSerializers

    def post(self, request: Request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid(raise_exception=True):
            query = int(serializer.data.get('query'))
            predict_price = model.predict(np.array([[query]]))
            data = serializer.data
            data['price'] = predict_price[0]
            return Response(data=data, status=200)
        else:
            return Response(data=serializer.errors)
