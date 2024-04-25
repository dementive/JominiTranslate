"""
Handles special tokens that should not get translated with the rest of the text in a loc key.
All of these tokens are instead replaced with a special character that the translation model will ignore during the translation.
The special tokens include:
\n
\t
[sChar('name').GetName]
@[scope.('scope_name').GetName]!
$loc_key_link$
@text_icon_link!
#G
#!
"""

from collections import deque


class LocValue:
    def __init__(self, str, special_token):
        self.tokens = deque()
        self.special_tokens = deque()
        self.SPECIAL_TOKEN = special_token
        self.tokenize_value(str)

    def handle_end_formatting(self, value):
        idx = value.index("#!")
        first_part = value[:idx]

        if "]" in first_part:
            self.tokens.append(self.SPECIAL_TOKEN)
            self.tokens.append(self.SPECIAL_TOKEN)
            self.special_tokens.append(first_part)
            self.special_tokens.append("#!")
        else:
            self.tokens.append(value.replace("#!", ""))
            self.tokens.append(self.SPECIAL_TOKEN)
            self.special_tokens.append("#!")

    def handle_special_token(self, value):
        self.tokens.append(self.SPECIAL_TOKEN)
        self.special_tokens.append(value)

    def handle_endl(self, value):
        newlines = value.split("\\n")
        for i, token in enumerate(newlines):
            if i + 1 == len(newlines):
                break
            if token == "":
                token = "\\n"
                self.special_tokens.append("\\n")
                self.tokens.append(self.SPECIAL_TOKEN)
            else:
                self.tokens.append(token)

    def handle_text_icon(self, value):
        for i in value.split("@"):
            if i.endswith("!"):
                self.special_tokens.append(f"@{i}")
                self.tokens.append(self.SPECIAL_TOKEN)
            elif "!" in i:
                idx = i.index("!") + 1
                first_part, second_part = i[:idx], i[idx:]
                self.special_tokens.append(f"@{first_part}")
                self.tokens.append(self.SPECIAL_TOKEN)
                self.tokens.append(second_part)
            else:
                self.tokens.append(i)

    def handle_text_formatting(self, value):
        if value.startswith("#") and value.endswith("#"):
            self.tokens.append(self.SPECIAL_TOKEN)
            self.special_tokens.append(value)

    def tokenize_value(self, value: str):
        split_values = value.split()
        for value in split_values:
            if all(c not in value for c in "#$]\\n@"):
                self.tokens.append(value)
            elif value.endswith("#!"):
                self.handle_end_formatting(value)
            elif value.startswith("#") and value.endswith("#"):
                self.handle_text_formatting(value)
            elif value.endswith("$"):
                self.handle_special_token(value)
            elif value.endswith("]"):
                self.handle_special_token(value)
            elif value.startswith("\\n"):
                self.handle_endl(value)
            elif value.endswith("\\n"):
                self.handle_endl(value)
            elif "@" in value:
                self.handle_text_icon(value)
            else:
                self.tokens.append(value)
