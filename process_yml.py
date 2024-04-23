import os
import glob
from typing import List

import ctranslate2
import sentencepiece as spm

from tokenizer import *
from language import Language

class ProcessYml:
    def __init__(self, args):
        self.map = {}
        self.source = Language(args.source)
        self.target = Language(args.target)
        self.output_dir = f"output/{self.target.name}"
        self.translator = ctranslate2.Translator(args.translation_model, device=args.device)
        self.sp = spm.SentencePieceProcessor()
        self.sp.Load(args.tokenize_model)

        self.process_directory(args.path)

    def process_directory(self, dir_path):
        if not os.path.exists(dir_path):
            print(f"Directory does not exist: {dir_path}")
            return

        for file_path in glob.glob(os.path.join(dir_path, "*.yml")):
            self.map.update({file_path: self.process_file(file_path)})

        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)

        self.process_and_translate()

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
                if key.startswith("#"):
                    continue # skip comments
                value = line[colon_pos + 1:].strip()

                # Find the first and last quote in the value
                first_quote = value.find('"')
                last_quote = value.rfind('"')
                if first_quote != -1 and last_quote != -1 and first_quote != last_quote:
                    value = value[first_quote + 1:last_quote]
                else:
                    # If there are no quotes or only one quote, skip this line
                    continue

                # Store the key-value pair in the map
                new_map[key] = LocValue(value)
        return new_map

    def process_and_translate(self):
        for i in self.map:
            filename = os.path.splitext(os.path.basename(i))[0]
            dirpath = os.path.join(self.output_dir, filename.replace(self.source.name, self.target.name)) + ".yml"
            with open(dirpath, "w") as file:
                file.write(f"l_{self.target.name}:\n")
                for x in self.map[i]:
                    translations = self.do_translation(self.map[i][x].tokens)
                    for index, j in enumerate(translations):
                        translations[index] = j.strip()
                        if translations[index] == "<unk>":
                            special_token = self.map[i][x].special_tokens.pop(0)
                            translations[index] = j.replace("<unk>", special_token).strip()

                    for index, j in enumerate(translations):
                        if index+1 != len(translations) and translations[index + 1] == "#!":
                            translations[index] = j + "#!"
                        elif j == "#!":
                            del translations[index]
                    translated_loc_value = f" {x}: \"{' '.join(translations)}\"\n"
                    file.write(translated_loc_value)

    def do_translation(self, lines: List[str]):
        # Set language prefixes of the source and target
        src_prefix = f"__{self.source.value}__"
        tgt_prefix = f"__{self.target.value}__"

        source_sents = [line.strip() for line in lines]
        target_prefix = [[tgt_prefix]] * len(source_sents)

        # Subword the source sentences
        source_sents_subworded = self.sp.Encode(source_sents, out_type=str)
        source_sents_subworded = [[src_prefix] + sent for sent in source_sents_subworded]

        # Translate the source sentences
        translations = self.translator.translate_batch(source_sents_subworded, batch_type="tokens", beam_size=1, target_prefix=target_prefix)
        translations = [translation.hypotheses[0] for translation in translations]


        # Desubword the target sentences
        translations_desubword = self.sp.Decode(translations)
        translations_desubword = [sent[len(tgt_prefix):] for sent in translations_desubword]
        return translations_desubword
