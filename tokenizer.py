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
from enum import Enum


class LocValue:
    def __init__(self, special_token: str, value=""):
        self.tokens = deque()
        self.special_tokens = deque()
        self.SPECIAL_TOKEN = special_token
        self.current_token_type = TokenType(1)
        self.current_token = ""
        if value:
            self.tokenize_value(value)

    def tokenize_value(self, value: str):
        for i, char in enumerate(value):
            is_last_char = True if len(value) == i + 1 else False
            next_char = "" if is_last_char else value[i + 1]
            if is_last_char or (
                char == " " and self.current_token_type.name == "normal_string"
            ):
                self.add_token(char)
            if char not in ("#", "$", "]", "[", "\\", "@"):
                if (
                    next_char in ("#", "$", "]", "[", "\\", "@")
                    and self.current_token_type.name == "normal_string"
                ):
                    self.current_token_type = TokenType(1)
                    self.add_token(char)
                elif (
                    self.current_token_type.name == "start_formatting"
                    and next_char == " "
                ):
                    self.add_token(char)
                elif char == "!" and (
                    self.current_token_type.name == "end_formatting"
                    or self.current_token_type.name == "text_icon"
                ):
                    self.add_token(char)
                elif char == "n" and self.current_token_type.name == "newline_char":
                    self.add_token(char)
                elif char == "t" and self.current_token_type.name == "tab_char":
                    self.add_token(char)
                else:
                    self.current_token += char
            elif char == "#":
                if next_char == "!":
                    self.current_token_type = TokenType(2)
                elif next_char.isalpha():
                    self.current_token_type = TokenType(3)
                self.current_token += char
            elif char == "$":
                if self.current_token_type.name == "loc_key_link":
                    self.add_token(char)
                elif next_char:
                    self.current_token_type = TokenType(4)
                    self.current_token += char
            elif char == "[":
                self.current_token += char
                if not self.current_token_type.name == "text_icon":
                    self.current_token_type = TokenType(5)
            elif char == "]":
                if self.current_token_type.name == "data_function":
                    self.add_token(char)
                else:
                    self.current_token += char
            elif char == "@":
                if next_char:
                    self.current_token_type = TokenType(6)
                self.current_token += char
            elif char == "\\" and next_char == "n":
                self.current_token += char
                self.current_token_type = TokenType(7)
            elif char == "\\" and next_char == "t":
                self.current_token += char
                self.current_token_type = TokenType(8)

        if self.tokens[-1] == self.SPECIAL_TOKEN:
            self.tokens.append(".")

    def add_token(self, char):
        self.current_token += char
        self.current_token = self.current_token.strip()
        if not self.current_token:
            self.current_token_type = TokenType(1)
            self.current_token = ""
            return

        if self.current_token_type.name == "normal_string":
            self.tokens.append(self.current_token)
        else:
            self.special_tokens.append(self.current_token)
            self.tokens.append(self.SPECIAL_TOKEN)

        self.current_token_type = TokenType(1)
        self.current_token = ""


class TokenType(Enum):
    normal_string = 1
    end_formatting = 2
    start_formatting = 3
    loc_key_link = 4
    data_function = 5
    text_icon = 6
    newline_char = 7
    tab_char = 8
