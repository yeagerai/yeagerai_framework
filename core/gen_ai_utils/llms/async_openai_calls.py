import os

import aiohttp


async def fetch_openai_completion(
    session: aiohttp.ClientSession, model: str, messages: list[dict]
) -> dict:
    url = "https://api.openai.com/v1/chat/completions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {os.environ.get('OPENAI_API_KEY')}",
    }
    data = {"model": model, "messages": messages}
    async with session.post(url, headers=headers, json=data) as resp:
        return await resp.json()


async def get_openai_completion(model: str, messages: list[dict]) -> dict:
    for i in range(5):
        try:
            async with aiohttp.ClientSession() as session:
                completion = await fetch_openai_completion(session, model, messages)
                try:
                    completion["choices"][0]["message"]["content"]
                except KeyError:
                    print(completion)
                    continue
                return completion
        except TimeoutError as err:
            print(f"Timeout error: {err}")
            continue
    return completion


async def get_openai_completion_mocked(model: str, messages: list[dict]) -> dict:
    completion = {
        "id": "chatcmpl-6wa4lAtNflOkrc3L6H1zvwxD9gu4H",
        "object": "chat.completion",
        "created": 1679419719,
        "model": "gpt-4-0314",
        "usage": {"prompt_tokens": 899, "completion_tokens": 374, "total_tokens": 1273},
        "choices": [
            {
                "message": {
                    "role": "assistant",
                    "content": "```yaml\nname: GmailToDiscord\ndescription: >\n  A Yeager Workflow that downloads all emails from a Gmail account and sends each email as a message in a specified Discord channel. The workflow consists of three primary components: 1) authenticating and retrieving emails from the Gmail account, 2) processing and formatting the retrieved emails into a readable format, and 3) posting the formatted messages to the desired Discord channel. OAuth 2.0 is used for Gmail API authentication, while the Discord API is utilized for sending messages to the channel.\n\ncomponents:\n  - name: GmailAuthenticator\n    description: >\n      Authenticate using OAuth2 to access the Gmail API. Receive the Gmail API credentials and scope as input\n      parameters. Return the authenticated Gmail API client.\n\n  - name: EmailRetriever\n    description: >\n      Retrieve all emails from the Gmail account. Take the authenticated Gmail API client as input. Use the\n      Gmail API functions to fetch all email message objects. Return a list of emails containing email sender,\n      subject, and content (text and/or HTML).\n\n  - name: DiscordMessenger\n    description: >\n      Format and send the retrieved emails as messages to a specific Discord channel. Take the list of emails and\n      a Discord webhook URL as input parameters. For each email, format the message content by combining the\n      sender, subject, and content. Use the Discord API and webhook to send these messages to the specified\n      channel.\n\nadj_matrix:\n  - [0, 1, 0]\n  - [0, 0, 1]\n  - [0, 0, 0]\n\nmapper:\n  EmailRetriever|gmail_api_client: GmailAuthenticator|gmail_api_client\n  DiscordMessenger|emails: EmailRetriever|emails\n```\n",
                },
                "finish_reason": "stop",
                "index": 0,
            }
        ],
    }
    completion_error = {
        "error": {
            "code": 400,
            "message": "Mocked error, switch function to get_openai_completion to use the real API",
        }
    }
    return completion
