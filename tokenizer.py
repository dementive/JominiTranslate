class LocValue:
    def __init__(self, str):
        self.tokens = []
        self.special_tokens = []
        self.tokenize_value(str)

    def tokenize_value(self, str):
        temp = ''
        inBrackets = False
        index = 0

        for i, c in enumerate(str):
            if c == '[' or (i+1 != len(str) and str[i] == '$' and str[i + 1].isalpha()):
                inBrackets = True
                temp = '' # Clear temp to start collecting new token
            elif c == ']':
                inBrackets = False
                temp = '[' + temp + ']'
                self.special_tokens.append(temp)
                # Add special character that will be ignored by translation and readded after translation
                # This is needed so the translator doens't mess up any [] functions or $$ parameters
                self.tokens.append("<unk>")
                index += 1
                temp = '' # Clear temp for the next token
            elif c == "$" and inBrackets:
                inBrackets = False
                temp = '$' + temp + '$'
                self.special_tokens.append(temp)
                self.tokens.append("<unk>")
                index += 1
                temp = ''
            elif c == ' ' and not inBrackets:
                if temp:
                    self.tokens.append(temp)
                    index += 1
                    temp = ''
            else:
                temp += c

        # Add the last token if it's not empty
        if temp:
            self.tokens.append(temp)
            index += 1
