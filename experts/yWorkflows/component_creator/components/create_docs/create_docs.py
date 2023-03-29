import os
import typing
from typing import Optional

import yaml
from dotenv import load_dotenv
from fastapi import FastAPI
from pydantic import BaseModel
import openai

from core.workflows.abstract_component import AbstractComponent
from core.workflows.utils import convert_to_snake_case
from core.gen_ai_utils.llms.async_openai_calls import get_openai_completion


class CreateDocsIn(BaseModel):
    component_name: str
    component_src: str
    component_path: str


class CreateDocsOut(BaseModel):
    component_internal_status: int


class CreateDocs(AbstractComponent):
    def __init__(self) -> None:
        super().__init__()
        with open(self.component_configuration_path(), "r", encoding="utf-8") as file:
            yaml_data = yaml.safe_load(file)
        self.openai_api_key: Optional[str] = os.environ.get(
            yaml_data["parameters"]["openai_api_key"]
        )
        self.master_prompt: str = yaml_data["parameters"]["master_prompt"]

    async def transform(
        self, args: CreateDocsIn, callbacks: typing.Any
    ) -> CreateDocsOut:
        await callbacks["send_message"](
            "I'm preparing the documentation for the code that I've generated..."
        )

        openai.api_key = self.openai_api_key

        final_prompt = self.master_prompt.replace(
            "<source_code_placeholder>", args.component_src
        )

        llm = "gpt-4"

        completion = await get_openai_completion(
            llm,
            [
                {"role": "user", "content": final_prompt},
            ],
        )

        try:
            response = (
                completion["choices"][0]["message"]["content"]
                .split("```")[1]
                .split("```")[0]
            )
        except IndexError:
            out = CreateDocsOut(
                component_internal_status=500,
            )
            return out

        snake_component = args.component_path.split("/")[
            -1
        ]  # hotfix why component_name is empty?
        print(snake_component)
        await callbacks["yeager_github_app"].update_file_commit_n_push(
            file_path=f"components/{snake_component}/README.md",
            commit_message=f"Adding info to README.md of the {snake_component} component",
            file_content=response,
            discord_callbacks=callbacks,
        )

        out = CreateDocsOut(
            component_internal_status=200,
        )
        return out


load_dotenv()
create_docs_app = FastAPI()


@create_docs_app.post("/transform/")
async def transform(
    args: CreateDocsIn,
) -> CreateDocsOut:
    create_docs = CreateDocs()
    return await create_docs.transform(args, callbacks=None)
