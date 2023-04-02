def convert_to_snake_case(string: str) -> str:
    new_string = ""
    for i, char in enumerate(string):
        if char.isupper():
            if i > 0 and string[i - 1].islower():
                new_string += "_"
            new_string += char.lower()
        else:
            new_string += char
    return new_string
