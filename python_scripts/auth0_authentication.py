"""Auth handlers"""
import json
import datetime

from functools import wraps
from urllib.request import urlopen
import urllib

from auth0.v3.authentication import GetToken
from auth0.v3.authentication import Database
from auth0.v3.management import Auth0

from flask import request
from jose import jwt

from db_functions import select_user_active_orgs_and_roles

from class_errors import AuthError
from settings import Settings

#  Declare AUth0 vars
AUTH0_AUDIENCE = Settings.get_setting('AUTH0_AUDIENCE')
ALGORITHMS = ['RS256']

AUTH0_CLIENT_ID = Settings.get_setting('AUTH0_CLIENT_ID')
AUTH0_CLIENT_SECRET = Settings.get_setting('AUTH0_CLIENT_SECRET')
AUTH0_CONNECTION = Settings.get_setting('AUTH0_CONNECTION')
AUTH0_DOMAIN = Settings.get_setting('AUTH0_DOMAIN')
AUTH0_MGT_AUDIENCE = Settings.get_setting('AUTH0_MGT_AUDIENCE')

# To check is enviroment variables are set
if not AUTH0_CLIENT_ID:
    print("AUTH0_CLIENT_ID is not set")

if not AUTH0_CLIENT_SECRET:
    print("AUTH0_CLIENT_SECRET is not set")

if not AUTH0_CONNECTION:
    print("AUTH0_CONNECTION is not set")

if not AUTH0_DOMAIN:
    print("AUTH0_DOMAIN is not set")


class JWKSClass:
    """Class to manage JWKS"""
    jwks = None
    refresh_time = None

    def get(self):
        """Get the JWKS object"""
        if self.jwks and self.refresh_time > datetime.datetime.now():
            return self.jwks

        jsonurl = urlopen("https://" + AUTH0_DOMAIN + "/.well-known/jwks.json")

        str_response = jsonurl.read().decode('utf-8')

        self.jwks = json.loads(str_response)
        self.refresh_time = datetime.datetime.now() + datetime.timedelta(
            hours=5)

        return self.jwks


JWKS = JWKSClass()


# Format error response and append status code
def get_token_auth_header():
    """Obtains the Access Token from the Authorization Header
    """
    auth = request.headers.get("Authorization", None)
    if not auth or auth == 'Bearer null':
        raise AuthError({
            "code": "authorization_header_missing",
            "message": "Authorization header is expected"
        }, 401)

    parts = auth.split()

    if parts[0].lower() != "bearer":
        raise AuthError(
            {
                "code": "invalid_header",
                "message": "Authorization header must start with Bearer"
            }, 401)
    elif len(parts) == 1:
        raise AuthError({
            "code": "invalid_header",
            "message": "Token not found"
        }, 401)
    elif len(parts) > 2:
        raise AuthError({
            "code": "invalid_header",
            "message": "Authorization header must be Bearer token"
        }, 401)

    token = parts[1]
    return token


def get_unverified_header(token):
    """Get the unverified token header, throw error if invalid"""
    try:
        unverified_header = jwt.get_unverified_header(token)
    except jwt.JWTError:
        raise AuthError(
            {
                "code": "invalid_header",
                "message":
                "Invalid header. Use an RS256 signed JWT Access Token"
            }, 401)
    if unverified_header["alg"] == "HS256":
        raise AuthError(
            {
                "code": "invalid_header",
                "message":
                "Invalid header. Use an RS256 signed JWT Access Token"
            }, 401)

    return unverified_header


def get_rsa_key(jwks, unverified_header):
    """get the applicable rsa key for a given token"""
    rsa_key = {}
    for key in jwks["keys"]:
        if key["kid"] == unverified_header["kid"]:
            rsa_key = {
                "kty": key["kty"],
                "kid": key["kid"],
                "use": key["use"],
                "n": key["n"],
                "e": key["e"]
            }

    if not rsa_key:
        raise AuthError({
            "code": "invalid_header",
            "message": "Unable to find appropriate key"
        }, 401)

    return rsa_key


