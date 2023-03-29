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


class CreateSourceIn(BaseModel):
    component_name: str
    component_path: str
    configuration: str
    details: str


class CreateSourceOut(BaseModel):
    component_internal_status: int
    component_src: str


class CreateSource(AbstractComponent):
    def __init__(self) -> None:
        super().__init__()
        with open(self.component_configuration_path(), "r", encoding="utf-8") as file:
            yaml_data = yaml.safe_load(file)
        self.openai_api_key: Optional[str] = os.environ.get(
            yaml_data["parameters"]["openai_api_key"]
        )
        self.master_prompt_1: str = yaml_data["parameters"]["master_prompt_1"]
        self.master_prompt_2: str = yaml_data["parameters"]["master_prompt_2"]
        self.master_prompt_wf1: str = yaml_data["parameters"]["master_prompt_wf1"]
        self.master_prompt_wf2: str = yaml_data["parameters"]["master_prompt_wf2"]

    async def transform(
        self, args: CreateSourceIn, callbacks: typing.Any
    ) -> CreateSourceOut:
        await callbacks["send_message"](
            "I'm preparing the source code of this component..."
        )

        openai.api_key = self.openai_api_key

        final_prompt = f"""
        ## Component name
        {args.component_name}

        ## Details
        {args.details}
        """
        llm = "gpt-4"

        if yaml.safe_load(args.details)["type"] == "workflow":
            completion = await get_openai_completion(
                llm,
                [
                    {"role": "system", "content": self.master_prompt_wf1},
                    {"role": "system", "content": self.master_prompt_wf2},
                    {"role": "user", "content": final_prompt},
                ],
            )
        else:
            completion = await get_openai_completion(
                llm,
                [
                    {"role": "system", "content": self.master_prompt_1},
                    {"role": "system", "content": self.master_prompt_2},
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
            out = CreateSourceOut(
                component_internal_status=500,
                component_src="Error",
            )
            return out

        ## Modifies the source code of the component file
        snake_component = convert_to_snake_case(args.component_name)
        await callbacks["yeager_github_app"].update_file_commit_n_push(
            file_path=f"components/{snake_component}/{snake_component}.py",
            commit_message=f"Adding source code of the {args.component_name} component",
            file_content=response,
            discord_callbacks=callbacks,
        )

        ## Modifies the configuration file to add the input and output classes
        class_lines = [
            line
            for line in response.splitlines()
            if line.startswith("class ") and line.endswith("(BaseModel):")
        ]

        # github parse actual content of the file
        file_content = await callbacks["yeager_github_app"].get_file_content(
            file_path=f"components/{snake_component}/configuration.yml",
        )

        config_data = yaml.safe_load(file_content)
        config_data["input-class"] = class_lines[0].split("(")[0].split(" ")[1]
        config_data["output-class"] = class_lines[1].split("(")[0].split(" ")[1]

        await callbacks["yeager_github_app"].update_file_commit_n_push(
            file_path=f"components/{snake_component}/configuration.yml",
            commit_message=f"Adding IO to the configuration.yml of the {args.component_name} component",
            file_content=yaml.dump(config_data),
            discord_callbacks=callbacks,
        )

        out = CreateSourceOut(
            component_internal_status=200,
            component_src=response,
        )
        return out


load_dotenv()
create_source_app = FastAPI()


@create_source_app.post("/transform/")
async def transform(
    args: CreateSourceIn,
) -> CreateSourceOut:
    create_source = CreateSource()
    return await create_source.transform(args, callbacks=None)
