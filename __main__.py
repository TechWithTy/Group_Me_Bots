from myapp import bots, posting, messages



# Add a bot to every group you have permissions in
filtered_bots = []


def post_message_to_groups(bots,message,interval):
    # Get all bots under a person
    
    posting.send_message_to_groups(bots, message)

    # Set post interval
 

    # Post message periodically
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
   

  


if __name__ == "__main__":
    main()



