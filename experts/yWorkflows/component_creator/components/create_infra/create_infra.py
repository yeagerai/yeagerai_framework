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


class CreateInfraIn(BaseModel):
    component_name: str
    component_path: str
    component_src: str


class CreateInfraOut(BaseModel):
    component_internal_status: int


class CreateInfra(AbstractComponent):
    def __init__(self) -> None:
        super().__init__()
        with open(self.component_configuration_path(), "r", encoding="utf-8") as file:
            yaml_data = yaml.safe_load(file)
        self.openai_api_key: Optional[str] = os.environ.get(
            yaml_data["parameters"]["openai_api_key"]
        )
        self.master_prompt: str = yaml_data["parameters"]["master_prompt"]

    async def transform(
        self, args: CreateInfraIn, callbacks: typing.Any
    ) -> CreateInfraOut:
        await callbacks["send_message"]("I'm preparing the deployment files...")

        openai.api_key = self.openai_api_key

        final_prompt = self.master_prompt.replace(
            "<source_code_placeholder>", args.component_src
        )

        llm = "gpt-4"

        completion = await get_openai_completion(
            llm,
            [
                {"role": "user", "content": final_prompt},
            ],
        )

        try:
            response = (
                completion["choices"][0]["message"]["content"]
                .split("```")[1]
                .split("```")[0]
            )
        except IndexError:
            out = CreateInfraOut(
                component_internal_status=500,
            )
            return out

        snake_component = convert_to_snake_case(args.component_name)

        await callbacks["yeager_github_app"].update_file_commit_n_push(
            file_path=f"components/{snake_component}/requirements.txt",
            commit_message="Adding requirements.txt content",
            file_content=response,
            discord_callbacks=callbacks,
        )

        dockerfile_content = f"""
# Start with a base Python image
FROM python:3.9-slim-buster

# Set the working directory to /app
WORKDIR /app

# Copy the requirements.txt file into the container
COPY ./{args.component_path}/requirements.txt .

# Install the required Python packages
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install uvicorn
# Copy the Python code into the container
COPY ./{args.component_path} .

# replace it with installable yeager python library
COPY ./core ./core

# Expose port 80 for the FastAPI application
EXPOSE 5000

# Start the FastAPI application when the container is run
CMD ["uvicorn", "{convert_to_snake_case(args.component_name)}:{convert_to_snake_case(args.component_name)}_app", "--host", "0.0.0.0", "--port", "5000"]

        """
        await callbacks["yeager_github_app"].update_file_commit_n_push(
            file_path=f"components/{snake_component}/Dockerfile",
            commit_message="Adding Dockerfile content",
            file_content=dockerfile_content,
            discord_callbacks=callbacks,
        )

        out = CreateInfraOut(
            component_internal_status=200,
        )
        return out


load_dotenv()
create_infra_app = FastAPI()


@create_infra_app.post("/transform/")
async def transform(
    args: CreateInfraIn,
) -> CreateInfraOut:
    create_infra = CreateInfra()
    return await create_infra.transform(args, callbacks=None)
