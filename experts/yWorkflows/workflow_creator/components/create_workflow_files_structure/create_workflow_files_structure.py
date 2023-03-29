import os
import typing

from fastapi import FastAPI
from pydantic import BaseModel
import yaml
from dotenv import load_dotenv

from core.workflows.abstract_component import AbstractComponent
from core.workflows.utils import convert_to_snake_case


class CreateWorkflowFilesStructureIn(BaseModel):
    workflow_name: str


class CreateWorkflowFilesStructureOut(BaseModel):
    component_internal_status: int
    workflow_path: str


class CreateWorkflowFilesStructure(AbstractComponent):
    def __init__(self) -> None:
        super().__init__()
        with open(self.component_configuration_path(), "r", encoding="utf-8") as file:
            yaml_data = yaml.safe_load(file)
        self.base_path: str = yaml_data["parameters"]["base_path"]

    async def transform(
        self, args: CreateWorkflowFilesStructureIn, callbacks: typing.Any
    ) -> CreateWorkflowFilesStructureOut:
        workflow_name = convert_to_snake_case(args.workflow_name)

        workflow_path = os.path.join(self.base_path, workflow_name)

        files_to_create = [
            ("__init__.py", ""),
            (f"{workflow_name}.py", ""),
            (f"t_{workflow_name}.py", ""),
            (f"{workflow_name}.md", ""),
            ("configuration.yml", ""),
            ("exc_flow.yml", ""),
            (".gitignore", ""),
            ("workflow_construction/last_step.yml", ""),
            ("Dockerfile", ""),
            ("requirements.txt", ""),
            ("LICENSE", """
 MIT License

Copyright (c) 2023 YeagerAI LLC

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.           
            """),
        ]

        await callbacks["yeager_github_app"].full_commit(
            commit_message=f"Initial add of {workflow_name} files...",
            files=files_to_create,
            discord_callbacks=callbacks,
        )

        return CreateWorkflowFilesStructureOut(
            component_internal_status=200, workflow_path=workflow_path
        )


load_dotenv()
create_workflow_files_structure_app = FastAPI()


@create_workflow_files_structure_app.post("/transform/")
async def transform(
    args: CreateWorkflowFilesStructureIn,
) -> CreateWorkflowFilesStructureOut:
    create_files = CreateWorkflowFilesStructure()
    return await create_files.transform(args, callbacks=None)
