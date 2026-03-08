from pathlib import Path
from pypdf import PdfReader

pdf_path = Path("Healthcare Monitoring AI Agent - 2 Month - Google Docs.pdf")
out_path = Path("project_text.txt")

reader = PdfReader(str(pdf_path))
parts = []
for i, page in enumerate(reader.pages, start=1):
    text = page.extract_text() or ""
    parts.append(f"\n\n===== PAGE {i} =====\n{text}")

out_path.write_text("".join(parts), encoding="utf-8")
print(f"Wrote {out_path} with {len(reader.pages)} pages")
