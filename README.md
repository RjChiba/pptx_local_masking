# PPTX Local Mask

## Description
This is a simple tool that allows you to mask the text of a PPTX file. 
It is useful when you want to share a PPTX file with someone, but you want to hide some information like PII (Personally Identifiable Information) or sensitive data.
You can register your own mask function to hide the text in the way you want.

## Installation
1. copy `app` directory to your project.
2. Install the required packages by running the following command:
```bash
pip install -r requirements.txt
```
3. Run the following command to start the app:
```bash
python app/index.py
```
4. Open the browser and go to the following URL:
```bash
http://localhost:3000/
```

## Customization
You can customize the mask function by adding the new folder in `app/src/TextMaskerUtil` directory.
The new folder should contain the following files:
```bash
TextMaskerUtil
├── YourMaskFunction
      ├── __init__.py
      ├── main.py
```
The `main.py` file should contain the following function:
```python
import sys, os

def execute(texts):
      # texts: list of texts to mask
      # returns: list of masked texts
      masked_texts = []
      for text in texts:
            # your masking logic
            masked_texts.append(text)
      return masked_texts
```
After adding the new folder, you can register the new mask function in `app/src/TextMaskerUtil/__init__.py` file:
```python
from .main import *
```
Finally, you need to register the new mask function in `app/src/TextMaskeUtil/setting.json` file:
```json
{
      "plugin":{
            "applied_masker": "default",
            "masker": {
                  "default": {
                        "version": "1.0.0",
                        "author": "Karthik",
                        "path": "default/"
                  },
                  "original": {
                        "version": "1.0.0",
                        "author": "Karthik",
                        "path": "original/"
                  },
                  "YourMaskFunction": {
                        "version": "1.0.0",
                        "author": "Your Name",
                        "path": "YourMaskFunction/"
                 }
            }
      }
}
```
