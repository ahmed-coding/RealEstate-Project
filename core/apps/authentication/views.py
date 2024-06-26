from rest_framework.authtoken.views import ObtainAuthToken, AuthTokenSerializer
from rest_framework.authtoken.models import Token
from rest_framework import generics
from rest_framework.response import Response
from rest_framework.views import APIView, Request, status
from rest_framework.generics import CreateAPIView, GenericAPIView
from django.contrib.auth import logout, authenticate, login
from rest_framework.permissions import IsAuthenticated
import firebase_admin
from firebase_admin import firestore

from .serializers import User, UserAuthSerializer


class CustomAuthToken(CreateAPIView):
    serializer_class = AuthTokenSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data,
                                           context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        login(request, user)
        return Response({
            'token': token.key,
            'user_id': user.pk,
            'email': user.email
        })


class ReigsterView(CreateAPIView):
    """
    ReigsterAPI to create user if request.session.has_key('email_code') and request.session.has_key('is_verify') is True
    and he will be replace the another view in User.view for Customer at new
    """
    # authentication_classes = [JWTAuthentication]
    # permission_classes = [IsAuthenticated]
    model = User
    serializer_class = UserAuthSerializer

    def post(self, request: Request):
        """
        Reigster User View to signup after verify the ``email`` or ``phone number`` (just email for new).
        Returns:
        - in_Success:
            - data: (``string``) -> message from server.
            - user: (``User``) -> data of user after created.
            - status_code : 200 
        - in_Fail:
            - error: (``string``) -> Error Message.
            - status: 401 when come bafore verify the ``email`` or ``phone_number``.
            - status: 400 when data isn't correct or somthing go to by wrong.
        """
        # print(generit_random_code())
        # print(type(generit_random_code()))

        # print(generit_random_code())
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid(raise_exception=True):
            user = serializer.save()
            user_data = serializer.validated_data
            # Synchronize user data with Firebase Realtime Database or Firestore
            # db = firestore.client()
            # users_ref = db.collection('Users')
            # users_ref.document(user.id).set({
            #     'email': user_data['email'],
            #     'fullName': user_data.get('name', ''),
            #     'userType' : user_data.get('user_type', ''),
            #     'phone_number': user_data.get('phone_number', ''),
            #     'imageUrl' : user_data.get('image', ''),
            #     # Add other fields as needed
            # }, merge=True)
            return Response(
                serializer.data, status=status.HTTP_200_OK)
        else:
            return Response({
                'error': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)


class LogoutView(APIView):

    """
    this will be take ``refresh`` token and add it to blackList
    Method :
        >>> [POST]
        dont add more
    """
    # authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = None

    def post(self, request: Request):
        """
        >>> LOGIN REQUIRD WITH JWT:
        - Try to get Authentication from User it's self by JWT[refresh].
        - then fo get AUTHORIZATION from request[META],

        Returns:
        - data: login done if the logiut success.
        - status: 200 or 401
        """
        # request.auth
        # d = TokenUser(request.auth)
        # d.delete()

        logout(request=request)
        return Response(data={
            'data': 'Logout done'
        }, status=status.HTTP_200_OK)
