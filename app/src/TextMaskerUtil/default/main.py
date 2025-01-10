import sys, os

def execute(texts):
	# texts: list of texts to mask
	# returns: list of masked texts
	masked_texts = []
	for text in texts:
		masked_text = '*'*len(text)
		masked_texts.append(masked_text)
	return masked_texts