import pytest
from component_batch_creator import (
    ComponentBatchCreator,
    ComponentListYaml,
    GeneratedComponents,
)


TEST_DATA = [
    (
        {"component_list_yaml": "name: test_component\n"},
        {"generated_components": ["test_component"]},
    ),
    (
        {"component_list_yaml": "name: test_component\n"},
        {"generated_components": ["test_component"]},
    ),
    (
        {
            "component_list_yaml": "name: foo_component\ndescription: This is a foo component\n"
        },
        {"generated_components": ["foo_component"]},
    ),
]


@pytest.mark.parametrize("mock_input, expected_output", TEST_DATA)
def test_component_batch_creator_transform(mock_input: dict, expected_output: dict):
    component_list_yaml = ComponentListYaml(**mock_input)
    component_batch_creator = ComponentBatchCreator()
    output = component_batch_creator.transform(component_list_yaml)
    assert output.dict() == expected_output


def test_empty_input():
    mock_input = {"component_list_yaml": ""}
    component_list_yaml = ComponentListYaml(**mock_input)
    component_batch_creator = ComponentBatchCreator()

    with pytest.raises(
        Exception
    ):  # Replace Exception with the appropriate exception class
        component_batch_creator.transform(component_list_yaml)


def test_invalid_yaml_input():
    mock_input = {"component_list_yaml": "Invalid YAML input"}
    component_list_yaml = ComponentListYaml(**mock_input)
    component_batch_creator = ComponentBatchCreator()

    with pytest.raises(yaml.YAMLError):
        component_batch_creator.transform(component_list_yaml)
