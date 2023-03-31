import json
from core.gen_ai_utils.llms.async_openai_calls import get_openai_completion

async def get_cleaned_json(model:str, prompts:list[dict])->dict:
    completion = await get_openai_completion(
            model,prompts
        )

    raw_json = completion["choices"][0]["message"]["content"]

    # Remove ```json and ``` if present
    if raw_json.startswith("```json"):
        raw_json = raw_json[len("```json"):]
    if raw_json.startswith("```"):
        raw_json = raw_json[len("```"):]
    if raw_json.endswith("```"):
        raw_json = raw_json[:-len("```")]

    try:
        cleaned_json = json.loads(raw_json)
    except json.JSONDecodeError as err:
        print(f"Invalid JSON received: {err}")
        return {"Error": "Invalid JSON received"}

    return cleaned_json

def convert_to_snake_case(s: str) -> str:
    new_s = ""
    for i, c in enumerate(s):
        if c.isupper():
            if i > 0 and s[i - 1].islower():
                new_s += "_"
            new_s += c.lower()
        else:
            new_s += c
    return new_s
