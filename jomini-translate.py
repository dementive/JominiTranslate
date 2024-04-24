# Uses NLLB-200 models converted to the CTranslate2 format
# Translates a full localization folder for any Paradox game to any other language supported by the NLLB-200 model used

import os
import argparse
from process_yml import ProcessYml

if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    NLLB = "/models/ct2-nllb-200-distilled-1.2B-int8"
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

    ProcessYml(args)