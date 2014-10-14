TruckMuncher Auth
=================

## Project Setup ##
These steps are used for running the server locally.

1. Install [PIP](http://www.pip-installer.org/en/latest/installing.html)
2. Install Virtualenv

        $ sudo pip install virtualenv

3. Create a virtualenv

        $ virtualenv venv

4. Activate the virtualenv

        $ source venv/bin/active

5. Install project dependencies

        $ pip install -r requirements.txt

6. Run one of the two servers

        $ python auth.py
        $ python fake_auth.py

### Using Real Auth
You will need to configure the `config.yml` in the root of the project. This file needs four keys

    facebook_app_id: ...
    facebook_secret_key: ...
    twitter_consumer_key: ...
    twitter_consumer_secret: ...

Insert appropriate values in `config.yml` before running the `auth.py` server.

### Using Fake Auth
Using fake auth, the user is always authenticated and is never checked against Twitter or Facebook.

For a Facebook user, the value of your Authorization header should be formatted as `access_token=theUserID|theUserName`.

For a Twitter user, the value of your Authorization header should be formatted as 
`oauth_token=theUserId,oauth_secret=theUserName`.