def convert_to_snake_case(s: str) -> str:
    new_s = ""
    for i, c in enumerate(s):
        if c.isupper():
            if i > 0 and s[i - 1].islower():
                new_s += "_"
            new_s += c.lower()
        else:
            new_s += c
    return new_s
