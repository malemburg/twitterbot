""" Twitter feed API

"""
import os
import twitter
import threading

### Helpers

def check_file_access(filename,
                      error_message='File not writeable: %r',
                      remove_file_if_exists=False):
    
    if not os.path.exists(filename):
        # Check if file location is writeable
        try:
            open(filename, 'w')
        except IOError as reason:
            raise IOError(error_message %
                          filename)
        else:
            if remove_file_if_exists:
                os.remove(filename)

### Authentiation

def connect_app(config):

    # OAuth credentials
    credentials_file = config.TWITTER_USER_CREDENTIALS
    check_file_access(credentials_file,
                      'TwitterBot credentials file not writeable: %r')

    # Run OAuth dance (opening a webbrowser)
    (token, token_secret) = twitter.oauth_dance(
        config.APP_NAME,
        config.TWITTER_CONSUMER_KEY,
        config.TWITTER_CONSUMER_SECRET,
        credentials_file)

    # Convert consumer key/secret to OAuth2 bearer token
    bearer_file = config.TWITTER_BEARER_CREDENTIALS
    check_file_access(bearer_file,
                      'TwitterBot bearer credentials file not writeable: %r')

    # Run OAuth2 dance and store credentials
    token = twitter.oauth2_dance(
        config.TWITTER_CONSUMER_KEY,
        config.TWITTER_CONSUMER_SECRET)
    twitter.write_bearer_token_file(bearer_file, token)

def build_oauth(config):

    if not os.path.exists(config.TWITTER_USER_CREDENTIALS):
        raise ValueError('App not yet connected to Twitter account')
    (token, token_secret) = twitter.read_token_file(
        config.TWITTER_USER_CREDENTIALS)
    return twitter.OAuth(token, token_secret,
                         config.TWITTER_CONSUMER_KEY,
                         config.TWITTER_CONSUMER_SECRET)
### Feed thread

def twitter_feed_thread(bot, chat_id, oauth):

    twitter_userstream = twitter.TwitterStream(
        auth=oauth,
        domain='userstream.twitter.com')
    for msg in twitter_userstream.user():
        bot.sendMessage(chat_id,
                        u'Tweet: %s' % msg)

def run_twitter_feed(config, bot, chat_id):

    oauth = build_oauth(config)
    thread = threading.Thread(target=twitter_feed_thread,
                              kwargs=dict(bot=bot,
                                          chat_id=chat_id,
                                          oauth=oauth))
    thread.start()

### Tests

def test_tweet(config, text='Hello World !'):
    
    token, token_secret = twitter.read_token_file(
        config.TWITTER_USER_CREDENTIALS)

    twitter_api = twitter.Twitter(
        auth=twitter.OAuth(token, token_secret,
                   config.TWITTER_CONSUMER_KEY,
                   config.TWITTER_CONSUMER_SECRET))

    # Now work with Twitter
    twitter_api.statuses.update(status=text)

###

if __name__ == '__main__':
    import twitterbot_config
    connect_app(twitterbot_config)
