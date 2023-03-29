import os

import time
import jwt
import requests

from github import GithubIntegration
from dotenv import load_dotenv

load_dotenv()


async def get_yeager_app_access_token() -> str:
    APP_ID = int(os.getenv("GITHUB_APP_ID"))

    private_key_pem_file = "yeagerai-bot.2023-03-26.private-key.pem"
    with open(private_key_pem_file, "r", encoding="utf-8") as file:
        private_key_pem_data = file.read()

    now = int(time.time())

    payload = {
        "iat": now,
        "exp": now + (10 * 60),
        "iss": APP_ID,
    }
    jwt_token = jwt.encode(payload, private_key_pem_data, algorithm="RS256")

    # Set up the API endpoint and headers
    api_base_url = "https://api.github.com"
    headers = {
        "Authorization": f"Bearer {jwt_token}",
        "Accept": "application/vnd.github+json",
    }

    # Get the list of installations
    installations_url = f"{api_base_url}/app/installations"
    response = requests.get(installations_url, headers=headers, timeout=10)

    INSTALLATION_ID = response.json()[-1]["id"]

    integration = GithubIntegration(APP_ID, private_key_pem_data)

    # Create an installation access token
    access_token = integration.get_access_token(INSTALLATION_ID).token
    return access_token
