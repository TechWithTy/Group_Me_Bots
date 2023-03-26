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


def post_message_to_groups(bots,message,interval):
    # Get all bots under a person
    
    posting.send_message_to_groups(filtered_bots, message)

    # Set post interval
 

    # Post message periodically
    posting.post_periodically(interval, filtered_bots, message)
    
    
def __main__():
    #Test Components
    # components_passed = __main__.main()
    
    # Add bots to groups
    add_bots_to_groups = bots.add_bots_to_groups
    add_bots_to_groups()

    # Get all bots under a person
    Bots = bots.get_bots()

    # Filter the Duplicate bots to avoid multiple postings
    filtered_bots = bots.filter_bots(Bots)

    post_message_to_groups(filtered_bots,messages.test_text,2)
   

  


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

