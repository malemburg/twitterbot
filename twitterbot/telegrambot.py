""" Telegram Bot - PyDDF Sprint 2017

"""
import pprint
import telepot
import telepot.helper
import telepot.delegate
import telepot.exception
from telepot import delegate
from twitterbot import twitterfeed

### Constants

HELP = """\
Welcome to the TwitterBot Telegram Bot
======================================

Available commands:

/connect   - connect to the configured Twitter account
/tweet msg - tweet msg to the connected Twitter account
/help      - this text

"""

###

class TwitterBotChatHandler(telepot.helper.ChatHandler):

    """ This chat handler is instantiated for every chat.

    """
    # TwitterBot configuration
    config = None

    # .chat_id is provided by the ChatContext as property 

    # Chat type ('private', 'group', 'channel')
    chat_type = 'private'

    # Twitter feed thread
    twitter = None

    def __init__(self, *args, **kws):

        self.config = kws['config']
        del kws['config']
        super(TwitterBotChatHandler, self).__init__(*args, **kws)

    def open(self, initial_msg, seed):

        """ Method called when a new chat is started.

        """
        # Remember the .chat_type of this chat
        (content_type, self.chat_type, chat_id) = telepot.glance(initial_msg)
        self.sender.sendMessage("Hello, I am the TwitterBot (chat %s)" % chat_id)
        print ('Telegram chat %r started' % chat_id)

    def on_chat_message(self, msg):

        """ Method called for every message sent to the bot.

        """
        (content_type, chat_type, chat_id) = telepot.glance(msg)
        print ('Incoming Telegram message (chat_id=%r, content_type=%r):' %
               (chat_id, content_type))
        print ('-' * 72)
        pprint.pprint(msg)
        print ('-' * 72)

        # Get entities (only available if the message contains special
        # entities such as bot commands)
        entities = msg.get('entities', None)
        if entities is None:
            # Normal text without entities
            print ('No entities found')
            return

        # Process bot commands
        for entity in entities:
            msg_type = entity.get('type', None)
            if msg_type == 'bot_command':
                offset = entity.get('offset', 0)
                length = entity.get('length', 0)
                command_name = msg.get('text', '')[offset:offset + length]
                if not command_name.startswith('/'):
                    # Ignore command
                    continue
                print ('Found bot command %r' % command_name)
                
                # Make sure we get an ASCII command and remove leading slash
                command = command_name.encode('ascii', 'replace')[1:]

                # Call handler, if any
                handler = getattr(self, 'handle_%s_command' % command, None)
                if handler is None:
                    self.handle_unknown(msg, entity, command_name)
                else:
                    handler(msg, entity)

    def on__idle(self, event):

        """ Method called when the chat is idling.

            The idle timeout is set in the TwitterBotDelegatorBot.

        """
        self.sender.sendMessage('Bye bye.')

        # Terminate the chat in case it is idling
        raise telepot.exception.IdleTerminate(event['_idle']['seconds'])

    def on_close(self, msg):

        """ Method called when the chat is closed.

        """
        self.twitter.run = False
        # We should wait for the thread to terminate, but this can
        # take very long (until the user posts a new tweet), so we
        # punt on this
        #self.twitter.join()
        return True

    ### Bot command handlers

    def handle_unknown(self, msg, entity, command_name):

        print ('Unknown bot command %r' % command_name)
        self.sender.sendMessage(u'Found unknown command %s' % command_name)

    def handle_help_command(self, msg, entity):

        print ('Help command called')
        self.sender.sendMessage(HELP)

    def handle_tweet_command(self, msg, entity):

        print ('Tweet command called')

        # Are we connected yet ?
        if self.twitter is None:
            self.sender.sendMessage(u'Not yet connected to Twitter account. '
                                    'Use /connect to connect.')
            print ('Not yet connected')
            return

        # Extract tweet text
        text = msg.get('text', '')
        offset = entity.get('offset', 0)
        length = entity.get('length', 0)
        
        # Tweet is everything following the /tweet command
        tweet = text[offset + length + 1:]
        self.twitter.send_text_tweet(tweet)

    def handle_connect_command(self, msg, entity):

        print ('Connect command called')

        # Don't connect twice
        if self.twitter is not None:
            self.sender.sendMessage(u'Already connected to Twitter account. '
                                    'Use /tweet msg to send tweets.')
            print ('Already connected')
            return
        
        # Start Twitter feed thread
        self.twitter = twitterfeed.run_twitter_feed(self.config,
                                                        self.sender.sendMessage)
        self.sender.sendMessage(u'Connected to Twitter account. '
                                'Use /tweet msg to send tweets.')
 

###

class TwitterBotDelegatorBot(telepot.DelegatorBot):

    """ Delegator which manages how chats are handled by the bot.

    """
    # TwitterBot configuration
    config = None
    
    # On-idle timeout in seconds
    on_idle_timeout = 60*60
    
    def __init__(self, config, on_idle_timeout=None):
        self.config = config
        if on_idle_timeout is not None:
            self.on_idle_timeout = on_idle_timeout
        else:
            self.on_idle_timeout = config.ON_IDLE_TIMEOUT
        super(TwitterBotDelegatorBot, self).__init__(
            config.TELEGRAM_BOT_TOKEN, [
                # Here is a delegate to specially handle owner commands.
                delegate.pave_event_space()(
                    delegate.per_chat_id_in(config.AUTHORIZED_USERS,
                                            types='private'),
                    delegate.create_open,
                    TwitterBotChatHandler,
                    # Add handler arguments here
                    config=config,
                    timeout=self.on_idle_timeout)
                ]
            )

###

def main(config):

    bot = TwitterBotDelegatorBot(config)
    bot.message_loop(run_forever='TwitterBot listening ...')

###

if __name__ == '__main__':
    import twitterbot_config
    main(twitterbot_config)
