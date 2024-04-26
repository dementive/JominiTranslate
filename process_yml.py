import os
import glob

import tqdm
import ctranslate2
import sentencepiece as spm

from tokenizer import *


class ProcessYml:
    def __init__(self, args):
        self.source = args.source
        self.target = args.target
        self.translation_model = args.translation_model
        self.device = args.device
        self.tokenize_model = args.tokenize_model
        self.SPECIAL_TOKEN = "5_1"  # This doens't work perfectly for all languages and is particuarly bad for chinese, should try to find a better way to ignore these tokens...
        self.output_dir = f"output/{self.target.value}"
        self.process_directory(args.path)

    def init_models(self):
        self.translator = ctranslate2.Translator(
            self.translation_model, device=self.device
        )
        self.sp = spm.SentencePieceProcessor()
        self.sp.Load(self.tokenize_model)

    def process_directory(self, dir_path):
        if not os.path.exists(dir_path):
            print(f"Directory does not exist: {dir_path}")
            return

        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)

        self.process_and_translate(dir_path)

    def process_file(self, file_path):
        new_map = {}
        with open(file_path, "r") as file:
            for line in file:
                colon_pos = line.find(":")
                if colon_pos == -1:
                    continue

                key = line[:colon_pos].strip()
                if key.startswith("#"):
                    continue
                value = line[colon_pos + 1 :].strip()

                first_quote = value.find('"')
                last_quote = value.rfind('"')
                if first_quote != -1 and last_quote != -1 and first_quote != last_quote:
                    value = value[first_quote + 1 : last_quote]
                else:
                    # If there are no quotes or only one quote, skip this line
                    continue

                if key and not value:
                    new_map[key] = LocValue(self.SPECIAL_TOKEN)
                else:
                    new_map[key] = LocValue(self.SPECIAL_TOKEN, value)
        return new_map

    def process_and_translate(self, dir_path):
        self.init_models()
        for file_path in glob.glob(os.path.join(dir_path, "**/*.yml"), recursive=True):
            file_dict = {file_path: self.process_file(file_path)}
            for i in file_dict:
                filename = os.path.splitext(os.path.basename(i))[0]
                print(f"Processing \033[93m{filename}\033[0m")
                dirpath = (
                    os.path.join(
                        self.output_dir,
                        filename.replace(self.source.value, self.target.value),
                    )
                    + ".yml"
                )
                with open(dirpath, "w") as file:
                    file.write(f"l_{self.target.value}:\n")
                    total_lines = len(file_dict[i])
                    pbar = tqdm.tqdm(file_dict[i], total=total_lines)
                    for line_num, x in enumerate(pbar):
                        color = "\033[93m" if line_num + 1 < total_lines else "\033[92m"
                        pbar.set_description(
                            f"Translating line {color}{line_num+1}\033[0m/{color}{total_lines}\033[0m"
                        )
                        tokens = file_dict[i][x].tokens
                        if len(tokens) != 0:
                            translations = self.do_translation(tokens)
                            file.write(
                                self.post_process_translations(
                                    translations, file_dict[i][x], x
                                )
                            )
                        else:
                            file.write(f' {x}: ""\n')
                    print()

    def post_process_translations(self, translations, loc_value, x):
        for index in range(len(translations)):
            new_sentence = str()
            for idx, token in enumerate(translations[index].split()):
                if self.SPECIAL_TOKEN in token and len(loc_value.special_tokens) > 0:
                    special_token = loc_value.special_tokens.popleft()
                    new_sentence += token.replace(self.SPECIAL_TOKEN, special_token)
                    if idx != len(translations[index].split()) - 1:
                        new_sentence += " "
                else:
                    new_sentence += token
                    if idx != len(translations[index].split()) - 1:
                        new_sentence += " "
            translations[index] = new_sentence
        translated_loc_value = f" {x}: \"{' '.join(translations)}\"\n".replace(
            f" {self.SPECIAL_TOKEN}", ""
        ).replace(" #!", "#!")

        return translated_loc_value

    def do_translation(self, lines):
        # Set language prefixes of the source and target
        lines = [" ".join(lines)]

        source_sents = [line.strip() for line in lines]
        target_prefix = [[self.target.name]] * len(source_sents)

        # Subword the source sentences
        source_sents_subworded = self.sp.EncodeAsPieces(source_sents)
        source_sents_subworded = [
            [self.source.name] + sent + ["</s>"] for sent in source_sents_subworded
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
            if self.target.name in translation:
                translation.remove(self.target.name)
        translations_desubword = self.sp.Decode(translations)

        return translations_desubword
