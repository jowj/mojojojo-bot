import os
import time
import re
import logging
from slackclient import SlackClient


# instantiate Slack client
slack_client = SlackClient(os.environ.get('SLACK_BOT_TOKEN'))
# starterbot's user ID in Slack: value is assigned after the bot starts up
starterbot_id = None

# constants
RTM_READ_DELAY = 1 # 1 second delay between reading from RTM

if slack_client.rtm_connect():  
    while True:
        events = slack_client.rtm_read()
        for event in events:
            if (
                'channel' in event and
                'text' in event and
                event.get('type') == 'message'
            ):
                channel = event['channel']
                text = event['text']
                if 'blah' in text.lower():
                    print(event.get('ts'))
                    slack_client.api_call(
                        'reactions.add',
                        channel = "bots-like-gaston",
                        name = "thumbsup",
                        timestamp = event.get('ts')
                    )
        time.sleep(1)
else:
    print('Connection failed, invalid token?')