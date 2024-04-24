import os

import ctranslate2
import sentencepiece as spm


# [Modify] Set paths to the CTranslate2 and SentencePiece models
ct_model_path = os.getcwd() + "/../models/ct2-nllb-200-distilled-1.2B-int8"
sp_model_path = os.getcwd() + "/../models/flores200_sacrebleu_tokenizer_spm.model"

device = "cpu"  # or "cpu"

# Load the source SentecePiece model
sp = spm.SentencePieceProcessor()
sp.Load(sp_model_path)

IGNORED_CHAR = "5_1"
translator = ctranslate2.Translator(ct_model_path, device)

special_tokens = ["#G", "#!", "@loyalty!", "\\n", "\\n", "\\n"]
source_sents = [
    "The",
    "appointed",
    "admiral",
    "will",
    "gain",
    IGNORED_CHAR,
    "15",
    IGNORED_CHAR,
    "Loyalty",
    IGNORED_CHAR,
    "5_15_15_1",
    "Choice",
    "of",
    "a",
    "naval",
    "bonus.",
]
source_sents = " ".join(source_sents)
source_sents = [source_sents]

# Source and target langauge codes
src_lang = "eng_Latn"
tgt_lang = "spa_Latn"

beam_size = 1

source_sentences = [sent.strip() for sent in source_sents]
print(source_sentences)
target_prefix = [[tgt_lang]] * len(source_sentences)

# Subword the source sentences
source_sents_subworded = sp.EncodeAsPieces(source_sentences)
source_sents_subworded = [
    [src_lang] + sent + ["</s>"] for sent in source_sents_subworded
]

# Translate the source sentences
translator = ctranslate2.Translator(ct_model_path, device=device)
translations_subworded = translator.translate_batch(
    source_sents_subworded,
    batch_type="tokens",
    max_batch_size=2024,
    beam_size=beam_size,
    target_prefix=target_prefix,
)

translations_subworded = [
    translation.hypotheses[0] for translation in translations_subworded
]
for translation in translations_subworded:
    if tgt_lang in translation:
        translation.remove(tgt_lang)

# Desubword the target sentences
translations = sp.Decode(translations_subworded)


# print("First sentence and translation:", source_sentences[0], translations[0], sep="\n• ")

print(translations)
for index, j in enumerate(translations):
    new_sentence = str()
    for i, token in enumerate(translations[index].split()):
        if IGNORED_CHAR in token:
            special_token = special_tokens.pop(0)
            print(f"{token} - {special_token}")
            new_sentence += token.replace(IGNORED_CHAR, special_token)
            if i != len(translations[index].split()) - 1:
                new_sentence += " "
        else:
            new_sentence += token
            if i != len(translations[index].split()) - 1:
                new_sentence += " "
    translations[index] = new_sentence


print()
print(translations)
