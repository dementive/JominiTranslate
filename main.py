# Uses M2M-100 models converted to the CTranslate2 format
# Translates a full localization folder for any Paradox game to any other language supported by the M2M model used

import os
import argparse
from process_yml import ProcessYml
from language import Language

if __name__ == "__main__":
	parser = argparse.ArgumentParser()

	parser.add_argument("-path", required=True, type=str)
	parser.add_argument("-source", required=True, choices=[language.value for language in Language], type=str)
	parser.add_argument("-target", required=True, choices=[language.value for language in Language], type=str)
	parser.add_argument("-device", default="cpu", choices=["cpu", "cuda"], type=str)
	parser.add_argument("--translation-model", default=f"{os.getcwd()}/models/translate-fairseq_m2m_100_418M/model", type=str)
	parser.add_argument("--tokenize-model", default=f"{os.getcwd()}/models/translate-fairseq_m2m_100_418M/sentencepiece.model", type=str)
	args = parser.parse_args()
	
	ProcessYml(args)
