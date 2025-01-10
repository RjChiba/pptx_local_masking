# Version: 1.0
import sys, os
import json
import importlib

FILE_PATH = os.path.dirname(os.path.abspath(__file__))

class MaskingFunction:
	settings_path = os.path.join(FILE_PATH, 'TextMaskerUtil', 'settings.json')
	with open(settings_path, "r", encoding="utf-8") as f:
		settings = json.load(f)

	mask_types = [x["name"] for x in settings["plugin"]["masker"]]

	def __init__(self, key):
		indexof = [i for i, x in enumerate(self.mask_types) if x == key]
		if not indexof:
			raise ValueError(f"Masker {key} not found")

		self.key = key
		self.path    = self.settings["plugin"]["masker"][indexof[0]]["path"]
		self.name    = self.settings["plugin"]["masker"][indexof[0]]["name"]
		self.version = self.settings["plugin"]["masker"][indexof[0]]["version"]

		self.masker = MaskingFunction.load_masker(
			os.path.join(FILE_PATH, 'TextMaskerUtil', self.path)
		)

	@staticmethod
	def load_masker(path):
		if not os.path.exists(path):
			raise ValueError(f"Masker {path} not found")

		sys.path.append(os.path.join(FILE_PATH, 'TextMaskerUtil'))
		masker = importlib.import_module("default")
		return masker

if __name__ == '__main__':
	default_masker = MaskingFunction("default")
	print(default_masker.masker.execute(["Hello World!"]))

