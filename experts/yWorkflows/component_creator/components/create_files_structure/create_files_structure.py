import os
import typing
from typing import Optional

from fastapi import FastAPI
from pydantic import BaseModel
import yaml
from dotenv import load_dotenv

from core.workflows.abstract_component import AbstractComponent
from core.workflows.utils import convert_to_snake_case


class CreateFilesStructureInputDict(BaseModel):
    component_name: str
    workflow_name: Optional[str] = None


class CreateFilesStructureOutputDict(BaseModel):
    component_internal_status: int
    component_path: str


class CreateFilesStructure(AbstractComponent):
    def __init__(self) -> None:
        super().__init__()
        with open(self.component_configuration_path(), "r", encoding="utf-8") as file:
            yaml_data = yaml.safe_load(file)
        self.base_path: str = yaml_data["parameters"]["base_path"]

    async def transform(
        self, args: CreateFilesStructureInputDict, callbacks: typing.Any
    ) -> CreateFilesStructureOutputDict:
        component_name = convert_to_snake_case(args.component_name)

        if args.workflow_name:
            workflow_name = convert_to_snake_case(args.workflow_name)
            component_path = os.path.join(
                self.base_path, workflow_name, "components", component_name
            )
        else:
            component_path = os.path.join(self.base_path, component_name)

        files_to_create = [
            ("components/__init__.py", ""),
            (f"components/{component_name}/__init__.py", ""),
            (f"components/{component_name}/{component_name}.py", ""),
            (f"components/{component_name}/t_{component_name}.py", ""),
            (f"components/{component_name}/README.md", ""),
            (f"components/{component_name}/configuration.yml", ""),
            (f"components/{component_name}/Dockerfile", ""),
            (f"components/{component_name}/requirements.txt", ""),
        ]

        await callbacks["yeager_github_app"].full_commit(
            commit_message="Initial add of many files...",
            files=files_to_create,
            discord_callbacks=callbacks,
        )

        return CreateFilesStructureOutputDict(
            component_internal_status=200, component_path=component_path
        )


load_dotenv()
create_files_structure_app = FastAPI()


@create_files_structure_app.post("/transform/")
async def transform(
    args: CreateFilesStructureInputDict,
) -> CreateFilesStructureOutputDict:
    create_files = CreateFilesStructure()
    return await create_files.transform(args, callbacks=None)
