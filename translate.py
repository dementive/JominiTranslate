import ctranslate2
import sentencepiece as spm
from typing import List

def do_translation(lines: List[str]):
	# [Modify] Set paths to the CTranslate2 and SentencePiece models
	ct_model_path = "/home/nathan/Documents/MetalTranslate/models/translate-fairseq_m2m_100_418M/model"
	sp_model_path = "/home/nathan/Documents/MetalTranslate/models/translate-fairseq_m2m_100_418M/sentencepiece.model"

	# [Modify] Set language prefixes of the source and target
	src_prefix = "__en__"
	tgt_prefix = "__es__"

	# [Modify] Set the device and beam size
	device = "cpu"  # or "cuda" for GPU
	beam_size = 1

	# Load the source SentecePiece model
	sp = spm.SentencePieceProcessor()
	sp.Load(sp_model_path)

	source_sents = [line.strip() for line in lines]
	target_prefix = [[tgt_prefix]] * len(source_sents)

	# Subword the source sentences
	source_sents_subworded = sp.Encode(source_sents, out_type=str)
	source_sents_subworded = [[src_prefix] + sent for sent in source_sents_subworded]

	# Translate the source sentences
	translator = ctranslate2.Translator(ct_model_path, device=device)
	translations = translator.translate_batch(source_sents_subworded, batch_type="tokens", max_batch_size=2024, beam_size=beam_size, target_prefix=target_prefix)
	translations = [translation.hypotheses[0] for translation in translations]


	# Desubword the target sentences
	translations_desubword = sp.Decode(translations)
	translations_desubword = [sent[len(tgt_prefix):] for sent in translations_desubword]
	return translations_desubword
