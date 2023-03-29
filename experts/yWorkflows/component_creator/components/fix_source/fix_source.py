import os
from typing import Optional

from fastapi import FastAPI
from pydantic import BaseModel

from langchain import OpenAI, ConversationChain
from langchain.prompts import PromptTemplate

import yaml

from dotenv import load_dotenv

from core.abstract_component import AbstractComponent


class FixSourceInputDict(BaseModel):
    prompt: str


class FixSourceOutputDict(BaseModel):
    component_name: str
    component_technical_description: str


class FixSource(AbstractComponent):
    def __init__(self) -> None:
        super().__init__()
        with open(self.component_configuration_path(), "r", encoding="utf-8") as file:
            yaml_data = yaml.safe_load(file)
        self.openai_api_key: Optional[str] = os.environ.get(
            yaml_data["parameters"]["openai_api_key"]
        )
        self.master_prompt: str = yaml_data["parameters"]["master_prompt"]
        self.llm = OpenAI(
            temperature=yaml_data["parameters"]["temperature"],
            openai_api_key=self.openai_api_key,
        )
        self.conversation = ConversationChain(llm=self.llm)

    def transform(self, args: FixSourceInputDict) -> FixSourceOutputDict:
        self.conversation.predict(input=self.master_prompt)
        processed_prompt = PromptTemplate(
            input_variables=["user_brief_description"],
            template="This is the short description: {user_brief_description}",
        )

        initial_description = args.prompt

        output = self.conversation.predict(
            input=processed_prompt.format(user_brief_description=initial_description)
        )
        print(output)
        name = output.split("name: ")[1].split("\n")[0]
        desc = output.split("description: ")[1]
        out = FixSourceOutputDict()
        out.component_name = name
        out.component_technical_description = desc
        return out


load_dotenv()
fix_source_app = FastAPI()


@fix_source_app.post("/transform/")
async def transform(
    args: FixSourceInputDict,
) -> FixSourceOutputDict:
    fix_source = FixSource()
    return fix_source.transform(args)
