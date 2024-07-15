from rest_framework import authentication
from rest_framework.exceptions import AuthenticationFailed, ParseError
from django.conf import settings
from datetime import datetime, timedelta
import jwt
from Users.models import User

class JWTAuthentication(authentication.BaseAuthentication):
    def authenticate(self, request):
        # Extract the JWT from the Authorization header
        jwt_token = request.META.get('HTTP_AUTHORIZATION')
        if jwt_token is None:
            return None

        jwt_token = self.get_the_token_from_header(jwt_token)  # clean the token

        # Decode the JWT and verify its signature
        try:
            payload = jwt.decode(jwt_token, settings.SECRET_KEY, algorithms=['HS256'])
        except jwt.exceptions.InvalidSignatureError:
            raise AuthenticationFailed('Invalid signature')
        except:
            raise ParseError()  
        # Check if the payload contains 'access' and decode it
        if 'access' in payload:
            try:
                access_payload = jwt.decode(payload['access'], settings.SECRET_KEY, algorithms=['HS256'])
            except jwt.exceptions.InvalidSignatureError:
                raise AuthenticationFailed('Invalid signature')
            except:
                raise ParseError()   
            # Extract user identifier from the nested access payload
            user_identifier = access_payload.get('id')
        else:
            user_identifier = payload.get('id')
        
        if user_identifier is None:
            raise AuthenticationFailed('User identifier not found in JWT')

        # Get the user from the database
        user = User.objects.filter(username=user_identifier).first()
        if user is None:
            
            user = User.objects.filter(pk=user_identifier).first()
            if user is None:
                
                raise AuthenticationFailed('User not found')
        # Return the user and token payload
        return (user, payload)

    def authenticate_header(self, request):
        return 'Bearer'

    @classmethod
    def create_jwt(cls, user):
        # Create the JWT payload
        payload = {
            'user_identifier': user.username,
            'exp': int((datetime.now() + timedelta(hours=settings.JWT_CONF['TOKEN_LIFETIME_HOURS'])).timestamp()),
            'iat': datetime.now().timestamp(),
            'username': user.username,
        }

        # Encode the JWT with your secret key
        jwt_token = jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256')

        return jwt_token

    @classmethod
    def get_the_token_from_header(cls, token):
        token = token.replace('Bearer', '').replace(' ', '')  # clean the token
        return token
