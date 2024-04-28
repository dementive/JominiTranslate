import os
import glob

import tqdm
import ctranslate2
import sentencepiece as spm

from language import NLLBLanguage
from tokenizer import *


class ProcessYml:
    def __init__(self, args):
        try:
            self.source = args.source = NLLBLanguage(args.source)
            self.target = args.target = NLLBLanguage(args.target)
        except ValueError as e:
            keys = list(NLLBLanguage._value2member_map_.keys())
            formatted_keys = "\n".join(
                [", ".join(keys[i : i + 5]) for i in range(0, len(keys), 5)]
            )
            print(f"{e} is not a valid option. Must be one of:\n{formatted_keys}")
            exit(1)
        self.translation_model = args.translation_model
        self.device = args.device
        self.tokenize_model = args.tokenize_model
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
                    new_map[key] = LocValue()
                else:
                    new_map[key] = LocValue(value)
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
                lines = deque([f"l_{self.target.value}:\n"])
                total_lines = len(file_dict[i])
                pbar = tqdm.tqdm(file_dict[i], total=total_lines)
                for line_num, x in enumerate(pbar):
                    color = "\033[93m" if line_num + 1 < total_lines else "\033[92m"
                    pbar.set_description(
                        f"Translating line {color}{line_num+1}\033[0m/{color}{total_lines}\033[0m"
                    )
                    translated_tokens = deque()
                    for index, token_deque in enumerate(file_dict[i][x].tokens):
                        translations = self.do_translation(token_deque)
                        translated_tokens.append(self.post_process_translations_new(translations, file_dict[i][x].special_tokens, index))
                    if len(translated_tokens) != 0:
                        lines.append(f' {x}: "{" ".join(translated_tokens)}"\n')
                    else:
                        lines.append(f' {x}: ""\n')
                with open(dirpath, "w", encoding="utf-8-sig") as file:
                    file.writelines(lines)
                print()


    def post_process_translations_new(self, translations, special_tokens, index):
        if index in special_tokens:
            for i in special_tokens[index]:
                translations.append(i)

        translations = " ".join(translations)
        return translations.replace(" #!", "#!")

    def do_translation(self, lines):
        # Set language prefixes of the source and target
        source_sents = [lines]
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
            no_repeat_ngram_size=25,
            disable_unk=True,
            target_prefix=target_prefix,
        )

        # Desubword the target sentences
        translations = [translation.hypotheses[0] for translation in translations]
        for translation in translations:
            if self.target.name in translation:
                translation.remove(self.target.name)
        translations_desubword = self.sp.Decode(translations)

        return translations_desubword
