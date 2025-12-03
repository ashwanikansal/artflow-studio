import requests
from typing import Any, Dict, Optional
import os

META_API_VERSION = os.getenv("META_API_VERSION", "v19.0")
ACCESS_TOKEN = os.getenv("INSTAGRAM_ACCESS_TOKEN")  # to be added later
USER_ID = os.getenv("INSTAGRAM_USER_ID")            # your Instagram Business ID

BASE_URL = f"https://graph.facebook.com/{META_API_VERSION}"


class InstagramAPIError(Exception):
    pass


def _check_token():
    if not ACCESS_TOKEN or not USER_ID:
        raise InstagramAPIError(
            "Instagram ACCESS_TOKEN or USER_ID missing. "
            "Please set them in your .env file."
        )


def ig_get(path: str, params: Optional[Dict[str, Any]] = None) -> Any:
    """
    Wrapper for GET requests to the Instagram Graph API.
    Automatically injects access token.
    """
    _check_token()

    if params is None:
        params = {}

    params["access_token"] = ACCESS_TOKEN

    url = f"{BASE_URL}/{path}"

    resp = requests.get(url, params=params)

    if resp.status_code != 200:
        raise InstagramAPIError(f"Error calling IG API: {resp.text}")

    return resp.json()
