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


@app.errorhandler(TwitterError)
def handle_twitter_error(error):
    del error.message[0]['code']
    return error.message[0]['message'], 401


@app.route('/', methods=['POST'])
def verify():
    auth = request.headers.get('Authorization').strip().split(',')
    tokens = validate_header_parts(auth)
    if 'access_token' in tokens:
        user = verify_facebook(tokens)
    else:
        user = verify_twitter(tokens)
    return jsonify(user)


@app.route('/username', methods=['POST'])
def get_username():
    auth = request.headers.get('Authorization').strip().split(',')
    tokens = validate_header_parts(auth)
    if 'access_token' not in tokens:
        raise_exception(message='Only Facebook users must retrieve their usernames separately from their user')
    resp = requests.get('https://graph.facebook.com/me?access_token=%s' % (tokens['access_token'],), headers={'Accept': 'application/json'})
    user = resp.json()
    if 'name' not in user:
        raise_exception(message='Invalid Facebook user specified')
    return jsonify({'username': user['name']})


def validate_header_parts(components):
    tokens = {}
    for part in components:
        if '=' in part:
            (key, value) = part.strip().split('=')
            key = key.strip()
            value = value.strip()
            if key != 'oauth_token' \
                    and key != 'oauth_secret' \
                    and key != 'access_token' \
                    and key != 'session_token':
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
        facebook_app_id = str(configuration['facebook_app_id'])
        facebook_secret_key = configuration['facebook_secret_key']
        twitter_consumer_key = configuration['twitter_consumer_key']
        twitter_consumer_secret = configuration['twitter_consumer_secret']
    app.run(host='0.0.0.0')
