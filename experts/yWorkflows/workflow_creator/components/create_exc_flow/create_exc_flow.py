import os
from typing import Optional
import typing

import yaml
from dotenv import load_dotenv
from fastapi import FastAPI
from pydantic import BaseModel
import openai

from core.workflows.abstract_component import AbstractComponent
from core.gen_ai_utils.llms.async_openai_calls import get_openai_completion


class CreateExcFlowIn(BaseModel):
    workflow_skeleton: str


class CreateExcFlowOut(BaseModel):
    component_internal_status: int


class CreateExcFlow(AbstractComponent):
    def __init__(self) -> None:
        super().__init__()
        with open(self.component_configuration_path(), "r", encoding="utf-8") as file:
            yaml_data = yaml.safe_load(file)
        self.openai_api_key: Optional[str] = os.environ.get(
            yaml_data["parameters"]["openai_api_key"]
        )
        self.master_prompt: str = yaml_data["parameters"]["master_prompt"]

    async def transform(
        self, args: CreateExcFlowIn, callbacks: typing.Any
    ) -> CreateExcFlowOut:
        await callbacks["send_message"](
            "I'm preparing the configuration files of this component..."
        )
        await callbacks["send_message"](
            "I'm preparing the documentation for the code that I've generated..."
        )

        openai.api_key = self.openai_api_key

        final_prompt = self.master_prompt.replace(
            "<technical_information>", args.workflow_skeleton
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
            out = CreateExcFlowOut(
                component_internal_status=500,
            )
            return out

        await callbacks["yeager_github_app"].update_file_commit_n_push(
            file_path="exc_flow.yml",
            commit_message="Adding info to exc_flow.yml of the workflow",
            file_content=response,
            discord_callbacks=callbacks,
        )

        out = CreateExcFlowOut(
            component_internal_status=200,
        )
        return out


load_dotenv()
create_exc_flow_app = FastAPI()


@create_exc_flow_app.post("/transform/")
async def transform(
    args: CreateExcFlowIn,
) -> CreateExcFlowOut:
    create_exc_flow = CreateExcFlow()
    return await create_exc_flow.transform(args, callbacks=None)
