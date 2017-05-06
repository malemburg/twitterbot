""" Telegram Bot - PyDDF Sprint 2017

"""
import telebot

###

class TwitterBotChatHandler(telepot.helper.ChatHandler):

    def __init__(self, *args, **kws):
        pass

    def on_chat_message(self, msg):
        pass

class TwitterBotDelegatorBot(telepot.DelegatorBot):
    
    def __init__(self, token, owner_id):
        pass

    

###

def main(config):
    
    bot = TwitterBotDelegatorBot(config.TELEGRAM_BOT_TOKEN,
                                 config.TELEGRAM_BOT_OWNER_ID)
    bot.message_loop(run_forever='TwitterBot listening ...')

###

if __name__ == '__main__':
    import twitterbot_config
    main(twitterbot_config)
