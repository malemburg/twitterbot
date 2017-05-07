import sys
from twitterbot.twitterfeed import *
import twitterbot_config

# Send a tweet
send_text_tweet(twitterbot_config, sys.argv[1])
