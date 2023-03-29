import typing
from typing import Optional
from dotenv import load_dotenv
from fastapi import FastAPI
from pydantic import BaseModel

from core.workflows.abstract_workflow import AbstractWorkflow


class ComponentCreatorIn(BaseModel):
    prompt: str
    workflow_path: Optional[str] = None
    workflow_name: Optional[str] = None


class ComponentCreatorOut(BaseModel):
    new_component_name: str
    new_component_path: str
    new_component_creation_status: int


class ComponentCreator(AbstractWorkflow):
    def __init__(self) -> None:
        super().__init__()

    async def transform(
        self, args: ComponentCreatorIn, callbacks: typing.Any
    ) -> ComponentCreatorOut:
        results_dict = await super().transform(args=args, callbacks=callbacks)
        new_component_name = results_dict[0].component_name
        new_component_path = results_dict[1].component_path
        last_key = list(results_dict.keys())[-1]
        new_component_creation_status = results_dict[last_key].component_internal_status
        out = ComponentCreatorOut(
            new_component_name=new_component_name,
            new_component_path=new_component_path,
            new_component_creation_status=new_component_creation_status,
        )
        return out


load_dotenv()
component_creator_app = FastAPI()


@component_creator_app.post("/transform/")
async def transform(
    args: ComponentCreatorIn,
) -> ComponentCreatorOut:
    component_creator = ComponentCreator()
    return await component_creator.transform(args, callbacks=None)
