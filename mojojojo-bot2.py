import os
import time
import re
import logging
from slackclient import SlackClient
import pdb


# instantiate Slack client
slack_client = SlackClient(os.environ.get('SLACK_BOT_TOKEN'))
# starterbot's user ID in Slack: value is assigned after the bot starts up
starterbot_id = None
# channel i care about:
bot_channel = "bots-like-gaston"

# constants
RTM_READ_DELAY = 1 # 1 second delay between reading from RTM


def reactable_message(event):
    """Test whether a (Slack) event is a reaction-able message

    Check whether it's not a DM, it's not empty, and it's actually a message
    """
    return 'channel' in event and 'text' in event and event.get('type') == 'message'

def get_channel_ID(channelName):
    for channel in slack_client.api_call('channels.list')["channels"]:
        if channel["name"] == channelName:
            return channel["id"]
    raise Exception("couldn't find channel requested.")
        
if slack_client.rtm_connect():  
    while True:
        events = slack_client.rtm_read()
        for event in events:
            if reactable_message(event):
                channel = event['channel']
                text = event['text']
                if 'blah' in text.lower():
                    print(event.get('ts')) # does this populate
                    pdb.set_trace()
                    slack_client.api_call(
                        'reactions.add',
                        channel = get_channel_ID("bots-like-gaston"),
                        name = "thumbsup",
                        timestamp = event.get('ts')
                    )
        time.sleep(1)
else:
    print('Connection failed, invalid token?')