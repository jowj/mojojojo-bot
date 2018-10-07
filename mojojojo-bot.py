import os
import time
import re
import logging
import json

from pathlib import Path
from slackclient import SlackClient
from json import JSONDecoder
from random import randint
from functools import partial

# instantiate Slack client
slack_client = SlackClient(os.environ.get('SLACK_BOT_TOKEN'))
# starterbot's user ID in Slack: value is assigned after the bot starts up
starterbot_id = None
# channel i want to get ID from
bot_channel = "inmyimo"

# constants
RTM_READ_DELAY = 1   # 1 second delay between reading from RTM
EXAMPLE_COMMAND = "do"
MENTION_REGEX = "^<@(|[WU].+)>(.*)"


def parse_bot_commands(slack_events):
    """
        Parses a list of events coming from the Slack RTM API to find bot commands.
        If a bot command is found, this function returns a tuple of command and channel.
        If its not found, then this function returns None, None.
    """
    if event["type"] == "message" and not "subtype" in event:
        user_id, message = parse_direct_mention(event["text"])
        if user_id == starterbot_id:
            return message, event["channel"]
    return None, None


def parse_direct_mention(message_text):
    """
        Finds a direct mention (a mention that is at the beginning) in message text
        and returns the user ID which was mentioned. If there is no direct mention, returns None
    """
    matches = re.search(MENTION_REGEX, message_text)
    # the first group contains the username, the second group contains the remaining message
    return (matches.group(1), matches.group(2).strip()) if matches else (None, None)


def select_noun():
    with open('/mjj1/corpora.json', 'r') as infh:
        for data in json_parse(infh):
            upper_Limit = len(data["nouns"])
            x = randint(0, upper_Limit)
            if data["nouns"][x]:
                return(data["nouns"][x])
            else:
                return("car")

            
def json_parse(fileobj, decoder=JSONDecoder(), buffersize=2048):
    buffer = ''
    for chunk in iter(partial(fileobj.read, buffersize), ''):
         buffer += chunk
         while buffer:
             try:
                 result, index = decoder.raw_decode(buffer)
                 yield result
                 buffer = buffer[index:]
             except ValueError:
                 # Not enough data to decode, read more
                 break

             
def handle_command(command, channel):
    """
        Executes bot command if the command is known
    """
    # Default response is help text for the user
    default_response = "fuck off bithc"

    # Finds and executes the given command, filling in response
    response = None
    # This is where you start to implement more commands!
    if command.startswith(EXAMPLE_COMMAND):
        response = "Sure...write some more code then I can do that!"
    if command.startswith("say"):
        response = "you're not my real dad"
    if command.startswith("download"):
        response = "you wouldn't download a %s" % (select_noun())

    # Sends the response back to the channel
    slack_client.api_call(
        "chat.postMessage",
        channel=channel,
        text=response or default_response
    )


def reactable_message(event):
    """Test whether a (Slack) event is a reaction-able message

    Check whether it's not a DM, it's not empty, and it's actually a message
    """
    return 'channel' in event and 'text' in event and event.get('type') == 'message'


def reactable_string(text):
    """Return regex objects matching interesting strings
    """
    reactable_array = []
    if re.search(r"\bai\b", text.lower()) is not None:
            reactable_array.append('ai')
    if 'furry' in text.lower() or 'furries' in text.lower() or 'fursuit' in text.lower():
        # no processing needed because: honestly its funnier even if it gets the word boundary wrong.
        reactable_array.append('furry')
    if 'flavor town' in text.lower() or 'flavortown' in text.lower() or 'guy fieri' in text.lower():
        # no processing needed because: honestly its funnier even if it gets the word boundary wrong.
        reactable_array.append('flavortown')
    return reactable_array


def react_to_message(reaction):
    slack_client.api_call(
        'reactions.add',
        channel = get_channel_ID("inmyimo"),
        name = reaction,
        timestamp = event.get('ts')
    )


def react_to_monitoring():    
    results_file = Path("/shared/alerts.log")
    does_file_exist = results_file.is_file()
    logging.info(f"file exists: {does_file_exist}")
    if results_file.is_file():
        open_file = open("/shared/alerts.log","r")
        logging.info('in file exists conditional')
        for line in open_file:
            logging.info('examining item: '+line)
            slack_client.api_call(
            "chat.postMessage",
            channel = get_channel_ID("bots-like-gaston"),
            text = line
            )
        os.remove("/shared/alerts.log")


def get_channel_ID(channelName):
    for channel in slack_client.api_call('channels.list')["channels"]:
        if channel["name"] == channelName:
            return channel["id"]
    raise Exception("couldn't find channel requested.")


if __name__ == "__main__":
    logging.basicConfig(filename='mojojojo.log', level=logging.INFO)
    logging.info('Started')
    results_file = Path("/shared/alerts.log")
    if slack_client.rtm_connect(with_team_state=False):
        print("mojo jojo online,  connected, and running!")
        # Read bot's user ID by calling Web API method `auth.test`
        starterbot_id = slack_client.api_call("auth.test")["user_id"]
        while True:
            if results_file.is_file():
                logging.info("results_file ifstatement passed!")
                react_to_monitoring()            
            for event in (slack_client.rtm_read()):
                command, channel = parse_bot_commands(event)
                if command:
                    handle_command(command, channel)
                if reactable_message(event):
                    channel = event['channel']
                    text = event['text']
                    reactions_needed = reactable_string(text)
                    if 'ai' in reactions_needed:
                        react_to_message("robot_face")
                    if 'furry' in reactions_needed:
                        react_to_message("eggplant")
                        react_to_message("sweat_drops")
                    if 'flavortown' in reactions_needed:
                        react_to_message("dark_sunglasses")
                        react_to_message("guyfieri")
            time.sleep(RTM_READ_DELAY)
        logging.info("Client worked. No errors (we think lol)")
    else:
        print("Connection failed. Exception traceback printed above.")
        logging.info('Check console  for exception traceback.')
    logging.info('Finished')
