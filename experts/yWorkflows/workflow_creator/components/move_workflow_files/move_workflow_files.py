import typing

from fastapi import FastAPI
from pydantic import BaseModel
import yaml
from dotenv import load_dotenv

from core.workflows.abstract_component import AbstractComponent
from core.workflows.utils import convert_to_snake_case


class MoveWorkflowFilesIn(BaseModel):
    workflow_name: str


class MoveWorkflowFilesOut(BaseModel):
    component_internal_status: int


class MoveWorkflowFiles(AbstractComponent):
    def __init__(self) -> None:
        super().__init__()
        with open(self.component_configuration_path(), "r", encoding="utf-8") as file:
            yaml_data = yaml.safe_load(file)
        self.base_path: str = yaml_data["parameters"]["base_path"]

    async def transform(
        self, args: MoveWorkflowFilesIn, callbacks: typing.Any
    ) -> MoveWorkflowFilesOut:
        workflow_name = convert_to_snake_case(args.workflow_name)

        source_folder = f"components/{workflow_name}"
        destination_folder = ""

        await callbacks["yeager_github_app"].move_files_n_commit(
            source_folder=source_folder,
            destination_folder=destination_folder,
            branch="main",
        )

        return MoveWorkflowFilesOut(component_internal_status=200)


load_dotenv()
move_workflow_files_app = FastAPI()


@move_workflow_files_app.post("/transform/")
async def transform(
    args: MoveWorkflowFilesIn,
) -> MoveWorkflowFilesOut:
    move_wf_files = MoveWorkflowFiles()
    return await move_wf_files.transform(args, callbacks=None)
