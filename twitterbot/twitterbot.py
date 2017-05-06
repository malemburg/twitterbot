""" Telegram Bot - PyDDF Sprint 2017

"""
import telepot
import telepot.helper
import telepot.delegate
from telepot import delegate
import twitterbot_config

###

class TwitterBotChatHandler(telepot.helper.ChatHandler):

    def __init__(self, *args, **kws):
        super(TwitterBotChatHandler, self).__init__(*args, **kws)

    def on_chat_message(self, msg):
        self.sender.sendMessage('Hello world!')

class TwitterBotDelegatorBot(telepot.DelegatorBot):

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
