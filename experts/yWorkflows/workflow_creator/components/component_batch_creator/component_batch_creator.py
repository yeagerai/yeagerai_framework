import typing
from typing import List

import yaml
from fastapi import FastAPI
from pydantic import BaseModel
from dotenv import load_dotenv

from core.workflows.abstract_component import AbstractComponent
from experts.yWorkflows.component_creator.component_creator import (
    ComponentCreator,
    ComponentCreatorIn,
)


class ComponentBatchCreatorIn(BaseModel):
    details: str
    workflow_path: str
    workflow_name: str


class ComponentBatchCreatorOut(BaseModel):
    generated_components: List[str]


class ComponentBatchCreator(AbstractComponent):
    def __init__(self) -> None:
        super().__init__()
        with open(self.component_configuration_path(), "r", encoding="utf-8") as file:
            yaml_data = yaml.safe_load(file)
        self.component_creator_workflow = yaml_data["parameters"][
            "component_creator_workflow"
        ]

    async def transform(
        self, args: ComponentBatchCreatorIn, callbacks: typing.Any
    ) -> ComponentBatchCreatorOut:
        component_list = [
            {
                "name": args.workflow_name,
                "description": "IOs - "
                + yaml.dump(yaml.safe_load(args.details)["IOs"]),
            }
        ]
        for el in yaml.safe_load(args.details)["components"]:
            component_list.append(el)
        print(component_list)
        workflow_path = args.workflow_path

        generated_components = []

        for component in component_list:
            # Instantiate the ComponentCreator and call its transform method
            creator = ComponentCreator()
            creator_in = ComponentCreatorIn(
                prompt=yaml.dump(component),
                workflow_path=workflow_path,
                workflow_name=args.workflow_name,
            )

            await callbacks["send_message"](
                f"I'm creating the component {component['name']}..."
            )

            generated_component = await creator.transform(creator_in, callbacks)
            generated_components.append(generated_component.new_component_name)

        return ComponentBatchCreatorOut(generated_components=generated_components)


load_dotenv()
component_batch_creator_app = FastAPI()


@component_batch_creator_app.post("/transform/")
async def transform(args: ComponentBatchCreatorIn) -> ComponentBatchCreatorOut:
    component_batch_creator = ComponentBatchCreator()
    return await component_batch_creator.transform(args, callbacks=None)
