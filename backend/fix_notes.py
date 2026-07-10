from pathlib import Path
from config import NOTES_DIR
import re

notes_dir = Path(NOTES_DIR)

for file in notes_dir.glob("**/*.md"):
    text = file.read_text(encoding="utf-8")

    start = text.find("---")
    if start == -1:
        continue

    end = text.find("---", start + 3)
    if end == -1:
        continue

    frontmatter_block = text[start + 3:end].strip()

    if not frontmatter_block or all(
            v.strip() == '' or v.strip() == '[]' or v.strip() == 'null'
            for v in re.findall(r':\s*(.*)', frontmatter_block)
    ):
        cleaned = text[end + 3:].strip()
        file.write_text(cleaned, encoding="utf-8")
        print(f"Corrigido: {file.name}")
    else:
        print(f"OK: {file.name}")