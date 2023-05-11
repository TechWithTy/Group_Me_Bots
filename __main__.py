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
import datetime

from typing import Optional,List
scheduler = BackgroundScheduler()
load_dotenv()


PRODUCTION = False

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
default_values = {}

default_interval = 2
default_times = ['8:37','12:15','5:55']


def post_periodically(filtered_bots: list, post_times: Optional[List[str]] = default_times, post_interval: Optional[int] = default_interval,  new_message: str = "Issa Bot", uploaded_images: Optional[str] = None) -> str:
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
    if post_times is not None:

        for post_time in post_times:
            time_obj = datetime.datetime.strptime(post_time, "%H:%M").time()
            print(f"Post scheduled for {post_time}")
            scheduler.add_job(posting.send_message_to_groups, 'date', run_date=time_obj,
                              args=[filtered_bots, new_message, uploaded_images])
        return
 
        
    if post_interval:
        print("Post Run")
        scheduler.add_job(posting.send_message_to_groups, 'interval',
                        hours=post_interval, args=[filtered_bots, new_message,uploaded_images])
        return
        
    
def post_message_to_groups(bots):

    for message in messages.message_duration_data:
        
        
       print(message)
       
       if 'images' in message:
           
        uploaded_images = []
        
        for image in message['images']:
            uploaded_url = posting.upload_image_to_groupme(image)
            uploaded_images.append(uploaded_url)

        # Choose a random image

        duration = message.get('duration')
        message_text = message.get('message')
        times = message.get('times')
      
      
        if (PRODUCTION):
            posting.send_message_to_groups(bots, message_text,uploaded_images)
       else:
        print('message posted' + message_text)
        if (PRODUCTION):
            posting.send_message_to_groups(bots, message_text)

        
        if duration:
            t = threading.Thread(target=post_periodically,
                        args=(),
                        kwargs={
                            'post_interval': duration,
                            'filtered_bots': bots,
                            'new_message': message_text,
                            'uploaded_images': uploaded_images
                        })  
        if times:
            t = threading.Thread(target=post_periodically,
                                 args=(),
                                 kwargs={
                                     'post_times': times,
                                     'filtered_bots': bots,
                                     'new_message': message_text,
                                     'uploaded_images': uploaded_images
                                 })
        t.start()
    else:
        duration = message.get('duration')
        message_text = message.get('message')
        times = message.get('times')
        
        

        
        if duration:
            t = threading.Thread(target=post_periodically,
                        args=(),
                        kwargs={
                            'post_interval': duration,
                            'filtered_bots': bots,
                            'new_message': message_text,
                            'uploaded_images': uploaded_images
                        })  
        if times:
            t = threading.Thread(target=post_periodically,
                                 args=(),
                                 kwargs={
                                     'post_times': times,
                                     'filtered_bots': bots,
                                     'new_message': message_text,
                                     'uploaded_images': uploaded_images
                                 })
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
        