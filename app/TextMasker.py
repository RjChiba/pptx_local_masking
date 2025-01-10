import sys, os
import zipfile
import shutil
from lxml import etree as ET
from src.TextMaskerUtil import MaskingFunction

def get_xpath(element, root):
    """
    特定のelementに対するXPathを生成する関数
    """
    path = []
    while element is not None and element != root:
        parent = element.getparent() if hasattr(element, 'getparent') else None
        siblings = list(parent) if parent is not None else []
        index = siblings.index(element) if siblings else 0
        tag = element.tag
        if len(siblings) > 1:
            path.append(f"{tag}[{index + 1}]")  # 1始まりのインデックス
        else:
            path.append(tag)
        element = parent
    return '/'.join(reversed(path))

class App:
	def __init__(self):
		self.mask_types = MaskingFunction.mask_types

	def mask(self, dataset, mask_type):
		# dataset: list of texts extracted from the file with xmlpath
		# mask_type: mask types to apply
		# returns: list of masked texts

		textset = [d["content"] for d in dataset]
		new_dataset = []

		masker = MaskingFunction(mask_type)
		masked_texts = masker.masker.execute(textset)

		for i, text in enumerate(masked_texts):
			new_dataset.append({
				"content": text,
				"slide": dataset[i]["slide"],
				"text": dataset[i]["text"],
				"xpath": dataset[i]["xpath"]
			})

		return new_dataset

	def remove_dir(self, exception=None):
		# returns: None
		working_dirs = [f for f in os.listdir(os.path.join(os.getcwd(), 'data')) if os.path.isdir(os.path.join(os.getcwd(), 'data', f))]
		for dir_name in working_dirs:
			if exception and dir_name == exception:
				continue
				
			shutil.rmtree(os.path.join(os.getcwd(), 'data', dir_name))

		return

	def copy_pptx(self, file_path, uid=None):
		# file_path: path of the file to copy
		# uid: unique identifier for dataset
		# returns: None
		dir_name = os.path.join(os.getcwd(), 'data')
		if uid:
			dir_name = os.path.join(dir_name, uid)
		
		os.makedirs(dir_name, exist_ok=True)

		targ_file_path = os.path.join(dir_name, os.path.split(file_path)[1])
		shutil.copy(file_path, targ_file_path)

		return targ_file_path

	def reverse_pptx(self, src, dst):
		# src: source file path
		# dst: destination file path
		# returns: None
		shutil.copy(src, dst)
		return 

	def unzip_pptx(self, file_name):
		# create dir for extracted files with file_name
		dir_name = os.path.join(os.getcwd(), 'data', file_name.split(".")[0])
		os.makedirs(dir_name, exist_ok=True)

		targ_file_path = os.path.join(os.getcwd(), 'data' , file_name)
		with zipfile.ZipFile(targ_file_path, 'r') as zip_ref:
			zip_ref.extractall(dir_name)

	def pptx_text_extract(self, dir_name):
		# dir_name: name of the file to extract text from
		# returns: list of texts extracted from the file with xmlpath
		ppt_dir = os.path.join(dir_name, 'ppt')
		ppt_slides_dir = os.path.join(ppt_dir, 'slides')
		texts = []
		
		slide_index = 0
		slide_files = [f for f in os.listdir(ppt_slides_dir) if f.endswith(".xml")]
		slide_files = sorted(slide_files, key=lambda x: int(x.split('slide')[-1].split('.')[0]))
		for file in slide_files:
			slide_index += 1
			text_index = 1
			if file.endswith('.xml'):
				file_path = os.path.join(ppt_slides_dir, file)
				tree = ET.parse(file_path)
				root = tree.getroot()
				for elem in root.iter():
					if elem.tag.endswith('}t'):
						xpath = get_xpath(elem, root)
						texts.append(
							{"slide":slide_index, "text":text_index, "content":elem.text, "xpath":xpath}
						)
						text_index += 1
		return texts

	def pptx_text_replace(self, dir_name, dataset):
		# dir_name: name of the file to replace text in
		# dataset: list of data to replace with
		# returns: None
		ppt_dir = os.path.join(dir_name, 'ppt')
		ppt_slides_dir = os.path.join(ppt_dir, 'slides')
		c = 0

		slide_files = [f for f in os.listdir(ppt_slides_dir) if f.endswith(".xml")]
		slide_files = sorted(slide_files, key=lambda x: int(x.split('slide')[-1].split('.')[0]))
		for file in slide_files:
			if file.endswith('.xml'):
				file_path = os.path.join(ppt_slides_dir, file)
				tree = ET.parse(file_path)
				root = tree.getroot()
				for elem in root.iter():
					if elem.tag.endswith('}t'):
						elem.text = dataset[c]["content"]
						c += 1
				tree.write(file_path)

	def zip_pptx(self, dir_name):
		# dir_name: name of the file to zip
		# returns: None
		print("zipping")
		print(dir_name)
		targ_file_path = dir_name + "_masked.pptx"

		# use shutil
		shutil.make_archive(targ_file_path, 'zip', dir_name)

		# rename (remove .zip)
		os.rename(targ_file_path+'.zip', targ_file_path)

if __name__ == '__main__':
	app = App()
	pptx_text_extract = app.pptx_text_extract('pitch')