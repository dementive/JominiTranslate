import os
import glob
import tqdm

import ctranslate2
import sentencepiece as spm

from tokenizer import *
from language import NLLBLanguage


class ProcessYml:
    def __init__(self, args):
        self.map = {}
        try:
            self.source = NLLBLanguage(args.source)
            self.target = NLLBLanguage(args.target)
        except ValueError as e:
            keys = list(NLLBLanguage._value2member_map_.keys())
            formatted_keys = "\n".join(
                [", ".join(keys[i : i + 5]) for i in range(0, len(keys), 5)]
            )
            print(f"{e} is not a valid Option. Must be one of:\n{formatted_keys}")
            exit(1)
        self.SPECIAL_TOKEN = "5_1"
        self.output_dir = f"output/{self.target.value}"
        self.translator = ctranslate2.Translator(
            args.translation_model, device=args.device
        )
        self.sp = spm.SentencePieceProcessor()
        self.sp.Load(args.tokenize_model)

        self.process_directory(args.path)

    def process_directory(self, dir_path):
        if not os.path.exists(dir_path):
            print(f"Directory does not exist: {dir_path}")
            return

        for file_path in glob.glob(os.path.join(dir_path, "**/*.yml"), recursive=True):
            self.map.update({file_path: self.process_file(file_path)})

        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)

        self.process_and_translate()

    def process_file(self, file_path):
        new_map = {}
        with open(file_path, "r") as file:
            for line in file:
                # Find the position of the colon
                colon_pos = line.find(":")
                if colon_pos == -1:  # Skip lines without a colon
                    continue

                # Extract the key and value
                key = line[:colon_pos].strip()
                if key.startswith("#"):
                    continue  # skip comments
                value = line[colon_pos + 1 :].strip()

                # Find the first and last quote in the value
                first_quote = value.find('"')
                last_quote = value.rfind('"')
                if first_quote != -1 and last_quote != -1 and first_quote != last_quote:
                    value = value[first_quote + 1 : last_quote]
                else:
                    # If there are no quotes or only one quote, skip this line
                    continue

                # Store the key-value pair in the map
                new_map[key] = LocValue(value, self.SPECIAL_TOKEN)
        return new_map

    def process_and_translate(self):
        pbar = tqdm.tqdm(self.map)
        for i in pbar:
            filename = os.path.splitext(os.path.basename(i))[0]
            pbar.set_description(f"Translating {filename}")
            dirpath = (
                os.path.join(
                    self.output_dir,
                    filename.replace(self.source.value, self.target.value),
                )
                + ".yml"
            )
            with open(dirpath, "w") as file:
                file.write(f"l_{self.target.value}:\n")
                for x in self.map[i]:
                    translations = self.do_translation(self.map[i][x].tokens)
                    for index, j in enumerate(translations):
                        new_sentence = str()
                        for idx, token in enumerate(translations[index].split()):
                            if (
                                self.SPECIAL_TOKEN in token
                                and len(self.map[i][x].special_tokens) > 0
                            ):
                                special_token = self.map[i][x].special_tokens.pop(0)
                                new_sentence += token.replace(
                                    self.SPECIAL_TOKEN, special_token
                                )
                                if idx != len(translations[index].split()) - 1:
                                    new_sentence += " "
                            else:
                                new_sentence += token
                                if idx != len(translations[index].split()) - 1:
                                    new_sentence += " "
                        translations[index] = new_sentence
                    translated_loc_value = (
                        f" {x}: \"{' '.join(translations)}\"\n".replace(
                            f" {self.SPECIAL_TOKEN}", ""
                        ).replace(" #!", "#!")
                    )
                    file.write(translated_loc_value)

    def do_translation(self, lines):
        # Set language prefixes of the source and target
        lines = " ".join(lines)
        lines = [lines]
        src_lang = f"{self.source.name}"
        target_lang = f"{self.target.name}"

        source_sents = [line.strip() for line in lines]
        target_prefix = [[target_lang]] * len(source_sents)

        # Subword the source sentences
        source_sents_subworded = self.sp.EncodeAsPieces(source_sents)
        source_sents_subworded = [
            [src_lang] + sent + ["</s>"] for sent in source_sents_subworded
        ]

        # Translate the source sentences
        translations = self.translator.translate_batch(
            source_sents_subworded,
            batch_type="tokens",
            beam_size=1,
            target_prefix=target_prefix,
        )

        # Desubword the target sentences
        translations = [translation.hypotheses[0] for translation in translations]
        for translation in translations:
            if target_lang in translation:
                translation.remove(target_lang)
        translations_desubword = self.sp.Decode(translations)

        return translations_desubword
