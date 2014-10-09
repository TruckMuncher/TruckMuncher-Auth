from flask import Flask
from flask import request
from flask import jsonify
app = Flask(__name__)


class InvalidAuthorization(Exception):
    status_code = 401

    def __init__(self, message, status_code=401, payload=None):
        Exception.__init__(self)
        self.message = message
        if status_code is not None:
            self.status_code = status_code
        self.payload = payload


@app.errorhandler(InvalidAuthorization)
def handle_invalid_authorization(error):
    return error.message, error.status_code


@app.route('/', methods=['POST'])
def verify():
    auth = request.headers.get('Authorization').strip().split(',')
    tokens = validate_header_parts(auth)
    if 'access_token' in tokens:
        user = verify_facebook(tokens)
    else:
        user = verify_twitter(tokens)
    return jsonify(user)


def validate_header_parts(components):
    """
    Only allow setting the oauth_token, oauth_secret, and access_token headers.
    """
    tokens = {}
    for part in components:
        if '=' in part:
            (key, value) = part.strip().split('=')
            key = key.strip()
            value = value.strip()
            if key != 'oauth_token' \
                    and key != 'oauth_secret' \
                    and key != 'access_token':
                raise_exception()
            tokens[key] = value
    return tokens


def verify_twitter(tokens):
    """
    If they sent an oauth_token beginning with tw, its valid. Strip the tw and
    the rest of the oauth_token is the user_id they want. The oauth_secret is
    their desired username. Construct a user object and return it. In all other
    cases raise an exception.
    """
    if 'oauth_token' not in tokens or 'oauth_secret' not in tokens:
        raise_exception()
    oauth_token = tokens['oauth_token']
    oauth_secret = tokens['oauth_secret']
    if oauth_token is None or oauth_secret is None:
        raise_exception()
    if len(oauth_token) >= 2 and oauth_token[:2] != 'tw':
        raise_exception()
    return {'user_id': oauth_token, 'username': oauth_secret}


def verify_facebook(tokens):
    if 'access_token' not in tokens:
        raise_exception()
    access_token = tokens['access_token']
    if access_token is None:
        raise_exception()
    if len(access_token) >= 2 and access_token[:2] != 'fb':
        raise_exception()
    (user_id, username) = access_token.split(',')
    return {'user_id': user_id, 'username': username}


def raise_exception(message='Invalid Authorization header'):
    raise InvalidAuthorization(message=message)


if __name__ == "__main__":
    app.debug = True
    app.run()
