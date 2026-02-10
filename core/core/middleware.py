
from channels.middleware import BaseMiddleware
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import AnonymousUser
from channels.db import database_sync_to_async


from urllib.parse import parse_qsl

class TokenAuthMiddleware(BaseMiddleware):
    async def __call__(self, scope, receive, send):
        # Get the token from the WebSocket headers or query string
        headers = dict(scope.get("headers", []))
        authorization_header = headers.get(b"authorization", b"")

        auth_token = None
        if authorization_header:
            token = authorization_header[6:]
            auth_token = token.decode("utf-8")
        
        # If not in headers, check query string
        if not auth_token:
            query_string = scope.get("query_string", b"").decode("utf-8")
            query_params = dict(parse_qsl(query_string))
            auth_token = query_params.get("token")

        # Validate the token and set the user in the scope
        scope["user"] = await self.get_user_from_token(auth_token)

        return await super().__call__(scope, receive, send)

    @database_sync_to_async
    def get_user_from_token(self, auth_token):
        try:
            token = Token.objects.get(key=auth_token)
            return token.user
        except Token.DoesNotExist:
            return AnonymousUser()
