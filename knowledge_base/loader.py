"""
Carrega a base de conhecimento a partir do PDF Guide CloudWalk Social 2025.
"""

from pathlib import Path

# PDF padrão: Guide CloudWalk Social 2025
KB_DIR = Path(__file__).resolve().parent.parent / "knowledge_base"
DEFAULT_PDF = KB_DIR / "Guide_CloudWalk_Social_2025.pdf"

_cached_text: str | None = None


def get_kb_text(pdf_path: Path | None = None) -> str:
    """
    Extrai todo o texto do PDF da KB. Usa cache em memória após a primeira leitura.
    """
    global _cached_text
    if _cached_text is not None:
        return _cached_text
    path = pdf_path or DEFAULT_PDF
    if not path.exists():
        return ""
    try:
        from pypdf import PdfReader
        reader = PdfReader(str(path))
        parts = []
        for page in reader.pages:
            t = page.extract_text()
            if t:
                parts.append(t)
        _cached_text = "\n\n".join(parts)
        return _cached_text
    except Exception:
        return ""
