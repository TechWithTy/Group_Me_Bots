Group Me Bots
This is a Python application that allows you to add a bot to every group you have permission to and post messages periodically.

Installation
Clone the repository

Install dependencies


pip install -r requirements.txt
Create a .env file with your Pushbullet API key:
makefile

PUSH_BULLET=YOUR_API_KEY
and create a variable for your group me api key importing and  assigning it wherever (ACCESS_TOKEN = ) is
Usage
Import the required modules
python

from myapp import bots, posting, messages
import pushbullet
import traceback
import time
from dotenv import load_dotenv
import os
import json
from pushbullet import Pushbullet

load_dotenv()

PUSHBULLET_KEY = os.environ.get('PUSH_BULLET')

restart_days = 3

pb = pushbullet.Pushbullet(PUSHBULLET_KEY)

# Add a bot to every group you have permissions in
filtered_bots = []
Define the post_message_to_groups() and main() functions
python

def post_message_to_groups(bots,message,interval):
    # Get all bots under a person
    posting.send_message_to_groups(bots, message)

    # Set post interval
    posting.post_periodically(interval, filtered_bots, message)
    
    
def main():
    # Add bots to groups
    add_bots_to_groups = bots.add_bots_to_groups
    add_bots_to_groups()

    # Get all bots under a person
    Bots = bots.get_bots()

    # Filter the Duplicate bots to avoid multiple postings
    filtered_bots = bots.filter_bots(Bots)

    post_message_to_groups(filtered_bots,messages.test_text,2)
Run the application using a try-catch block that sends a Pushbullet notification of the error if the main() function fails three times:
python

if __name__ == "__main__":
    failure_count = 0
    while True:
        try:
            main()
            # reset failure count if successful
            failure_count = 0
        except Exception as e:
            # increment failure count
            failure_count += 1
            # send pushbullet notification on third failure
            if failure_count == 3:
                pb.push_note("Group Me -","Error in main function ", str(e))
                print(f"Error in main function: {e}")
                failure_count = 0
            # wait for 5 minutes before trying again
            time.sleep(300)
        # Schedule the program to run every 3 days at 2am EST
        schedule.every(restart_days).days.at("02:00").do(main)
        # Check if any scheduled tasks are pending and run them
        schedule.run_pending()
        # wait for 1 minute before checking again
        time.sleep(60)
License
This project is licensed under the MIT License - see the LICENSE.md file for details.