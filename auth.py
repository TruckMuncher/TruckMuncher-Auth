from flask import Flask
from flask import request
from flask import jsonify
import requests
import twitter
from twitter import TwitterError
import yaml
from os.path import dirname
app = Flask(__name__)


class InvalidAuthorization(Exception):
    status_code = 400

    def __init__(self, message, status_code=400, payload=None):
        Exception.__init__(self)
        self.message = message
        if status_code is not None:
            self.status_code = status_code
        self.payload = payload

    def to_dict(self):
        rv = dict(self.payload or ())
        rv['message'] = self.message
        return rv


@app.errorhandler(InvalidAuthorization)
def handle_invalid_authorization(error):
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response


@app.errorhandler(TwitterError)
def handle_twitter_error(error):
    del error.message[0]['code']
    response = jsonify(error.message[0])
    response.status_code = 400
    return response


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
    tokens = {}
    for part in components:
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
    if 'oauth_token' not in tokens or 'oauth_secret' not in tokens:
        raise_exception()
    api = twitter.Api(consumer_key=twitter_consumer_key,
                      consumer_secret=twitter_consumer_secret,
                      access_token_key=tokens['oauth_token'],
                      access_token_secret=tokens['oauth_secret'])
    user = api.VerifyCredentials()
    return {'user_id': 'tw%s' % user.id, 'username': user.screen_name}


def verify_facebook(tokens):
    if 'access_token' not in tokens:
        raise_exception()
    resp = requests.get('https://graph.facebook.com/debug_token?input_token=%s&access_token=%s|%s' % (tokens['access_token'], facebook_app_id, facebook_secret_key), headers={'Accept': 'application/json'})
    user = resp.json()
    if 'data' not in user or 'app_id' not in user['data']:
        raise_exception()
    if user['data']['app_id'] != facebook_app_id:
        raise_exception(message='You signed in to the wrong Facebook app')
    return {'user_id': 'fb%s' % user['data']['user_id']}


def raise_exception(message='Invalid Authorization header'):
    raise InvalidAuthorization(message=message)


if __name__ == "__main__":
    config_path = '%s%s' % (dirname(dirname(__file__)), 'config.yml')
    with open(config_path) as data:
        configuration = yaml.safe_load(data)
        facebook_app_id = configuration['facebook_app_id']
        facebook_secret_key = configuration['facebook_secret_key']
        twitter_consumer_key = configuration['twitter_consumer_key']
        twitter_consumer_secret = configuration['twitter_consumer_secret']
    app.run()