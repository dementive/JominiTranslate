import os
import glob

from tokenizer import *
from translate import do_translation

class ProcessYml:
    def __init__(self, dir_path):
        self.map = {}
        self.process_directory(dir_path)

    def process_directory(self, dir_path):
        if not os.path.exists(dir_path):
            print(f"Directory does not exist: {dir_path}")
            return

        for file_path in glob.glob(os.path.join(dir_path, "*.yml")):
            self.map.update({file_path: self.process_file(file_path)})

    def process_file(self, file_path):
        new_map = {}
        with open(file_path, 'r') as file:
            for line in file:
                # Find the position of the colon
                colon_pos = line.find(':')
                if colon_pos == -1: # Skip lines without a colon
                    continue

                # Extract the key and value
                key = line[:colon_pos].strip()
                value = line[colon_pos + 1:].strip()

                # Find the first and last quote in the value
                first_quote = value.find('"')
                last_quote = value.rfind('"')
                if first_quote != -1 and last_quote != -1 and first_quote != last_quote:
                    # Extract the substring between the first and last quote
                    value = value[first_quote + 1:last_quote]
                else:
                    # If there are no quotes or only one quote, skip this line
                    continue

                # Store the key-value pair in the map
                new_map[key] = LocValue(value)
        return new_map

    def process_and_translate(self):
        for i in self.map:
            print(i)
            for x in self.map[i]:
                translations = do_translation(self.map[i][x].tokens)
                for index, j in enumerate(translations):
                    translations[index] = j.strip()
                    if translations[index] == "<unk>":
                        special_token = self.map[i][x].special_tokens.pop(0)
                        translations[index] = j.replace("<unk>", special_token).strip()
                print(f"{x}: \"{' '.join(translations)}\"")
            print()
