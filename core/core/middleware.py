
from channels.middleware import BaseMiddleware
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import AnonymousUser
from channels.db import database_sync_to_async


class TokenAuthMiddleware(BaseMiddleware):
    async def __call__(self, scope, receive, send):
        # Get the token from the WebSocket headers
        # Get the 'Authorization' header from the WebSocket headers
        # Convert headers list to a dictionary
        headers = dict(scope.get("headers", []))
        authorization_header = headers.get(b"authorization", b"")

        # Decode the 'Authorization' header from bytes to string
        auth_token = authorization_header.decode(
            "utf-8") if authorization_header else None

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
