""" Twitter feed API

"""
import os
import twitter
import threading
import pprint

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

### Tweets

def send_text_tweet(config, text='Hello World !'):
    
    token, token_secret = twitter.read_token_file(
        config.TWITTER_USER_CREDENTIALS)

    twitter_api = twitter.Twitter(
        auth=twitter.OAuth(token, token_secret,
                   config.TWITTER_CONSUMER_KEY,
                   config.TWITTER_CONSUMER_SECRET))

    # Now work with Twitter
    twitter_api.statuses.update(status=text)

### Twitter feed reader

class TwitterFeedThread(threading.Thread):

    # TwitterBot configuration
    config = None

    # OAuth object
    oauth = None
    
    # Function to call to send messages to a TG chat
    send_message = None

    # Run "semaphore"
    run = True

    def __init__(self, config, send_message):

        self.config = config
        self.send_message = send_message
        self.oauth = build_oauth(config)
        super(TwitterFeedThread, self).__init__()

    def run(self):

        """ Check Twitter user stream for updates and send these to the
            TG chat via .send_message().

            This code runs in a separate thread until .run is set to
            False.

            Caveat: Terminating the thread is difficult, since it can
            only check the .run flag when receiving new tweets or
            messages from the stream.

        """
        twitter_userstream = twitter.TwitterStream(
            auth=self.oauth,
            domain='userstream.twitter.com')
        for msg in twitter_userstream.user():
            if not self.run:
                break
            print ('Incoming Twitter stream message:')
            print ('-' * 72)
            pprint.pprint(msg)
            print ('-' * 72)
            if 'text' not in msg:
                # Not a status update, so skip this...
                continue
            self.send_message(u'_Received tweet from @%s:_\n%s' % (
                msg['user']['screen_name'],
                msg['text']),
                parse_mode='Markdown')

    def send_text_tweet(self, text):

        """ Send a new tweet text to the Twitter account.

            Note: This code runs in the thread of the caller, not the
            stream reader.

        """
        if not text:
            # Don't send emtpy tweets
            return
        twitter_api = twitter.Twitter(auth=self.oauth)
        twitter_api.statuses.update(status=text)
        print ('Sent tweet %r' % text)

def run_twitter_feed(config, send_message):

    thread = TwitterFeedThread(config, send_message)
    thread.start()
    return thread

###

def print_twitter_feed(config, domain='userstream.twitter.com'):

    token, token_secret = twitter.read_token_file(
        config.TWITTER_USER_CREDENTIALS)

    oauth=twitter.OAuth(token, token_secret,
                        config.TWITTER_CONSUMER_KEY,
                        config.TWITTER_CONSUMER_SECRET)

    twitter_userstream = twitter.TwitterStream(
        auth=oauth,
        domain=domain)
    for msg in twitter_userstream.user():
        print ('Message received:')
        print ('-' * 72)
        pprint.pprint(msg)
        print ('-' * 72)

if __name__ == '__main__':
    import twitterbot_config
    print_twitter_feed(twitterbot_config)
