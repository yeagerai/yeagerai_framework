import os

import yaml
import pytest

from engines.yeager_base.component_creator.components.create_files_structure.create_files_structure import (
    CreateFilesStructure,
    CreateFilesStructureInputDict,
)
from core.workflows.utils import convert_to_snake_case


def component() -> CreateFilesStructure:
    return CreateFilesStructure()


def input_dict(
    component_name: str, workflow_name: str
) -> CreateFilesStructureInputDict:
    return CreateFilesStructureInputDict(
        component_name=component_name, workflow_name=workflow_name
    )


@pytest.mark.parametrize(
    "component_name, workflow_name",
    [
        ("GmailToGSheet", None),
        ("GmailDownloader", None),
        ("CreateFilesStructure", "CreateFilesStructureWorkflow"),
        ("FixSource", "CreateFilesStructureWorkflow"),
        ("HelloWorld", "HelloWorldWorkflow"),
    ],
)
def test_files_creation(component_name: str, workflow_name: str) -> None:
    in_prompt = input_dict(component_name=component_name, workflow_name=workflow_name)
    output = component().transform(in_prompt)
    assert output.component_internal_status == 200

    with open(
        component().component_configuration_path(), "r", encoding="utf-8"
    ) as file:
        yaml_data = yaml.safe_load(file)
        base_path = yaml_data["parameters"]["base_path"]
    c_name = convert_to_snake_case(component_name)

    if workflow_name:
        w_name = convert_to_snake_case(workflow_name)
        assert os.path.exists(
            os.path.join(base_path, w_name, "components", c_name, "__init__.py")
        )
        assert os.path.exists(
            os.path.join(base_path, w_name, "components", c_name, f"{c_name}.py")
        )
        assert os.path.exists(
            os.path.join(base_path, w_name, "components", c_name, f"t_{c_name}.py")
        )
        assert os.path.exists(
            os.path.join(base_path, w_name, "components", c_name, f"{c_name}.md")
        )
        assert os.path.exists(
            os.path.join(base_path, w_name, "components", c_name, "configuration.yml")
        )
        assert os.path.exists(
            os.path.join(base_path, w_name, "components", c_name, "Dockerfile")
        )
        assert os.path.exists(
            os.path.join(base_path, w_name, "components", c_name, "requirements.txt")
        )
    else:
        assert os.path.exists(os.path.join(base_path, c_name, "__init__.py"))
        assert os.path.exists(os.path.join(base_path, c_name, f"{c_name}.py"))
        assert os.path.exists(os.path.join(base_path, c_name, f"t_{c_name}.py"))
        assert os.path.exists(os.path.join(base_path, c_name, f"{c_name}.md"))
        assert os.path.exists(os.path.join(base_path, c_name, "configuration.yml"))
        assert os.path.exists(os.path.join(base_path, c_name, "Dockerfile"))
        assert os.path.exists(os.path.join(base_path, c_name, "requirements.txt"))
