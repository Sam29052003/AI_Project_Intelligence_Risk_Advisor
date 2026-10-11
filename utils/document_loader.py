import os
import pandas as pd
from pypdf import PdfReader
from docx import Document


class DocumentLoader:
    def __init__(self, upload_dir):
        self.upload_dir = upload_dir

    def load_file(self, path):
        ext = os.path.splitext(path)[1].lower()
        if ext == ".pdf":
            reader = PdfReader(path)
            return "\n".join((p.extract_text() or "") for p in reader.pages)
        if ext == ".docx":
            doc = Document(path)
            return "\n".join(p.text for p in doc.paragraphs if p.text)
        if ext == ".csv":
            df = pd.read_csv(path)
            return f"CSV: {os.path.basename(path)}\n" + df.to_string(index=False)
        with open(path, "r", encoding="utf-8") as f:
            return f.read()

    def load_all(self):
        docs = {}
        for f in sorted(os.listdir(self.upload_dir)):
            path = os.path.join(self.upload_dir, f)
            if os.path.isfile(path):
                docs[f] = self.load_file(path)
        return docs
