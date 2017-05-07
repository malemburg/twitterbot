import sys
from twitterbot.twitterfeed import *
import twitterbot_config

# Send a tweet
test_tweet(twitterbot_config, sys.argv[1])
