from app import bots, posting, messages
from AWS import keys
import pushbullet
import traceback
import time
from dotenv import load_dotenv
import os
import json
from pushbullet import Pushbullet
import schedule
import threading
from apscheduler.schedulers.background import BackgroundScheduler

scheduler = BackgroundScheduler()
load_dotenv()

PUSHBULLET_KEY = os.environ.get('PUSH_BULLET')


if not PUSHBULLET_KEY:
    TOKEN_OBJ = json.loads(keys.get_secret("PUSH_BULLET"))
  
    PUSHBULLET_KEY = TOKEN_OBJ.get('PUSH_BULLET')
    print("PUSH_BULLET", PUSHBULLET_KEY)
    
restart_days = 3

pb = pushbullet.Pushbullet(PUSHBULLET_KEY)

# Add a bot to every group you have permissions in
filtered_bots = []


def post_periodically(post_interval, filtered_bots, new_message):
    """
    Posts a message to the specified GroupMe groups via the corresponding bots
    every specified number of hours.

    Args:
        auth_token (str): The GroupMe access token for authentication.
        bots (list): A list of bot objects, where each object contains a 'bot_id' and 'group_id'.
        message (str): The message to be sent to the groups.
        post_interval (int): The number of hours to wait between each post.

    Returns:
        None
    """
    print("Post Run")
    schedule.every(post_interval).hours.do()
    scheduler.add_job(posting.send_message_to_groups, 'interval',
                      hours=post_interval, args=[filtered_bots, new_message])
    
    
def post_message_to_groups(bots):
    # Get all bots under a person

    # Set post interval
    

    def post_messages():
        for message in messages.message_duration:
            duration = message.get('duration')
            message_text = message.get('message')
            posting.send_message_to_groups(bots, message_text)
            t = threading.Thread(target=post_periodically, args=(duration, bots, message_text))
            t.start()
        # Post message periodically
    post_messages()
    scheduler.start()
    
def __main__(i):
    #Test Components
    # components_passed = __main__.main()
    
    # Add bots to groups
    add_bots_to_groups = bots.add_bots_to_groups
    add_bots_to_groups()

    # Get all bots under a person
    Bots = bots.get_bots()

    # Filter the Duplicate bots to avoid multiple postings
    filtered_bots = bots.filter_bots(Bots)

    post_message_to_groups(filtered_bots, messages.mlightm, 6)
    post_message_to_groups(filtered_bots, messages.docs, 8)
    post_message_to_groups(filtered_bots, messages.automated_posts, 8)


  


if __name__ == "__main__":
    failure_count = 0
    while True:
        try:
            __main__()
            # reset failure count if successful
            failure_count = 0
        except Exception as e:
            # increment failure count
            failure_count += 1
            # send pushbullet notification on third failure
            if failure_count == 3 :
                pb.push_note("Group Me -","Error in main function  and function tests failing", str(e))
                print(f"Error in main function: {e}")
                failure_count = 0
            # wait for 5 minutes before trying again
            time.sleep(300)
        # Schedule the program to run every 3 days at 2am EST
        schedule.every(restart_days).days.at("02:00").do(__main__)
        # Check if any scheduled tasks are pending and run them
        schedule.run_pending()
        # wait for 1 minute before checking again
        time.sleep(60)

