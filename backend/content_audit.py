"""Generate a local curricular concept catalogue and a human-readable audit.

Run from ``backend`` with ``python content_audit.py``. It deliberately does
not modify source Markdown; generated artifacts live under backend/data and
docs so editorial work can be prioritized separately.
"""

from __future__ import annotations

import json
import re
from collections import Counter, defaultdict
from pathlib import Path

try:
    from .pedagogical_normalizer import clean_pedagogical_lines
    from .text_utils import normalize_text
except ImportError:
    from pedagogical_normalizer import clean_pedagogical_lines
    from text_utils import normalize_text


ROOT = Path(__file__).resolve().parent.parent
CONTENT_ROOT = ROOT / "contenidos"
CATALOG_PATH = Path(__file__).with_name("data") / "catalogo_conceptos.json"
REPORT_PATH = Path(__file__).with_name("data") / "reporte_auditoria_contenidos.json"
MARKDOWN_REPORT_PATH = ROOT / "docs" / "AUDITORIA_CONTENIDOS_PEDAGOGICOS.md"
IGNORED_PARTS = {"00_documentacion", "17_compendios", "18_rag", "__pycache__", "node_modules"}
SECTION_NAMES = {"definition": ("respuesta breve", "explicacion clara", "explicacion completa"), "example": ("ejemplo",), "summary": ("mini resumen", "ideas fundamentales"), "practice": ("preguntas de practica", "pregunta de practica")}
EXPECTED_COLLECTIONS = {
    "1° básico": ("primero_basico",), "2° básico": ("segundo_basico",),
    "3° básico": ("tercero_basico",), "4° básico": ("cuarto_basico",),
    "5° básico": ("quinto_basico",), "6° básico": ("sexto_basico",),
    "7° básico": ("septimo_basico",), "8° básico": ("octavo_basico",),
    "Matemática": ("matematica",), "Aritmética": ("aritmetica",), "Álgebra": ("algebra",),
    "Geometría": ("geometria",), "Astronomía": ("Enciclopedia_Astronomia_Espacio_1B_a_4M_Chat_Escolar",),
    "Biología": ("Enciclopedia_Biologia_1B_a_4M_Chat_Escolar",), "Física": ("Enciclopedia_Fisica_1B_a_4M_Chat_Escolar",),
    "Química": ("Enciclopedia_Quimica_1B_a_4M_Chat_Escolar",),
    "Ciencias Naturales": ("Enciclopedia_Ciencias_Naturales_Generales_1B_a_4M_Chat_Escolar",),
    "Ciencias de la Tierra": ("Enciclopedia_Ciencias_Tierra_Ecologia_Medioambiente_1B_a_4M_Chat_Escolar",),
    "Historia de Chile": ("Enciclopedia_Historia_de_Chile_1B_a_4M_Chat_Escolar",),
    "Historia Universal": ("Enciclopedia_Historia_Universal_1B_a_4M_Chat_Escolar",),
    "Geografía": ("Enciclopedia_Geografia_Chile_Universal_1B_a_4M_Chat_Escolar",),
    "Educación Ciudadana": ("Enciclopedia_Educacion_Ciudadana_Formacion_Civica_Derecho_1B_a_4M_Chat_Escolar",),
    "Conflictos históricos y guerras": ("Enciclopedia_Conflictos_Historicos_Guerras_1B_a_4M_Chat_Escolar",),
    "Lenguaje": ("lenguaje",),
}


def coverage_report() -> dict:
    """Inventory every Markdown before the filtered pedagogical audit."""
    top_level = [path for path in sorted(CONTENT_ROOT.iterdir()) if path.is_dir()]
    markdown_by_folder = {
        path.name: sum(1 for _ in path.rglob("*.md")) for path in top_level
    }
    ignored = sorted({path.relative_to(CONTENT_ROOT).as_posix() for path in CONTENT_ROOT.rglob("*") if path.is_dir() and path.name in IGNORED_PARTS})
    empty = [name for name, count in markdown_by_folder.items() if count == 0]
    unusual = [path.relative_to(CONTENT_ROOT).as_posix() for path in CONTENT_ROOT.rglob("*") if path.is_file() and (path.suffix.lower() in {".txt", ".docx", ".pdf"} or path.name.lower().endswith(".md.txt"))]
    found = {path.name for path in top_level}
    expected = {
        label: "encontrada" if any(folder in found for folder in alternatives) else "no encontrada"
        for label, alternatives in EXPECTED_COLLECTIONS.items()
    }
    return {
        "markdown_total_encontrado": sum(markdown_by_folder.values()),
        "carpetas_principales": [path.name for path in top_level],
        "markdown_por_carpeta": markdown_by_folder,
        "carpetas_ignoradas": ignored,
        "carpetas_sin_markdown": empty,
        "archivos_extension_no_markdown": unusual,
        "cobertura_esperada": expected,
    }


def _front_matter(raw: str) -> dict[str, str | list[str]]:
    if not raw.startswith("---") or raw.count("---") < 2:
        return {}
    block = raw.split("---", 2)[1]
    values: dict[str, str | list[str]] = {}
    for line in block.splitlines():
        if ":" not in line or line.lstrip().startswith("-"):
            continue
        key, value = line.split(":", 1)
        value = value.strip().strip('"\'')
        if value.startswith("[") and value.endswith("]"):
            values[key.strip()] = [item.strip().strip('"\'') for item in value[1:-1].split(",") if item.strip()]
        else:
            values[key.strip()] = value
    return values


