""" Telegram Bot - PyDDF Sprint 2017

"""
import telepot
import telepot.helper
import telepot.delegate
import telepot.exception
from telepot import delegate
import twitterbot_config

###

class TwitterBotChatHandler(telepot.helper.ChatHandler):

    """ This chat handler is instantiated for every chat.

    """

    # Chat ID
    chat_id = None

    # Chat type ('private' or 'group')
    chat_type = 'private'

    def __init__(self, *args, **kws):
        super(TwitterBotChatHandler, self).__init__(*args, **kws)

    def open(self, initial_msg, seed):

        """ Method called when a new chat is started.

        """
        # Use the initial message to access the .chat_type and
        # .chat_id
        (content_type,
         self.chat_type, self.chat_id) = telepot.glance(initial_msg)
        self.sender.sendMessage("Hello, I am the TwitterBot")

    def on_chat_message(self, msg):

        """ Method called for every message sent to the bot.

        """
        (content_type, chat_type, chat_id) = telepot.glance(msg)
        self.sender.sendMessage('debug... content_type=%r msg=%r' % (
            content_type, msg))

        # Get entities (only available if the message contains special
        # entities such as bot commands)
        entities = msg.get('entities', None)
        if entities is None:
            # Normal text without entities
            self.sender.sendMessage(u'No entities found')
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
                self.sender.sendMessage(u'Found bot command %s' % command_name)
                
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

    ### Bot command handlers

    def handle_unknown(self, msg, entity, command_name):

        self.sender.sendMessage(u'Found unknown command %s' % command_name)

    def handle_help_command(self, msg, entity):

        self.sender.sendMessage('Help command\nnew line')

###

class TwitterBotDelegatorBot(telepot.DelegatorBot):

    """ Delegator which manages how chats are handled by the bot.

    """
    # On-idle timeout in seconds
    on_idle_timeout = twitterbot_config.ON_IDLE_TIMEOUT
    
    def __init__(self, token, authorized_users):
        super(TwitterBotDelegatorBot, self).__init__(
            token, [
                # Here is a delegate to specially handle owner commands.
                delegate.pave_event_space()(
                    delegate.per_chat_id_in(authorized_users,
                                            types='private'),
                    delegate.create_open,
                    TwitterBotChatHandler,
                    # Add handler argument here
                    timeout=self.on_idle_timeout)
                ]
            )

###

def main(config):
    
    bot = TwitterBotDelegatorBot(config.TELEGRAM_BOT_TOKEN,
                                 config.AUTHORIZED_USERS)
    bot.message_loop(run_forever='TwitterBot listening ...')

###

if __name__ == '__main__':
    import twitterbot_config
    main(twitterbot_config)
