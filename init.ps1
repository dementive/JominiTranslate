# Installation of a pre-trained NLLB-200 model and tokenizer
# For more information and a comparison of the 3 models below read more here: https://forum.opennmt.net/t/nllb-200-with-ctranslate2/5090

# 600M
# Invoke-WebRequest -Uri "https://pretrained-nmt-models.s3.us-west-004.backblazeb2.com/CTranslate2/nllb/nllb-200_600M_int8_ct2.zip" -OutFile "models\nllb-200_600M_int8_ct2.zip"
# Expand-Archive -Path "models\nllb-200_600M_int8_ct2.zip" -DestinationPath "models\"
# Remove-Item "models\nllb-200_600M_int8_ct2.zip"

# 1.2B
Invoke-WebRequest -Uri "https://pretrained-nmt-models.s3.us-west-004.backblazeb2.com/CTranslate2/nllb/nllb-200_1.2B_int8_ct2.zip" -OutFile "models\nllb-200_1.2B_int8_ct2.zip"
Expand-Archive -Path "models\nllb-200_1.2B_int8_ct2.zip" -DestinationPath "models\"
Remove-Item "models\nllb-200_1.2B_int8_ct2.zip"

# 3.3B
# Invoke-WebRequest -Uri "https://pretrained-nmt-models.s3.us-west-004.backblazeb2.com/CTranslate2/nllb/nllb-200_3.3B_int8_ct2.zip" -OutFile "models\nllb-200_3.3B_int8_ct2.zip"
# Expand-Archive -Path "models\nllb-200_3.3B_int8_ct2.zip" -DestinationPath "models\"
# Remove-Item "models\nllb-200_3.3B_int8_ct2.zip"

# Tokenizer model
Invoke-WebRequest -Uri "https://pretrained-nmt-models.s3.us-west-004.backblazeb2.com/CTranslate2/nllb/flores200_sacrebleu_tokenizer_spm.model" -OutFile "models\flores200_sacrebleu_tokenizer_spm.model"
