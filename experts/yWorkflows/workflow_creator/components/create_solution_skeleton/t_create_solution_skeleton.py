import pytest
from engines.yeager_base.component_creator.components.generate_technical_info.generate_technical_info import (
    GenerateTechnicalInfo,
    GenerateTechnicalInfoInputDict,
    GenerateTechnicalInfoOutputDict,
)


def component() -> GenerateTechnicalInfo:
    return GenerateTechnicalInfo()


def input_dict(prompt: str) -> GenerateTechnicalInfoInputDict:
    return GenerateTechnicalInfoInputDict(prompt=prompt)


@pytest.mark.parametrize(
    "input_prompt",
    [
        "get every email and send it to google sheet",
        """a Component that performs sentiment analysis on a given text using 
        the Google Cloud Natural Language API""",
        "A component that downloads all emails from google",
        """A component that listens to twitter and sends a slack 
        message every time it detects a new message""",
        "A component that lists all the required tests of a component",
    ],
)
def test_transform_out_type(input_prompt: str) -> None:
    in_prompt = input_dict(input_prompt)
    output = component().transform(in_prompt)
    assert isinstance(output, GenerateTechnicalInfoOutputDict)


@pytest.mark.parametrize(
    "input_prompt",
    [
        "get every email and send it to google sheet",
        """a Component that performs sentiment analysis on a given text using 
        the Google Cloud Natural Language API""",
        "A component that downloads all emails from google",
        """A component that listens to twitter and sends a slack 
        message every time it detects a new message""",
        "A component that lists all the required tests of a component",
    ],
)
def test_desc_len(input_prompt: str) -> None:
    in_prompt = input_dict(input_prompt)
    output = component().transform(in_prompt)
    assert len(output.component_technical_description) >= 3 * len(input_prompt)
