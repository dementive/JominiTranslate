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

import re

text_icon_re = re.compile(r"@\[?[^]]*\]?!")
text_format_re = re.compile(r"#\w+")


class LocValue:
    def __init__(self, str, special_token):
        self.tokens = []
        self.special_tokens = []
        self.SPECIAL_TOKEN = special_token
        self.tokenize_value(str)

    def handle_end_formatting(self, value):
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
        self.special_tokens.extend(re.findall(text_icon_re, value))
        svalue = re.sub(text_icon_re, self.SPECIAL_TOKEN, value)
        pattern = rf"({self.SPECIAL_TOKEN}|\\n|\s|\\t)"
        parts = re.split(pattern, svalue)
        # Filter out empty strings from the result
        parts = [part for part in parts if part]
        for i in parts:
            if i in ("\\n", "\\t"):
                self.tokens.append(self.SPECIAL_TOKEN)
                self.special_tokens.append(i)
            else:
                self.tokens.append(i)

    def handle_text_formatting(self, value):
        match = re.match(text_format_re, value)
        if match:
            matched_value = match.group()
            self.tokens.append(self.SPECIAL_TOKEN)
            self.special_tokens.append(matched_value)

    def tokenize_value(self, value: str):
        split_values = value.split()
        for value in split_values:
            if value.endswith("#!"):
                self.handle_end_formatting(value)
            elif re.search(text_format_re, value):
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