def _sections(content: str) -> dict[str, str]:
    result: dict[str, list[str]] = defaultdict(list)
    current = ""
    for line in content.splitlines():
        match = re.match(r"^#{1,6}\s+(.+)$", line)
        if match:
            current = normalize_text(match.group(1))
        elif current:
            result[current].append(line)
    return {heading: "\n".join(lines) for heading, lines in result.items()}


def _title(content: str, fallback: str) -> str:
    match = re.search(r"(?m)^#\s+(?:Tema:\s*)?(.+)$", content)
    return match.group(1).strip() if match else fallback.replace("_", " ").title()


def _area(path: Path, metadata: dict[str, str | list[str]]) -> str:
    declared = str(metadata.get("area") or metadata.get("asignatura") or "")
    searchable = normalize_text(f"{declared} {path}")
    if any(term in searchable for term in ("matematica", "algebra", "geometria", "aritmetica", "probabilidad")):
        return "Matemática"
    if any(term in searchable for term in ("lenguaje", "literatura", "comunicacion")):
        return "Lenguaje"
    if any(term in searchable for term in ("historia", "geografia", "ciudadana")):
        return "Historia"
    return "Ciencias Naturales"


def _concepts(title: str, metadata: dict[str, str | list[str]]) -> list[str]:
    values = [title, str(metadata.get("tema", "")), str(metadata.get("titulo", ""))]
    keywords = metadata.get("palabras_clave") or metadata.get("keywords") or []
    if isinstance(keywords, list):
        values.extend(keywords)
    concepts: list[str] = []
    for value in values:
        for part in re.split(r"\s*(?:,|/| y | e |;|:)\s*", str(value), flags=re.IGNORECASE):
            normalized = normalize_text(part)
            if 2 <= len(normalized) <= 70 and normalized not in concepts:
                concepts.append(normalized)
    return concepts[:12]


def audit() -> dict:
    catalog: list[dict] = []
    files = 0
    coverage = coverage_report()
    for path in sorted(CONTENT_ROOT.rglob("*.md")):
        relative = path.relative_to(CONTENT_ROOT)
        if any(part in IGNORED_PARTS for part in relative.parts) or path.name.lower().startswith(("readme", "changelog", "00_indice")):
            continue
        try:
            raw = path.read_text(encoding="utf-8")
        except (OSError, UnicodeError):
            continue
        files += 1
        metadata = _front_matter(raw)
        body = raw.split("---", 2)[2] if raw.startswith("---") and raw.count("---") >= 2 else raw
        title = _title(body, path.stem)
        sections = _sections(body)
        fragments = {kind: next((clean_pedagogical_lines(text) for heading, text in sections.items() if any(name in heading for name in names) and clean_pedagogical_lines(text)), "") for kind, names in SECTION_NAMES.items()}
        for concept in _concepts(title, metadata):
            catalog.append({
                "concepto": concept,
                "concepto_normalizado": normalize_text(concept),
                "area": _area(relative, metadata),
                "categoria": str(metadata.get("categoria") or metadata.get("eje") or "Sin categoría"),
                "curso_fuente": str(metadata.get("curso_origen") or metadata.get("curso") or "Sin curso declarado"),
                "titulo_fuente": title,
                "ruta": relative.as_posix(),
                "encabezado": next((heading for heading in sections if concept in heading), ""),
                "palabras_clave": metadata.get("palabras_clave") or metadata.get("keywords") or [],
                "fragmentos_candidatos": fragments,
                "prioridad": int(bool(fragments["definition"])) + int(bool(fragments["example"])) + int(bool(fragments["practice"])),
            })
    by_area = Counter(item["area"] for item in catalog)
    weak = [item for item in catalog if not item["fragmentos_candidatos"]["definition"]]
    report = {"cobertura_documental": coverage, "archivos_analizados": files, "conceptos_detectados": len(catalog), "conceptos_por_materia": dict(by_area), "sin_definicion_clara": weak[:500], "sin_ejemplo": [item for item in catalog if not item["fragmentos_candidatos"]["example"]][:500], "sin_pregunta_practica": [item for item in catalog if not item["fragmentos_candidatos"]["practice"]][:500]}
    CATALOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    MARKDOWN_REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    CATALOG_PATH.write_text(json.dumps(catalog, ensure_ascii=False, indent=2), encoding="utf-8")
    REPORT_PATH.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    coverage_lines = "\n".join(f"- {folder}: {count}" for folder, count in coverage["markdown_por_carpeta"].items())
    expected_lines = "\n".join(f"- {name}: {state}" for name, state in coverage["cobertura_esperada"].items())
    MARKDOWN_REPORT_PATH.write_text("# Auditoría de contenidos pedagógicos\n\n" + f"- Markdown encontrados: {coverage['markdown_total_encontrado']}\n- Archivos analizados (excluyendo carpetas ignoradas): {files}\n- Conceptos detectados: {len(catalog)}\n\n## Markdown por carpeta principal\n\n{coverage_lines}\n\n## Cobertura esperada\n\n{expected_lines}\n\n## Carpetas ignoradas\n\n" + "\n".join(f"- {item}" for item in coverage["carpetas_ignoradas"]) + "\n\n## Conceptos por materia\n\n" + "\n".join(f"- {area}: {count}" for area, count in sorted(by_area.items())) + "\n\n## Prioridades\n\n" + f"- Sin definición clara: {len(weak)}\n", encoding="utf-8")
    return report


if __name__ == "__main__":
    result = audit()
    print(json.dumps({key: result[key] for key in ("archivos_analizados", "conceptos_detectados", "conceptos_por_materia")}, ensure_ascii=False, indent=2))
