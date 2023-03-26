import requests
import pytest
import sys
from pytest_mock import mocker
from dotenv import load_dotenv
import os
import json
from ..app import posting

# Load environment variables from .env file
load_dotenv()

ACCESS_TOKEN = os.environ.get('ZB_PROMO')



# 
# # fmt: off
# from posting import *
# # fmt: on


@pytest.fixture
def mock_response():
    class MockResponse:
        def __init__(self, status_code):
            self.status_code = status_code

        def json(self):
            return {}

    return MockResponse


def test_send_message_to_groups(mocker, mock_response):
   
    # Set up mock data for the test
    new_bots = [{'bot_id': '123', 'group_id': '456'},
                {'bot_id': '789', 'group_id': '012'}]
    message = 'Test message'

    # Mock the requests.post method to return a 202 status code
    mocker.patch('requests.post', return_value=mock_response(202))

    # Call the function and check the return value
    result = send_message_to_groups(new_bots, message)
    assert result == "Message sent to all groups successfully."

    # Check that the requests.post method was called twice (once for each bot)
    assert requests.post.call_count == 2

    # Check that the requests.post method was called with the correct arguments
    requests.post.assert_any_call(
        'https://api.groupme.com/v3/bots/post',
        headers={'Content-Type': 'application/json',
                 'X-Access-Token': ACCESS_TOKEN},
        data='{"text": "Test message", "attachments": [], "bot_id": "123"}'
    )
    requests.post.assert_any_call(
        'https://api.groupme.com/v3/bots/post',
        headers={'Content-Type': 'application/json',
                 'X-Access-Token': ACCESS_TOKEN},
        data='{"text": "Test message", "attachments": [], "bot_id": "789"}'
    )

    # Mock the requests.post method to return a 500 status code
    mocker.patch('requests.post', return_value=mock_response(500))

    # Call the function and check that it raises an error
    with pytest.raises(Exception):
        send_message_to_groups(new_bots, message)


#✅
#TODO
# @pytest.fixture
# def mock_send_message_to_groups(mocker):
#     return mocker.patch('send_message_to_groups')


# def test_post_periodically(mocker):
#     # Set up mock data for the test
#     post_interval = 1
#     filtered_bots = [{'bot_id': '123', 'group_id': '456'},
#                      {'bot_id': '789', 'group_id': '012'}]
#     new_message = 'Test message'

#     # Mock the time.sleep method to return immediately
#     mocker.patch('time.sleep', return_value=None)

#     # Mock the send_message_to_groups function to do nothing
#     mocker.patch('send_message_to_groups', return_value=None)

#     # Call the function and wait for a short period of time
#     post_periodically(post_interval, filtered_bots, new_message)
#     time.sleep(0.1)

#     # Check that the send_message_to_groups function was called once with the correct arguments
#     send_message_to_groups.assert_called_once_with(filtered_bots, new_message)

#     # Reset the mock to its initial state
#     send_message_to_groups.reset_mock()

#     # Call the function again and wait for a longer period of time
#     post_periodically(post_interval, filtered_bots, new_message)
#     time.sleep(1)

#     # Check that the send_message_to_groups function was called twice (once for each bot) with the correct arguments
#     send_message_to_groups.assert_has_calls([
#         call([{'bot_id': '123', 'group_id': '456'}], new_message),
#         call([{'bot_id': '789', 'group_id': '012'}], new_message)
#     ])
