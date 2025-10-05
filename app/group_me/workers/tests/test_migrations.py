from unittest.mock import patch
import json
import pytest
import requests
import sys
from pytest_mock import mocker
import response
from dotenv import load_dotenv
import os
import json

#?⚠ File Under  Construction���

# Load environment variables from .env file
load_dotenv()

ACCESS_TOKEN = os.environ.get('ZB_PROMO')
sys.path.append('/workspace/Group_Me_Bots/myapp')
# in this order

#!Important
# fmt: off
from migration import *
# fmt: on


def test_migrate_users():
    # Set up mock data for the test
    original_group_id = '91209188'
    target_group_id = '87323365'
    

    members = [{'nickname': 'Alice', 'user_id': '123'},
               {'nickname': 'Bob', 'user_id': '456'}]

    # Set up mock responses for the requests library
    mock_responses = [
        # First call to get members from original group
        {'status_code': 200, 'text': json.dumps(
            {'response': {'members': members}})},
        # Second call to add members to target group
        {'status_code': 200, 'text': '{"meta": {"code": 200}}'}
    ]

    # Mock the requests.get and requests.post methods to return the mock responses
    with patch('requests.get') as mock_get, patch('requests.post') as mock_post:
        mock_get.return_value = type('MockResponse', (), mock_responses[0])
        mock_post.return_value = type('MockResponse', (), mock_responses[1])

        # Call the function and check the return value
        migrate_users(original_group_id, target_group_id, ACCESS_TOKEN)
        assert mock_get.call_count == 1
        assert mock_post.call_count == len(members)