def get_payload(token, rsa_key) -> dict:
    """Get JWT payload, throw error if invalid"""
    try:
        payload = jwt.decode(
            token,
            rsa_key,
            algorithms=ALGORITHMS,
            audience=AUTH0_AUDIENCE,
            issuer="https://" + AUTH0_DOMAIN + "/")
    except jwt.ExpiredSignatureError:
        raise AuthError({
            "code": "token_expired",
            "message": "token is expired"
        }, 401)
    except jwt.JWTClaimsError:
        raise AuthError(
            {
                "code": "invalid_claims",
                "message":
                "incorrect claims, please check the audience and issuer"
            }, 401)
    except Exception:
        raise AuthError({
            "code": "invalid_header",
            "message": "Unable to parse authentication token."
        }, 401)

    return payload


def get_user(kwargs):
    token = get_token_auth_header()
    jwks = JWKS.get()
    unverified_header = get_unverified_header(token)
    rsa_key = get_rsa_key(jwks, unverified_header)
    payload = get_payload(token, rsa_key)

    # make sure the access token has an email address
    try:
        email = payload['https://s2s.wilcompute.com/email']
    except KeyError:
        raise AuthError({
            "code": "missing_email",
            "message": "Unable to determine user's ID"
        }, 401)

    # get orgs and roles for this email address
    user = select_user_active_orgs_and_roles(email)

    # this can happen if the user exists in Auth0 but not in the local db
    # or if the user exists in Auth0 but all accounts are disabled
    if not user:
        raise AuthError(
            {
                "code": "user_doesnt_exist",
                "message": "User not enabled in this API"
            }, 401)

    # if the request is for something within an org,
    # check that user has any sort of access
    # and apply the org and role to the user
    # rules engine will determine granular access later

    try:
        requested_org_id = kwargs['organization_id']

        try:
            user_org_role = next(
                org_role for org_role in user['org_roles'] if org_role['organization']['id'] == requested_org_id)
            user['user_id'] = user_org_role['user_id']
            user['organization_id'] = user_org_role['organization']['id']
            user['organization'] = user_org_role['organization']
        except (StopIteration, KeyError):
            raise AuthError(
                {
                    "code": "accessing_wrong_org",
                    "message": "Attempting to access wrong organization"
                }, 403)
    except KeyError:
        requested_org_id = None

    return user


def requires_auth(decorated_func):
    """Determines if the access token is valid
    """

    @wraps(decorated_func)
    def decorated(self, *args, **kwargs):
        """Decorator that gets and validates auth"""
        return decorated_func(self, get_user(kwargs), *args, **kwargs)

    return decorated


def auth0_client():
    """Get an Auth0 management client"""
    get_token = GetToken(AUTH0_DOMAIN)
    token = get_token.client_credentials(
        AUTH0_CLIENT_ID, AUTH0_CLIENT_SECRET,
        'https://{}/api/v2/'.format(AUTH0_DOMAIN))
    mgmt_api_token = token['access_token']

    auth0 = Auth0(AUTH0_DOMAIN, mgmt_api_token)

    return auth0


def auth0_login(username, password):
    """Perform login for devices that can't do Auth0"""
    auth_data = {
        'grant_type': "password",
        'client_id': AUTH0_CLIENT_ID,
        'client_secret': AUTH0_CLIENT_SECRET,
        'audience': AUTH0_AUDIENCE,
        'username': username,
        'password': password,
        'scope': "openid email"
    }

    auth_data = bytes(json.dumps(auth_data), 'utf-8')

    auth_request = urllib.request.Request(
        'https://{}/oauth/token'.format(AUTH0_DOMAIN),
        data=auth_data,
        headers={'content-type': 'application/json'})

    with urllib.request.urlopen(auth_request) as response:
        json_response = json.loads(response.read().decode('utf-8'))

    return json_response


def auth0_reset_pw(email):
    """Initiate password reset"""
    auth0_db = Database(AUTH0_DOMAIN)
    return auth0_db.change_password(AUTH0_CLIENT_ID, email, AUTH0_CONNECTION)
