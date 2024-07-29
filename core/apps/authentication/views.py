from django.conf import settings
from django.template import loader
from ..models import generit_random_code
from django.core.mail import send_mail, EmailMessage
from rest_framework.decorators import api_view
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

from .serializers import User, UserAuthSerializer, PasswordResetSerializer


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
            'email': user.email,
            'user_type': user.user_type
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


#### Email Method ######


@api_view(["POST"])
def check_email_velidate(request: Request):
    """
    Argament:
        `email`: to check email validate.
    """
    # print(dir(request.META))
    # for key in request.META :
    #     print(key)

    if request.data.get('email'):
        try:
            email = User.objects.get(email=request.data.get('email'))
            return Response({
                'is_valid': False
            }, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({
                'is_valid': True
            }, status=status.HTTP_200_OK)
    return Response({
        'error': "check-email-velidate"
    }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def send_verify_email(request: Request):
    """
    Argament:
        `email`: to send code.
    """
    if request.data.get('email'):
        try:
            code = generit_random_code(4)
            print(code)
            email = request.data.get('email')
            template = loader.get_template('email-template/code_design.html').render({
                'code': code
            })
            send = EmailMessage(
                "OTP Form RealEstate authentication Verify", template,  settings.EMAIL_HOST_USER, [email, ])
            # send_mail(
            #     f" Welcome Your Code : {code}.", settings.EMAIL_HOST_USER, [email, ], fail_silently=False)
            send.content_subtype = 'html'
            send.send()
            # {
            #     "email": "ahmed.128hemzh@gmail.com"
            # }
            request.session['email_code'] = code
            # request.session['is_verify'] = False
            return Response({
                'code': code
            }, status=status.HTTP_200_OK)
        except Exception as e:
            print(e)
            return Response({"error": e}, status=status.HTTP_204_NO_CONTENT)

    else:
        return Response(status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def verify_email(request: Request):

    email_code = ''
    code = ''
    # and request.session.has_key('is_verify'): -> لما نكمل بشكل كامل لازم يكون create user من هناء لما يكون False يعني مايقع شي
    # if request.session.has_key('email_code'):
    #     email_code = request.session.get('email_code')
    # else:
    #     return Response(status=status.HTTP_401_UNAUTHORIZED)
    if request.data.get('code'):
        code = request.data.get('code')
    else:
        return Response(status=status.HTTP_400_BAD_REQUEST)
    # if email_code == code:        # request.session['is_verify'] = True # هنا

    if code:
        return Response({
            'is_valid': True
        }, status=status.HTTP_200_OK)
    else:
        return Response({
            'is_valid': False
        }, status=status.HTTP_200_OK)

#### End Email Method ######


class PasswordResetView(APIView):
    serializer_class = PasswordResetSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            new_password = serializer.validated_data['new_password']
            user = User.objects.get(email=email)
            # Reset the password
            user.set_password(new_password)
            # user.profile.reset_password_token = ''
            # user.profile.save()
            user.save()

            return Response({"message": "Password has been reset"}, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
