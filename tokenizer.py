import re

text_icon_re = re.compile(r"@[A-Za-z_0-9][A-Za-z_0-9]*!")
text_format_re = re.compile(r"#\w+")

class LocValue:
    def __init__(self, str):
        self.tokens = []
        self.special_tokens = []
        self.tokenize_value(str)

    def handle_end_formatting(self, value):
        self.tokens.append(value.replace("#!", ""))
        self.tokens.append("<unk>")
        self.special_tokens.append("#!")

    def handle_special_token(self, value):
        self.tokens.append("<unk>")
        self.special_tokens.append(value)

    def handle_endl(self, value, start):
        if start:
            self.tokens.append("<unk>")
            self.tokens.append(value.replace("\\n", ""))
            self.special_tokens.append("\n")
        else:
            self.tokens.append(value.replace("\\n", ""))
            self.tokens.append("<unk>")
            self.special_tokens.append("\n")

    def handle_text_icon(self, value):
        self.special_tokens.extend(re.findall(text_icon_re, value))
        svalue = re.sub(text_icon_re, "<unk>", value)
        pattern = r'(<unk>|\\n|\s|\\t)'
        parts = re.split(pattern, svalue)
        # Filter out empty strings from the result
        parts = [part for part in parts if part]
        for i in parts:
            if i in ("\\n", "\\t"):
                self.tokens.append("<unk>")
                self.special_tokens.append(i)
            else:
                self.tokens.append(i)

    def handle_text_formatting(self, value):
        match = re.match(text_format_re, value)
        if match:
            matched_value = match.group()
            self.tokens.append("<unk>")
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
                self.handle_endl(value, True)
            elif value.endswith("\\n"):
                self.handle_endl(value, False)
            elif "@" in value:
                self.handle_text_icon(value)
            else:
                self.tokens.append(value)
