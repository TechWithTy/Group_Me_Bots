import requests
from typing import Optional


def get_group_info(group_id: str) -> Optional[dict]:
    """
    Retrieves the name and share URL of a GroupMe group given its ID.

    Args:
    group_id (str): The ID of the GroupMe group.
    ACCESS_TOKEN (str): Your GroupMe API access token.

    Returns:
    A dictionary containing the group name and share URL if successful, None otherwise.
    """
    url = f"https://api.groupme.com/v3/groups/{group_id}?token={ACCESS_TOKEN}"
    response = requests.get(url).json()

    if response["meta"]["code"] == 200:
        group_name = response["response"]["name"]
        group_url = response["response"]["share_url"]
        return {"group_name": group_name, "group_url": group_url}
    else:
        print("Failed to retrieve group information.")
        return None
