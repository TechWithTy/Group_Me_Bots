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
import schedule
import time
import datetime

from typing import Optional,List
scheduler = BackgroundScheduler()
load_dotenv()


PRODUCTION = True

PUSHBULLET_KEY = os.environ.get('PUSH_BULLET')
print(PUSHBULLET_KEY)

if not PUSHBULLET_KEY:
    TOKEN_OBJ = json.loads(keys.get_secret("PUSH_BULLET"))
  
    PUSHBULLET_KEY = TOKEN_OBJ.get('PUSH_BULLET')
    if  PUSHBULLET_KEY:
        print("PUSH BULLET Key Found")
    
restart_days = 3

pb = pushbullet.Pushbullet(PUSHBULLET_KEY)

# Add a bot to every group you have permissions in
filtered_bots = []
default_values = {}

default_interval = 2
default_times = ['8:37','12:15','5:55']

def schedule_posts(filtered_bots: list, post_times: Optional[List[str]] = None, post_interval: Optional[int] = None,  new_message: str = "Issa Bot", uploaded_images: Optional[str] = None):
    for post_time in post_times:
        print("Post Time Run" + " " + post_time)
        time_obj = datetime.datetime.strptime(post_time, "%H:%M").time()

        schedule.every().day.at(post_time).do(posting.send_message_to_groups, filtered_bots, new_message, uploaded_images)
        print(f"Post scheduled for {post_time}")
    
    if post_interval:
        print("Post Interval Run" , post_interval)
        scheduler.add_job(posting.send_message_to_groups, 'interval',
                        hours=post_interval, args=[filtered_bots, new_message,uploaded_images])
        return
   
        
    if post_times:
        schedule_posts(post_times, filtered_bots, new_message, uploaded_images)
    
       
        
def post_periodically(filtered_bots: list, post_times: Optional[List[str]] = None, post_interval: Optional[int] = None,  new_message: str = "Issa Bot", uploaded_images: Optional[str] = None) -> str:
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
    if post_times:

        for post_time in post_times:
            print("Post Time Run" + post_time )
            time_obj = datetime.datetime.strptime(post_time, "%H:%M").time()
            date_obj = datetime.date.today()  # get the current date

            combined_time = datetime.datetime.combine(date_obj, time_obj)
            print(f"Post scheduled for {post_time}")
            scheduler.add_job(posting.send_message_to_groups, 'cron', hour=combined_time.hour, minute=combined_time.minute,
                              args=[filtered_bots, new_message, uploaded_images])
        return
 
        
    if post_interval:
        print("Post Interval Run" , post_interval)
        scheduler.add_job(posting.send_message_to_groups, 'interval',
                        hours=post_interval, args=[filtered_bots, new_message,uploaded_images])
        return
        
    
def post_message_to_groups(bots):

    for message in messages.message_duration_data:
       duration = message.get('duration')
       message_text = message.get('message')
       times = message.get('times')
       
      
        
       print(message)
       
       if 'images' in message:
           
            uploaded_images = []
            
            for image in message['images']:
                uploaded_url = posting.upload_image_to_groupme(image)
                uploaded_images.append(uploaded_url)
           
            if (PRODUCTION):
                posting.send_message_to_groups(bots, message_text,uploaded_images)
        
            # Choose a random image
            if times:
                print('TIMES FOUND')
                t = threading.Thread(target=post_periodically,
                                    args=(),
                                    kwargs={
                                        'post_times': times,
                                        'filtered_bots': bots,
                                        'new_message': message_text,
                                        'uploaded_images': uploaded_images
                                    })
                t.start()

            if duration:
                t = threading.Thread(target=post_periodically,
                                    args=(),
                                    kwargs={
                                        'post_interval': duration,
                                        'filtered_bots': bots,
                                        'new_message': message_text,
                                        'uploaded_images': uploaded_images
                                    })
                t.start()

        
      
      
             
       else:
            print('Message Has No Images')
            
            
            if (PRODUCTION):
                posting.send_message_to_groups(bots, message_text)

            
            

            
            if duration:
                t = threading.Thread(target=post_periodically,
                            args=(),
                            kwargs={
                                'post_interval': duration,
                                'filtered_bots': bots,
                                'new_message': message_text,
                               
                            })
                t.start()
                
            if times:
                t = threading.Thread(target=post_periodically,
                                    args=(),
                                    kwargs={
                                        'post_times': times,
                                        'filtered_bots': bots,
                                        'new_message': message_text,
                                    })
                t.start()
            
    
  
    scheduler.start()
    scheduler.print_jobs()
        # Post message periodically
    while True:
        try:  
            schedule.run_pending()
            pass
        except (KeyboardInterrupt, SystemExit):
             scheduler.shutdown()
             pb.push_note("Group Me -", "App Crashed", str(SystemExit))
             break    
        
    
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
    pb.push_note("Group Me -", "Function Started Successfully",)
    # print(filtered_bots)
    post_message_to_groups(filtered_bots)
    


  




def main_wrapper():
    failure_count = 0
    while failure_count < 3:
        try:
            scheduler.remove_all_jobs()
            __main__()

            # reset failure count if successful
            failure_count = 0
        except Exception as e:
            # increment failure count
            failure_count += 1
            # send pushbullet notification on third failure
            if failure_count == 3:
                pb.push_note("Group Me -", "Error in main function and function tests failing", str(e))
                print(f"Error in main function: {e}")
            # wait for 5 minutes before trying again
            time.sleep(300)

def call_main_every_24h():
    main_wrapper()

    # Schedule the next call to main_wrapper() after 24 hours (24 hours * 60 minutes * 60 seconds)
    threading.Timer(24 * 60 * 60, call_main_every_24h).start()


if __name__ == "__main__":
    pb.push_note("Group Me -", "Function Started Successfully" )
    call_main_every_24h()

   
  