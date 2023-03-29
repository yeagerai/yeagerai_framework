import os
import typing
from typing import Optional

import yaml
from dotenv import load_dotenv
from fastapi import FastAPI
from pydantic import BaseModel
from core.workflows.abstract_component import AbstractComponent
from core.workflows.utils import convert_to_snake_case


class CreateConfigurationIn(BaseModel):
    component_name: str
    component_path: str
    details: str


class CreateConfigurationOut(BaseModel):
    component_internal_status: int


class CreateConfiguration(AbstractComponent):
    def __init__(self) -> None:
        super().__init__()
        with open(self.component_configuration_path(), "r", encoding="utf-8") as file:
            yaml_data = yaml.safe_load(file)
        self.openai_api_key: Optional[str] = os.environ.get(
            yaml_data["parameters"]["openai_api_key"]
        )
        self.master_prompt_1: str = yaml_data["parameters"]["master_prompt_1"]

    async def transform(
        self, args: CreateConfigurationIn, callbacks: typing.Any
    ) -> CreateConfigurationOut:
        await callbacks["send_message"](
            "I'm preparing the configuration files of this component..."
        )

        tech_info_yaml = yaml.safe_load(args.details)

        # the new_yaml just preserves the keys name, description and parameters of the original yaml, and for the parameters it only saves the name
        new_yaml = {
            "name": tech_info_yaml["name"],
            "description": tech_info_yaml["description"],
            "parameters": {},
        }

        for parameter in tech_info_yaml["parameters"]:
            new_yaml["parameters"][parameter["name"]] = parameter["default_value"]

        snake_component = convert_to_snake_case(args.component_name)

        await callbacks["yeager_github_app"].update_file_commit_n_push(
            file_path=f"components/{snake_component}/configuration.yml",
            commit_message=f"Adding parameters to configuration.yml of {snake_component}",
            file_content=yaml.dump(new_yaml),
            discord_callbacks=callbacks,
        )

        out = CreateConfigurationOut(component_internal_status=200)
        return out


load_dotenv()
create_configuration_app = FastAPI()


@create_configuration_app.post("/transform/")
async def transform(
    args: CreateConfigurationIn,
) -> CreateConfigurationOut:
    create_source = CreateConfiguration()
    return await create_source.transform(args, callbacks=None)
