# jomini-translate

Jomini Translate is a cli program that runs a [NLLB-200](https://forum.opennmt.net/t/nllb-200-with-ctranslate2/5090) language translation model with [CTranslate2](https://github.com/OpenNMT/CTranslate2) to translate all the localization files in mods for any paradox game in any language to one of 200 other languages supported by the NLLB-200 model.

# Setup

To start you will need to run the init script (init on linux, init.ps1 on windows). This will download the NLLB model and unzip to the models folder.

By default the script will install NLLB-200-1.2B, there are a few other NLLB versions that may be better for you depending on your use case to download these just uncomment the part of the script you need.
For more info on the difference between the models read here https://forum.opennmt.net/t/nllb-200-with-ctranslate2/5090/3

# Usage

`python jomini-translate`

## Arguments

- -path:
	Description: Path to the localization folder you want to translate
	Example: "path/to/mod/localization/english/"
	Required: True

- -source
	Description: Source language to translate from, for all possible languages look at language.py
	Example: english
	Required: True

- -target
	Description: Target language to translate to
	Example: spanish
	Required: True

- -device
	Description: Set the device for the translation to use, cuda will run the translation on the gpu if you have a gpu that supports it and cuda 12.0+ installed.
	Example: cuda/cpu
	Default: cpu

- --translation-model
	Description: Full path to the NLLB-200 translation model folder to use
	Default: "/models/ct2-nllb-200-distilled-1.2B-int8"

- --tokenize-model
	Description: Full path to the NLLB-200 compatible sentencepiece tokenization model file to use
	Default: "/models/flores200_sacrebleu_tokenizer_spm.model"
