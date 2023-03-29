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


class CreateSolutionSkeletonIn(BaseModel):
    prompt: str


class CreateSolutionSkeletonOut(BaseModel):
    workflow_name: str
    total_tokens_used: int
    workflow_skeleton: str
    component_internal_status: int


class CreateSolutionSkeleton(AbstractComponent):
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
        self, args: CreateSolutionSkeletonIn, callbacks: typing.Any
    ) -> CreateSolutionSkeletonOut:
        openai.api_key = self.openai_api_key

        await callbacks["send_message"]("I'm preparing a workflow solution sketch...")

        llm = "gpt-4"
        for i in range(5):
            completion = await get_openai_completion(
                llm,
                [
                    {"role": "system", "content": self.master_prompt},
                    {"role": "user", "content": args.prompt},
                ],
            )

            if "error" in completion:
                answer = await callbacks["retry_component"](
                    "We are having some issues with the OpenAI API. This happens often as they are working on scaling their systems. Do you want to retry?"
                )

                if answer == "retry":
                    continue
                else:
                    break
            try:
                response = (
                    completion["choices"][0]["message"]["content"]
                    .split("```yaml")[1]
                    .split("```")[0]
                )

                resp_yml = yaml.safe_load(response)
                name_desc_edited = await callbacks["edit_step"](
                    title="Workflow name and description",
                    description="Please modify the form below and submit the changes.",
                    step_dict={
                        "name": resp_yml["name"],
                        "description": resp_yml["description"],
                    },
                )

                resp_yml["name"] = name_desc_edited["name"]
                resp_yml["description"] = name_desc_edited["description"]

                # component by component
                await callbacks["send_message"](
                    "\n\nNow let's edit the components one by one when required...\n\n"
                )
                for component in resp_yml["components"]:
                    edited_component = await callbacks["edit_step"](
                        title="Workflow Component",
                        description="Please modify the form below and submit the changes.",
                        step_dict={
                            "name": component["name"],
                            "description": component["description"],
                        },
                    )
                    component["name"] = edited_component["name"]
                    component["description"] = edited_component["description"]

                break
            except (
                KeyError,
                IndexError,
                yaml.scanner.ScannerError,
                yaml.parser.ParserError,
            ) as err:
                print(err)
                answer = await callbacks["retry_component"](
                    "We are having some issues with the OpenAI API. This happens often as they are working on scaling their systems. Do you want to retry?\n\n\t"
                )
                if answer == "retry":
                    continue
                else:
                    break

        out = CreateSolutionSkeletonOut(
            workflow_name=resp_yml["name"],
            workflow_skeleton=response,
            total_tokens_used=completion["usage"]["total_tokens"],
            component_internal_status=200,
        )
        repo_id = callbacks["yeager_github_app"].repo_id
        discord_user_name = callbacks["yeager_github_app"].discord_user_name
        await callbacks["yeager_github_app"].create_new_repo(
            repo_name=f"yWorkflows-{resp_yml['name']}-by-{discord_user_name}-{repo_id}",
            workflow_name=resp_yml["name"],
            workflow_description=resp_yml["description"],
            discord_callbacks=callbacks,
        )

        ## add readme file?
        await callbacks["yeager_github_app"].create_file_commit_n_push(
            file_path="README.md",
            commit_message="Add README.md",
            file_content=f"""
# {resp_yml['name']}

{resp_yml['description']}
## Initial generation prompt
{args.prompt}

## Authors: 
- yWorkflows
- {discord_user_name}
        """,
            discord_callbacks=callbacks,
        )
        await callbacks["yeager_github_app"].invite_collaborators(
            discord_callbacks=callbacks,
        )
        return out


load_dotenv()
create_solution_skeleton_app = FastAPI()


@create_solution_skeleton_app.post("/transform/")
async def transform(
    args: CreateSolutionSkeletonIn,
) -> CreateSolutionSkeletonOut:
    create_solution_skeleton = CreateSolutionSkeleton()
    return await create_solution_skeleton.transform(args, callbacks=None)
