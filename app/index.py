from flask import Flask, request, render_template, session, jsonify
from datetime import timedelta
import os
import json
from typing import Dict, List, Optional, Union
from dataclasses import dataclass
from TextMasker import App as MaskApp
import random
import string

@dataclass
class SessionData:
    identifier: str
    filepath: str
    copied_filepath: str

class PPTXMaskingApp:
    def __init__(self):
        self.app = Flask(__name__)
        self.app.secret_key = os.getenv('FLASK_SECRET_KEY', 'default_secret_key')
        self.app.permanent_session_lifetime = timedelta(minutes=5)
        self.mask_app = MaskApp()
        self._register_routes()

    def _register_routes(self) -> None:
        self.app.route("/")(self.index)
        self.app.route("/convert", methods=["POST"])(self.convert)

    def _generate_uid(self) -> str:
        """Generate a unique identifier for the session."""
        return ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))

    def _get_session_data(self) -> Optional[SessionData]:
        """Retrieve session data if it exists."""
        try:
            return SessionData(
                identifier=session["identifier"],
                filepath=session["filepath"],
                copied_filepath=session["copied_filepath"]
            )
        except KeyError:
            return None

    def _process_file(self, file_path: str, uid: str) -> tuple[List, List]:
        """Process the PPTX file and return original and masked datasets."""
        copied_file_path = self.mask_app.copy_pptx(file_path, uid)
        self.mask_app.unzip_pptx(copied_file_path)

        # Store session data
        session["identifier"] = uid
        session["filepath"] = file_path
        session["copied_filepath"] = copied_file_path

        xml_dir = copied_file_path.replace(".pptx", "")
        dataset_original = self.mask_app.pptx_text_extract(xml_dir)
        dataset_masked = self.mask_app.mask(dataset_original, "default")

        # Save datasets
        self._save_datasets(copied_file_path, dataset_original, dataset_masked)

        return dataset_original, dataset_masked

    def _save_datasets(self, file_path: str, original: List, masked: List) -> None:
        """Save datasets to JSON files."""
        dataset_dir = os.path.dirname(file_path)
        for filename, data in [
            ("dataset_original.json", original),
            ("dataset_masked.json", masked)
        ]:
            file_path = os.path.join(dataset_dir, filename)
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False)

    def _load_datasets(self, dataset_dir: str) -> tuple[List, List]:
        """Load datasets from JSON files."""
        datasets = {}
        for filename in ["dataset_original.json", "dataset_masked.json"]:
            file_path = os.path.join(dataset_dir, filename)
            with open(file_path, "r", encoding="utf-8") as f:
                key = filename.replace(".json", "")
                datasets[key] = json.load(f)
        return datasets["dataset_original"], datasets["dataset_masked"]

    def index(self):
        """Handle the index route."""
        try:
            file_path = request.args.get("filepath")
            if not file_path:
                return render_template("index.html", filepath=None, dataset=[], mask_types=[])

            uid = self._generate_uid()
            self.mask_app.remove_dir(exception=uid)
            
            dataset_original, dataset_masked = self._process_file(file_path, uid)

            return render_template("index.html",
                identifier=uid,
                filepath=file_path,
                dataset_original=dataset_original,
                dataset_masked=dataset_masked)

        except Exception as e:
            return render_template("index.html", filepath=None, dataset=[], mask_types=[], error="")

    def convert(self):
        """Handle the convert route."""
        try:
            data = request.get_json()
            if not data:
                return jsonify({"error": "No JSON data provided"}), 400

            checked = data.get("checked", [])
            uid = data.get("identifier")
            
            session_data = self._get_session_data()
            if not session_data or uid != session_data.identifier:
                return jsonify({"ok": False, "error": "Invalid session"}), 401

            if not checked:
                return jsonify({"ok": True, "error": "No mask type provided"})

            # Load datasets
            dataset_dir = os.path.dirname(session_data.copied_filepath)
            dataset_original, dataset_masked = self._load_datasets(dataset_dir)

            # Create masked dataset
            masked_dataset = [
                line if i in checked else dataset_original[i]
                for i, line in enumerate(dataset_masked)
            ]

            # Process and save the masked PPTX
            xml_dir = session_data.copied_filepath.replace(".pptx", "")
            self.mask_app.pptx_text_replace(xml_dir, masked_dataset)
            self.mask_app.zip_pptx(xml_dir)
            
            masked_output = session_data.copied_filepath.replace(".pptx", "_masked.pptx")
            final_output = session_data.filepath.replace(".pptx", "_masked.pptx")
            self.mask_app.reverse_pptx(masked_output, final_output)

            # Cleanup
            self.mask_app.remove_dir()

            return jsonify({"ok": True})

        except Exception as e:
            return jsonify({"ok": False, "error": str(e)}), 500

    def run(self, **kwargs):
        """Run the Flask application."""
        self.app.run(**kwargs)

if __name__ == "__main__":
    app = PPTXMaskingApp()
    app.run(debug=True, port=3000, host="localhost")
