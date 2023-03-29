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


class CreateTestsIn(BaseModel):
    component_name: str
    component_path: str
    component_src: str


class CreateTestsOut(BaseModel):
    component_internal_status: int


class CreateTests(AbstractComponent):
    def __init__(self) -> None:
        super().__init__()
        with open(self.component_configuration_path(), "r", encoding="utf-8") as file:
            yaml_data = yaml.safe_load(file)
        self.openai_api_key: Optional[str] = os.environ.get(
            yaml_data["parameters"]["openai_api_key"]
        )
        self.master_prompt: str = yaml_data["parameters"]["master_prompt"]

    async def transform(
        self, args: CreateTestsIn, callbacks: typing.Any
    ) -> CreateTestsOut:
        await callbacks["send_message"](
            "I'm preparing the unit tests of this component..."
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
                .split("```python")[1]
                .split("```")[0]
            )
        except IndexError:
            out = CreateTestsOut(
                component_internal_status=500,
            )
            return out

        snake_component = convert_to_snake_case(args.component_name)
        await callbacks["yeager_github_app"].update_file_commit_n_push(
            file_path=f"components/{snake_component}/t_{snake_component}.py",
            commit_message=f"Adding source code of the {args.component_name} component",
            file_content=response,
            discord_callbacks=callbacks,
        )

        out = CreateTestsOut(
            component_internal_status=200,
        )
        return out


load_dotenv()
create_tests_app = FastAPI()


@create_tests_app.post("/transform/")
async def transform(
    args: CreateTestsIn,
) -> CreateTestsOut:
    create_tests = CreateTests()
    return await create_tests.transform(args, callbacks=None)
