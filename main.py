# This uses M2M-100 models converted to the CTranslate2 format.

from parse_yml import ProcessYml

# Example usage
if __name__ == "__main__":
	ProcessYml("/home/nathan/.local/share/Paradox Interactive/Imperator/mod/TestMod/localization/english").process_and_translate()