import re

# Replace <YOUR_YAML_SNIPPET> with the actual YAML snippet to be validated
YAML_SNIPPET = """name: MyComponent
description: |
  This is a Component that does something cool.

inputs:
  - name: input_data
    description: |
      The input data.
    type: str

outputs:
  - name: output_data
    description: |
      The output data.
    type: str

parameters:
  - name: parameter1
    description: |
      The first parameter.
    type: int
    default: 1

  - name: parameter2
    description: |
      The second parameter.
    type: str
    default: "hello world"

transformer_breakdown: |
  1. Do something cool with the input data.
  2. Return the output data.

external_calls:
  - name: Some external API
    description: |
      Calls an external API.

test:
  - description: |
      Test that the output is a string value.
    input:
      input_data: "hello world"
    output_type: str
  - description: |
      Test that the output matches the input.
    input:
      input_data: "hello world"
    expected_output:
      output_data: "hello world"
      
"""

# Kudos to https://regex101.com/ for their amazing regex tester
# Regex to validate the YAML snippet
REGEX = r"^name: [a-zA-Z0-9_\-]+\s+description: \|[\S\s]*?\n+\s+inputs:(\s+- name: [a-zA-Z0-9_\-]+\s+description: \|[\S\s]*?type: [a-zA-Z0-9_\-]+\n?)+\s+outputs:(\s+- name: [a-zA-Z0-9_\-]+\s+description: \|[\S\s]*?type: [a-zA-Z0-9_\-]+\n?)+\s+parameters:(\s+- name: [a-zA-Z0-9_\-]+\s+description: \|[\S\s]*?type: [a-zA-Z0-9_\-]+\s+default: [\" a-zA-Z0-9_\-]+\n?)+\s+transformer_breakdown: \|[\S\s]*?\n+\s+external_calls:(\s+- name: [ a-zA-Z0-9_\-]+\s+description: \|[\S\s]*?)+\s+test:(\s+- description: \|[\S\s]*?input:(\s+[a-zA-Z0-9_\-]+: [\" a-zA-Z0-9_\-]+)+\s+output_type: [a-zA-Z0-9_\-]+(\s+- description: \|[\S\s]*?input:(\s+[a-zA-Z0-9_\-]+: [\" a-zA-Z0-9_\-]+)+\s+expected_output:(\s+[a-zA-Z0-9_\-]+: [\" a-zA-Z0-9_\-]+)+)+)+$"
if re.match(REGEX, YAML_SNIPPET, re.MULTILINE | re.DOTALL):
    print("YAML snippet is valid")
else:
    print("YAML snippet is invalid")
