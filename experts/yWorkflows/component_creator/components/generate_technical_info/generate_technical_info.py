import os
import typing
from typing import Optional

import json
import yaml
from dotenv import load_dotenv
from fastapi import FastAPI
from pydantic import BaseModel
import openai

from core.workflows.abstract_component import AbstractComponent
from core.workflows.utils import get_cleaned_json, convert_to_snake_case


class GenerateTechnicalInfoInputDict(BaseModel):
    prompt: str


class GenerateTechnicalInfoOutputDict(BaseModel):
    component_name: str
    component_full_response: str
    component_internal_status: int


class GenerateTechnicalInfo(AbstractComponent):
    def __init__(self) -> None:
        super().__init__()
        with open(self.component_configuration_path(), "r", encoding="utf-8") as file:
            yaml_data = yaml.safe_load(file)
        self.openai_api_key: Optional[str] = os.environ.get(
            yaml_data["parameters"]["openai_api_key"]
        )
        self.master_prompt: str = yaml_data["parameters"]["master_prompt"]
        self.output = ""

    async def transform(
        self, args: GenerateTechnicalInfoInputDict, callbacks: typing.Any
    ) -> GenerateTechnicalInfoOutputDict:
        openai.api_key = self.openai_api_key
        await callbacks["send_message"]("I'm preparing a component solution design...")

        for _ in range(5):
            resp_yml = await get_cleaned_json(
                model="gpt-4",
                prompts=[
                    {"role": "system", "content": self.master_prompt},
                    {"role": "user", "content": args.prompt},
                ]
            )
            if "Error" in resp_yml:
                answer = await callbacks["retry_component"](
                    "We are having some issues with the OpenAI API. This happens often as they are working on scaling their systems. Do you want to retry?"
                )

                if answer == "retry":
                    continue
                else:
                    break
            try:
                ## callback de t'agrada el resultat? no? continue, si? break
                answer = await callbacks["edit_step"](
                    title="Component Stream",
                    description="Please modify the form below and submit the changes. It should preserve the structure of one step per line starting with - .",
                    step_dict={
                        "transformer_breakdown": "\n".join(
                            ["- " + item for item in resp_yml["transformer_breakdown"]]
                        )
                    },
                )

                new_list = [
                    line.strip().lstrip("- ")
                    for line in answer["transformer_breakdown"].split("\n")
                    if line.strip()
                ]
                resp_yml["transformer_breakdown"] = new_list
                response = json.dumps(resp_yml)
                break
            except (
                IndexError,
                TypeError,
                KeyError,
            ) as err:
                print(err)
                answer = await callbacks["retry_component"](
                    "We are having some issues with the OpenAI API. This happens often as they are working on scaling their systems. Do you want to retry?\n\n\t"
                )
                if answer == "retry":
                    continue
                else:
                    break

        resp_yml = json.loads(response)
        if resp_yml["transformer_breakdown"] == [] and resp_yml["type"] == "workflow":
            resp_yml["transformer_breakdown"] = [
                "Execute the transform of the AbstractWorkflow",
                "Prepare the Output BaseModel",
            ]
        if "parameters" not in resp_yml and resp_yml["type"] == "workflow":
            resp_yml["parameters"] = [""]
        out = GenerateTechnicalInfoOutputDict(
            component_name=resp_yml["name"],
            component_full_response=response,
            component_internal_status=200,
        )
        transformer_breakdown_string = "\n".join(
            "- " + (item if isinstance(item, str) else json.dumps(item))
            for item in resp_yml["transformer_breakdown"]
        )
        snake_component = convert_to_snake_case(resp_yml["name"])
        await callbacks["yeager_github_app"].create_file_commit_n_push(
            file_path=f"components/{snake_component}/README.md",
            commit_message=f"Adding content to the README.md of {snake_component}",
            file_content=f"""
# {resp_yml['name']}

{resp_yml['description']}

## Initial generation prompt
{args.prompt}

## Transformer breakdown
{transformer_breakdown_string}

## Parameters
{resp_yml['parameters']}

        """,
            discord_callbacks=callbacks,
        )
        return out


load_dotenv()
gen_tech_info_app = FastAPI()


@gen_tech_info_app.post("/transform/")
async def transform(
    args: GenerateTechnicalInfoInputDict,
) -> GenerateTechnicalInfoOutputDict:
    gen_tech_info = GenerateTechnicalInfo()
    return await gen_tech_info.transform(args, callbacks=None)
