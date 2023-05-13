import time
import requests
import __main__
from dotenv import load_dotenv
import os
import json
from AWS import  keys
# Load environment variables from .env file
load_dotenv()
ACCESS_TOKEN = os.environ.get('ZB_PROMO')
# print(ACCESS_TOKEN, 'ACCESS_TOKEN')

if not ACCESS_TOKEN:
    TOKEN_OBJ = json.loads(keys.get_secret("ZB_PROMO"))
  
    ACCESS_TOKEN = TOKEN_OBJ.get('ZB_PROMO')
    
    if(ACCESS_TOKEN):
        print("GROUP ME ACCESS TOKEN FOUND ACCESS_TOKEN")
    
Bot_Name = 'Zort Pro'

#@title Add a bot to every group you have privileges in 
def add_bots_to_groups():
    # Define the API endpoint and headers
    bot_url = f'https://api.groupme.com/v3/bots?token={ACCESS_TOKEN}'
    headers = {'Content-Type': 'application/json'}

    # Define the bot payload
    payload = {
        'bot': {
            'name': Bot_Name,
            'avatar_url': 'https://i.groupme.com/225x225.png.d628db9eb2e648f9bfa206caf4043bef',
            'callback_url': ''
        }
    }
    
    # Get a list of all the groups you're in
    groups_url = f'https://api.groupme.com/v3/groups?token={ACCESS_TOKEN}'
    response = requests.get(groups_url)
    # print(response)
    groups = response.json()['response']

    Bots = []  # Initialize an empty array to store bot objects

    # Loop through each group and add the bot to it
    for i,group in enumerate(groups):
        group_id = group['id']
        payload['bot']['group_id'] = group_id
        response = requests.post(
            bot_url, headers=headers, data=json.dumps(payload))
        if response.status_code == 201:
            bot_id = response.json()['response']['bot']['bot_id']
            print(
                f"Bot 'Zort Pro' added to group '{group_id}' with ID '{bot_id}'.")
            bot_object = {'bot_id': bot_id, 'group_id': group_id}
            Bots.append(bot_object)  # Save the bot object to the array
        else:
            print(
                f"Error adding bot 'Zort Pro' to group '{group_id}'. Status code: {response.status_code}")
        if i > 0:  # Add delay after first loop
            time.sleep(1)
    # print(Bots)
    return Bots  # Return the array of bot objects


######################################
#@title Get All Bots From User


def get_bots() -> list:
    """
    Returns a list of bots associated with the given GroupMe access token.
    """
    # Define the API endpoint and headers
    url = f'https://api.groupme.com/v3/bots?token={ACCESS_TOKEN}'
    headers = {'Content-Type': 'application/json'}

    # Send a request to the endpoint
    response = requests.get(url, headers=headers)

    # Parse the JSON response and add bot data to the Bots array
    Bots = []
    if response.status_code == 200:
        bot_data = response.json()['response']
        for bot in bot_data:
            bot_id = bot['bot_id']
            group_id = bot['group_id']
            bot_name = bot['name']
            Bots.append(
                {'bot_id': bot_id, 'group_id': group_id, 'bot_name': bot_name})
    else:
        print(f"Error getting bot data. Status code: {response.status_code}")
    return Bots


             


######################################################################################

# @title Filter Bots 2

def filter_bots(bots: list)-> list:
    """
    Filters and removes duplicates from the Bots array by comparing group IDs and bot names.
    Keeps only bot names starting with "Zo" and removes those starting with "Gort".

    Args:
        bots (list): A list of bot objects, where each object contains a 'bot_id', 'group_id', and 'bot_name'.

    Returns:
        list: The filtered Bots array with duplicates removed and bot names filtered.
    """
    filtered_bots = []
    seen_groups = set()

    for bot in bots:
        if bot['bot_name'].startswith('Gort'):
            continue
        if bot['group_id'] in seen_groups:
            continue
        if 'Zo' not in bot['bot_name']:
            continue
        filtered_bots.append(bot)
        seen_groups.add(bot['group_id'])
    # print(filtered_bots)
    return filtered_bots




