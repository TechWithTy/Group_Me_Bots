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
import random

scheduler = BackgroundScheduler()
load_dotenv()

PUSHBULLET_KEY = os.environ.get('PUSH_BULLET')
print(PUSHBULLET_KEY)

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
        bots (list): A list of bot objects, where each object contains a 'bot_id' and 'group_id'.
        new_message (str): The message to be sent to the groups.
        post_interval (int): The number of hours to wait between each post.

    Returns:
        None
    """
    print("Post Run")
    scheduler.add_job(posting.send_message_to_groups, 'interval',
                      hours=post_interval, args=[filtered_bots, new_message])
    
    
def post_message_to_groups(bots):

    for message in messages.message_duration_data:
        if 'images' in message:
            converted_images = {}
            for image in message['images']:
                uploaded_url = posting.upload_image_to_groupme(image)
                converted_images[image] = uploaded_url

            # Choose a random image
            random_image = random.choice(list(converted_images.values()))

            duration = message.get('duration')
            message_text = message.get('message')

            # Append the random image URL to the message_text
            message_text += f" {random_image}"
            print('Image Message Test:',message_text)
            
            posting.send_message_to_groups(bots, message_text)
            t = threading.Thread(target=post_periodically,
                                args=(duration, bots, message_text))
            t.start()
        else:
            duration = message.get('duration')
            message_text = message.get('message')
            print('Message Test:',message_text)


            posting.send_message_to_groups(bots, message_text)
            t = threading.Thread(target=post_periodically,
                                args=(duration, bots, message_text))
            t.start()
            
    
    scheduler.start()
    scheduler.print_jobs()
        # Post message periodically
    try:
        while True:
            pass
    except (KeyboardInterrupt, SystemExit):
        scheduler.shutdown()
        
    
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
    # print(filtered_bots)
    post_message_to_groups(filtered_bots)
    


  



__main__()
      
        

# failure_count = 0
# if __name__ == "__main__" and failure_count < 4:
   
#     try:
#         __main__()
#                 # reset failure count if successful
#         failure_count = 0
#     except Exception as e:
#                 # increment failure count
#                 failure_count += 1
#                 # send pushbullet notification on third failure
#                 if failure_count == 3 :
#                     pb.push_note("Group Me -","Error in main function  and function tests failing", str(e))
#                     print(f"Error in main function: {e}")
#                     failure_count =+ 1
                    
#                 # wait for 5 minutes before trying again
#                 time.sleep(300)
#                 __main__()
        