# Uses NLLB-200 models converted to the CTranslate2 format
# Translates a full localization folder for any Paradox game to any other language supported by the NLLB-200 model used

import os
import argparse

from process_yml import ProcessYml
from language import NLLBLanguage

if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    NLLB = "/models/nllb-200-distilled-600M-int8"
    NLLB_TOKENIZER = "/models/flores200_sacrebleu_tokenizer_spm.model"

    parser.add_argument("-path", required=True, type=str)
    parser.add_argument("-source", required=True, type=str)
    parser.add_argument("-target", required=True, type=str)
    parser.add_argument("-device", default="cpu", choices=["cpu", "cuda"], type=str)
    parser.add_argument("--translation-model", default=f"{os.getcwd()}{NLLB}", type=str)
    parser.add_argument(
        "--tokenize-model", default=f"{os.getcwd()}{NLLB_TOKENIZER}", type=str
    )
    args = parser.parse_args()

    try:
        args.source = NLLBLanguage(args.source)
        args.target = NLLBLanguage(args.target)
    except ValueError as e:
        keys = list(NLLBLanguage._value2member_map_.keys())
        formatted_keys = "\n".join(
            [", ".join(keys[i : i + 5]) for i in range(0, len(keys), 5)]
        )
        print(f"{e} is not a valid option. Must be one of:\n{formatted_keys}")
        exit(1)

    # NEW ARGS:
    # --beam-size: Can be either "1", "4".
    # 1 does "Greedy search is the most basic and fastest decoding strategy. It simply takes the token that has the highest probability at each timestep."
    # 4 does "Beam search is a common decoding strategy for sequence models. The algorithm keeps N hypotheses at all times. This negatively impacts decoding speed and memory but allows finding a better final hypothesis."

    ProcessYml(args)
