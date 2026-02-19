import PyPDF2
from pathlib import Path

PDF_PATH = Path("extras/files/ford_motor_bond_2022.pdf")
OUTPUT_PATH = Path("extras/files/ford_motor_textfile.txt")


def extract_text_from_pdf(pdf_path: Path) -> str:
    with open(pdf_path, "rb") as f:
        reader = PyPDF2.PdfReader(f)
        return "\n".join(page.extract_text() or "" for page in reader.pages)


def save_text(text: str, output_path: Path) -> None:
    output_path.write_text(text, encoding="utf-8")


if __name__ == "__main__":
    text = extract_text_from_pdf(PDF_PATH)
    save_text(text, OUTPUT_PATH)
    print(f"Extracted text saved to {OUTPUT_PATH}")
