import os
from functools import wraps
from flask import request, jsonify
from jose import jwt, JWTError
from urllib.request import urlopen
import json

AUTH0_DOMAIN = os.environ.get("AUTH0_DOMAIN", "")
AUTH0_AUDIENCE = os.environ.get("AUTH0_AUDIENCE", "")
ROLES_CLAIM = "https://social-insper.com/roles"
ALGORITHMS = ["RS256"]


def _get_jwks():
    url = f"https://{AUTH0_DOMAIN}/.well-known/jwks.json"
    with urlopen(url) as resp:
        return json.loads(resp.read())


def _get_token():
    auth = request.headers.get("Authorization", "")
    if not auth.startswith("Bearer "):
        return None
    return auth.split(" ", 1)[1]


def _decode_token(token):
    jwks = _get_jwks()
    header = jwt.get_unverified_header(token)
    key = next((k for k in jwks["keys"] if k["kid"] == header["kid"]), None)
    if key is None:
        raise JWTError("Public key not found")
    return jwt.decode(token, key, algorithms=ALGORITHMS, audience=AUTH0_AUDIENCE)


def requires_auth(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        token = _get_token()
        if not token:
            return jsonify({"error": "Authorization header missing or malformed"}), 401
        try:
            request.jwt_payload = _decode_token(token)
        except JWTError as e:
            return jsonify({"error": "Invalid token", "detail": str(e)}), 401
        return f(*args, **kwargs)
    return wrapper


def requires_admin(f):
    @wraps(f)
    @requires_auth
    def wrapper(*args, **kwargs):
        roles = request.jwt_payload.get(ROLES_CLAIM, [])
        if "ADMIN" not in roles:
            return jsonify({"error": "Forbidden: ADMIN role required"}), 403
        return f(*args, **kwargs)
    return wrapper
