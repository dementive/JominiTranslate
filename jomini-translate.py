# Uses NLLB-200 models converted to the CTranslate2 format
# Translates a full localization folder for any Paradox game to any other language supported by the NLLB-200 model used

import sys
import os
import argparse

import customtkinter

from gui import App
from process_yml import ProcessYml

NLLB = "/models/nllb-200_600M_int8_ct2"
NLLB_TOKENIZER = "/models/flores200_sacrebleu_tokenizer_spm.model"

customtkinter.set_appearance_mode("dark")

def gui_app():
    application = App()
    application.mainloop()

def cli_app():
    parser = argparse.ArgumentParser()
    parser.add_argument("-path", required=True, type=str)
    parser.add_argument("-source", required=True, type=str)
    parser.add_argument("-target", required=True, type=str)
    parser.add_argument("-device", default="cpu", choices=["cpu", "cuda"], type=str)
    parser.add_argument("--beam-size", default=1, choices=[1, 4], type=int)
    parser.add_argument("--translation-model", default=f"{os.getcwd()}{NLLB}", type=str)
    parser.add_argument(
        "--tokenize-model", default=f"{os.getcwd()}{NLLB_TOKENIZER}", type=str
    )
    
    args = parser.parse_args()
    ProcessYml(args)

if __name__ == "__main__":
    if len(sys.argv) > 1:
        cli_app()
    else:
        gui_app()