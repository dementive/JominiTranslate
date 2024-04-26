# jomini-translate

Jomini Translate is a cli program that runs a [NLLB-200](https://forum.opennmt.net/t/nllb-200-with-ctranslate2/5090) language translation model with [CTranslate2](https://github.com/OpenNMT/CTranslate2) to translate all the localization files in mods for any paradox game in any language to one of 200 other languages supported by the NLLB-200 model. All translation is done offline locally on your computer by the model so you don't need to deal with rate limits or other limitations like you would with most translation services.

# Setup

To start you will need to have python version 3.11 or greater installed and then run `pip install -r requirements.txt` to install all of the python dependencies.

Next run the init script (init on linux, init.ps1 on windows). This will download the NLLB model and unzip to the models folder.

By default the script will install NLLB-200-1.2B, there are a few other NLLB versions that may be better for you depending on your use case to download these just uncomment the part of the script you need.
For more info on the difference between the models read here https://forum.opennmt.net/t/nllb-200-with-ctranslate2/5090/3

# Usage

`python jomini-translate -path "./tests/english" -source english -target spanish`

## CLI Arguments

### `-path`
- **Description**: Specifies the path to the localization folder for translation.
- **Example**: `"path/to/mod/localization/english/"`
- **Required**: Yes

### `-source`
- **Description**: Indicates the source language to translate from. For a list of all possible languages, refer to `language.py`.
- **Example**: `english`
- **Required**: Yes

### `-target`
- **Description**: Specifies the target language to translate to.
- **Example**: `spanish`
- **Required**: Yes

### `-device`
- **Description**: Sets the device for translation. `cuda` will run the translation on the GPU if you have a GPU that supports it and CUDA 12.0+ is installed.
- **Example**: `cuda/cpu`
- **Default**: `cpu`

### `--beam-size`
- **Description**: Can be either `"1"` or `"4"`.
 - `1` performs a Greedy search, which is the most basic and fastest decoding strategy. It simply takes the token with the highest probability at each timestep.
 - `4` uses Beam search, a common decoding strategy for sequence models. The algorithm keeps N hypotheses at all times, which negatively impacts decoding speed and memory but allows finding a better final hypothesis.
 - **Default**: `cpu`


### `--translation-model`
- **Description**: Specifies the full path to the NLLB-200 translation model folder to use.
- **Default**: `"/models/nllb-200-distilled-600M-int8"`

### `--tokenize-model`
- **Description**: Specifies the full path to the NLLB-200 compatible sentencepiece tokenization model file to use.
- **Default**: `"/models/flores200_sacrebleu_tokenizer_spm.model"`


## Translation Speed

The hardware you are using, the `-device` argument, the `--beam-size` argument, and which NLLB model you are using can all have a big impact on the speed, memory usage, and translation quality of the program.

To maximize the translation speed use the NLLB-200-600M model, it translates about twice as fast as the other models but has lower translation quality. Also use the `cuda` device option to run translations on the GPU and set the `--beam-size` argument to 1.

To maximize translation quality at the expense of speed use the NLLB-200-3.3B model (or newer compatible NLLB model) and set the `--beam-size` argument to 4.
