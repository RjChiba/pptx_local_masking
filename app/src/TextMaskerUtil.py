# Version: 1.0
import sys, os
import json
import importlib

FILE_PATH = os.path.dirname(os.path.abspath(__file__))

class MaskingFunction:
	def __init__(self):
		settings_path = os.path.join(FILE_PATH, 'TextMaskerUtil', 'settings.json')
		with open(settings_path, "r", encoding="utf-8") as f:
			settings = json.load(f)

		applied_mask_type = settings["plugin"]["applied_masker"]

		self.name = applied_mask_type
		self.path    = settings["plugin"]["masker"][applied_mask_type]["path"]
		self.version = settings["plugin"]["masker"][applied_mask_type]["version"]

		self.masker = MaskingFunction.load_masker(
			applied_mask_type,
			os.path.join(FILE_PATH, 'TextMaskerUtil', self.path)
		)

	@staticmethod
	def load_masker(applied_mask_type, path):
		if not os.path.exists(path):
			raise ValueError(f"Masker {path} not found")

		sys.path.append(os.path.join(FILE_PATH, 'TextMaskerUtil'))
		masker = importlib.import_module(applied_mask_type)
		return masker