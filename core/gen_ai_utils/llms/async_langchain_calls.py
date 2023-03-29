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
    async with aiohttp.ClientSession() as session:
        for i in range(5):
            try:
                completion = await fetch_openai_completion(session, model, messages)
                return completion
            except TimeoutError as err:
                print(f"Timeout error: {err}")
                continue
    return completion
