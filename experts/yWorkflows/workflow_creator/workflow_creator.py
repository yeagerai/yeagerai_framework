import typing

from dotenv import load_dotenv
from fastapi import FastAPI
from pydantic import BaseModel

from core.workflows.abstract_workflow import AbstractWorkflow


class WorkflowCreatorIn(BaseModel):
    prompt: str


class WorkflowCreatorOut(BaseModel):
    new_workflow_creation_status: int


class WorkflowCreator(AbstractWorkflow):
    def __init__(self) -> None:
        super().__init__()

    async def transform(
        self, args: WorkflowCreatorIn, callbacks: typing.Any
    ) -> WorkflowCreatorOut:
        if callbacks:
            await callbacks["send_message"](
                f"""I'm creating the requested workflow, it may take a while... 
The initial prompt is: 

**{args.prompt}**\n\n

"""
            )

        results_dict = await super().transform(args=args, callbacks=callbacks)

        await callbacks["send_message"](
            "The creation of the workflow is complete!!! Congratulations!"
        )

        last_key = list(results_dict.keys())[-1]
        new_component_creation_status = results_dict[last_key].component_internal_status
        out = WorkflowCreatorOut(
            new_component_creation_status=new_component_creation_status,
        )

        return out

    def _sum_tokens_used(self, d: dict) -> int:
        """
        Recursively searches for all keys and subkeys of a dictionary `d` and sums the
        values associated with keys like "tokens_used".
        """
        total = 0
        for k, v in d.items():
            if isinstance(v, dict):
                total += self._sum_tokens_used(v)
            elif k == "tokens_used":
                total += v
        return total


load_dotenv()
workflow_creator_app = FastAPI()


@workflow_creator_app.post("/transform/")
async def transform(
    args: WorkflowCreatorIn,
) -> WorkflowCreatorOut:
    workflow_creator = WorkflowCreator()
    return await workflow_creator.transform(args, callbacks=None)
