
import requests
import pytest
import sys

sys.path.append('/workspace/Group_Me_Bots/myapp')
# in this order

#!Important
# fmt: off
from bots import *
# fmt: on

# Import the function to be tested


def test_add_bots_to_groups():
    # Call the function
    test_bots = None
    test_bots = add_bots_to_groups()

    # Check that the function returns a list
    assert isinstance(test_bots, list)

    # Check that the list contains at least one bot object
    assert isinstance(test_bots, list) and len(test_bots) >= 0

    # Check that each bot object has a 'bot_id' and a 'group_id'
    for bot in test_bots:
        assert 'bot_id' in bot
        assert 'group_id' in bot

    # Check that each bot object has a valid bot ID (a string of numbers)
    for bot in test_bots:
        assert isinstance(bot['bot_id'], str)
        try:
            assert bot['bot_id'].isdigit()
        except:
            print(bot['bot_id'])


# ✅


def test_get_bots():
    # Define a mock response
    mock_response = {
        "response": [
            {"bot_id": "123", "group_id": "456", "name": "Bot1"},
            {"bot_id": "789", "group_id": "101", "name": "Bot2"}
        ]
    }

    # Mock the requests.get method to return the mock response
    def mock_get(*args, **kwargs):
        class MockResponse:
            def __init__(self, json_data, status_code):
                self.json_data = json_data
                self.status_code = status_code

            def json(self):
                return self.json_data

        return MockResponse(mock_response, 200)

    requests.get = mock_get

    # Call the get_bots function and check the response
    response = get_bots()

    assert response == [{'bot_id': '123', 'group_id': '456', 'bot_name': 'Bot1'},
                        {'bot_id': '789', 'group_id': '101', 'bot_name': 'Bot2'}]
    assert len(response) > 1
    assert response[0]['bot_id'].isdigit()
    assert response[1]['bot_name'] == 'Bot2'


# ✅


def test_filter_bots():
    # Create a list of bot objects to use for testing
    bots = [{'bot_id': '1', 'group_id': '100', 'bot_name': 'ZoBot'},
            {'bot_id': '2', 'group_id': '101', 'bot_name': 'GortBot'},
            {'bot_id': '3', 'group_id': '100', 'bot_name': 'ZoBot'},
            {'bot_id': '4', 'group_id': '102', 'bot_name': 'GortZoBot'},
            {'bot_id': '5', 'group_id': '103', 'bot_name': 'Zobot'},
            {'bot_id': '6', 'group_id': '104', 'bot_name': 'Zo'}]

    # Call the function and get the filtered bots
    filtered_bots = filter_bots(bots)

    # Check that the function returns a list
    assert isinstance(filtered_bots, list)

    # Check that the list contains only unique bot objects
    bot_ids = [bot['bot_id'] for bot in filtered_bots]
    assert len(bot_ids) == len(set(bot_ids))



#✅
