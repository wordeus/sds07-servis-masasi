#!/usr/bin/env python3
"""İki haftalık ilerleme raporunu dersin Word şablonundan üretir.

Şablonun üst bilgi bandı, bilgi tablosu ve beş başlığı olduğu gibi korunur. Yalnız
yer tutucu metinler ve tablo satırları içerik dosyasından (JSON) doldurulur. Köşeli
parantezli metinler ("[Ad Soyad]") kullanıcının dolduracağı alanlardır ve sarı
vurguyla işaretlenir.

Kullanım:
    python tools/build_report.py --template <şablon.docx> \
        --content docs/reports/rapor-03.content.json --output docs/reports/Rapor-03_Hafta-3.docx

Gereksinim: lxml (requirements-docs.txt). Standart xml kütüphanesi kullanılmaz; çünkü
Word'ün mc:Ignorable ad alanı bildirimlerini korumaz.
"""

from __future__ import annotations

import argparse
import copy
import json
import re
import sys
import zipfile
from datetime import UTC, datetime
from pathlib import Path

from lxml import etree

W_NS = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
NS = {"w": W_NS}
XML_NS = "http://www.w3.org/XML/1998/namespace"
PLACEHOLDER = re.compile(r"(\[[^\]]+\])")


def w(tag: str) -> str:
    return f"{{{W_NS}}}{tag}"


def text_of(element) -> str:
    return "".join(t.text or "" for t in element.iter(w("t")))


# --- Çalıştırma (run) yardımcıları ---------------------------------------------
RPR_ORDER = [
    "rStyle",
    "rFonts",
    "b",
    "bCs",
    "i",
    "iCs",
    "caps",
    "smallCaps",
    "strike",
    "dstrike",
    "outline",
    "shadow",
    "emboss",
    "imprint",
    "noProof",
    "snapToGrid",
    "vanish",
    "webHidden",
    "color",
    "spacing",
    "w",
    "kern",
    "position",
    "sz",
    "szCs",
    "highlight",
    "u",
    "effect",
    "bdr",
    "shd",
    "fitText",
    "vertAlign",
    "rtl",
    "cs",
    "em",
    "lang",
    "eastAsianLayout",
    "specVanish",
    "oMath",
]


def set_rpr_flag(rpr, name: str, on: bool, value: str | None = None) -> None:
    """rPr içinde bir öğeyi şema sırasına uygun ekler veya kaldırır."""
    existing = rpr.find(f"w:{name}", NS)
    if not on:
        if existing is not None:
            rpr.remove(existing)
        return
    if existing is None:
        existing = etree.Element(w(name))
        position = RPR_ORDER.index(name)
        insert_at = len(rpr)
        for index, child in enumerate(rpr):
            local = etree.QName(child).localname
            if local in RPR_ORDER and RPR_ORDER.index(local) > position:
                insert_at = index
                break
        rpr.insert(insert_at, existing)
    if value is not None:
        existing.set(w("val"), value)


def make_run(base_rpr, text: str, *, italic=False, bold=None, highlight=False, size=None, color=None):
    run = etree.Element(w("r"))
    rpr = copy.deepcopy(base_rpr) if base_rpr is not None else etree.Element(w("rPr"))
    set_rpr_flag(rpr, "i", italic)
    if bold is not None:
        set_rpr_flag(rpr, "b", bold)
    if size is not None:
        set_rpr_flag(rpr, "sz", True, str(size))
    if color is not None:
        set_rpr_flag(rpr, "color", True, color)
    set_rpr_flag(rpr, "highlight", highlight, "yellow" if highlight else None)
    run.append(rpr)
    t = etree.SubElement(run, w("t"))
    t.text = text
    t.set(f"{{{XML_NS}}}space", "preserve")
    return run


def first_text_rpr(paragraph):
    for run in paragraph.findall("w:r", NS):
        if run.find("w:t", NS) is not None:
            return run.find("w:rPr", NS)
    return None


def fill_paragraph(paragraph, text: str, base_rpr, **style) -> None:
    for run in paragraph.findall("w:r", NS):
        paragraph.remove(run)
    for segment in PLACEHOLDER.split(text):
        if segment:
            paragraph.append(make_run(base_rpr, segment, highlight=bool(PLACEHOLDER.fullmatch(segment)), **style))


def fill_cell(cell, value) -> None:
    """Hücreyi bir veya birden çok paragrafla doldurur; biçimi ilk paragraftan alır."""
    lines = value if isinstance(value, list) else [value]
    paragraphs = cell.findall("w:p", NS)
    base_p = paragraphs[0]
    base_rpr = first_text_rpr(base_p)
    for extra in paragraphs[1:]:
        cell.remove(extra)
    fill_paragraph(base_p, lines[0], base_rpr)
    previous = base_p
    for line in lines[1:]:
        new_p = copy.deepcopy(base_p)
        fill_paragraph(new_p, line, base_rpr)
        previous.addnext(new_p)
        previous = new_p


def keep_with_next(paragraph) -> None:
    """Paragrafa keepNext ekler (şema sırası: pStyle'dan hemen sonra)."""
    ppr = paragraph.find("w:pPr", NS)
    if ppr is None:
        ppr = etree.Element(w("pPr"))
        paragraph.insert(0, ppr)
    if ppr.find("w:keepNext", NS) is None:
        index = 1 if ppr.find("w:pStyle", NS) is not None else 0
        ppr.insert(index, etree.Element(w("keepNext")))


# --- Tablo yardımcıları --------------------------------------------------------
def ensure_trpr(row, *, header: bool) -> None:
    trpr = row.find("w:trPr", NS)
    if trpr is None:
        trpr = etree.Element(w("trPr"))
        index = 1 if row.find("w:tblPrEx", NS) is not None else 0
        row.insert(index, trpr)
    if trpr.find("w:cantSplit", NS) is None:
        trpr.insert(0, etree.Element(w("cantSplit")))
    if header and trpr.find("w:tblHeader", NS) is None:
        trpr.append(etree.Element(w("tblHeader")))


def set_widths(table, widths: list[int]) -> None:
    grid_cols = table.findall("w:tblGrid/w:gridCol", NS)
    if len(grid_cols) != len(widths):
        raise ValueError(f"Sütun sayısı uyuşmuyor: şablon {len(grid_cols)}, içerik {len(widths)}")
    for col, width in zip(grid_cols, widths, strict=True):
        col.set(w("w"), str(width))
    for row in table.findall("w:tr", NS):
        for cell, width in zip(row.findall("w:tc", NS), widths, strict=True):
            tcw = cell.find("w:tcPr/w:tcW", NS)
            if tcw is not None:
                tcw.set(w("w"), str(width))
                tcw.set(w("type"), "dxa")


def fill_table(table, spec: dict) -> None:
    rows = table.findall("w:tr", NS)
    header, prototypes = rows[0], rows[1:3] if len(rows) >= 3 else [rows[1], rows[1]]
    expected = spec.get("expect_header")
    if expected and not text_of(header).startswith(expected):
        raise ValueError(f"Beklenen tablo başlığı bulunamadı: {expected!r} / {text_of(header)[:60]!r}")
    for row in rows[1:]:
        table.remove(row)
    ensure_trpr(header, header=True)
    for index, values in enumerate(spec["rows"]):
        row = copy.deepcopy(prototypes[index % 2])
        cells = row.findall("w:tc", NS)
        if len(cells) != len(values):
            raise ValueError(f"Satır {index + 1}: {len(values)} değer, {len(cells)} hücre")
        for cell, value in zip(cells, values, strict=True):
            fill_cell(cell, value)
        ensure_trpr(row, header=False)
        table.append(row)
    if "widths" in spec:
        set_widths(table, spec["widths"])


def note_paragraph(base_paragraph, text: str):
    note = copy.deepcopy(base_paragraph)
    rpr = first_text_rpr(note)
    ppr = note.find("w:pPr", NS)
    if ppr is None:
        ppr = etree.Element(w("pPr"))
        note.insert(0, ppr)
    spacing = ppr.find("w:spacing", NS)
    if spacing is None:
        spacing = etree.SubElement(ppr, w("spacing"))
    spacing.set(w("before"), "80")
    spacing.set(w("after"), "80")
    fill_paragraph(note, text, rpr, italic=True, size=17, color="555555")
    return note


# --- Ana akış ------------------------------------------------------------------
# build() küçük adımlara bölündü (Hafta 3, RSK-07): her adım tek iş yapar ve ayrı okunur.
def _template_parts(root):
    """Belge gövdesindeki tabloları ve "1. ".."5. " başlıklarını bulur."""
    children = list(root.find("w:body", NS))
    tables = [c for c in children if etree.QName(c).localname == "tbl"]
    headings = {}
    for child in children:
        match = re.match(r"^([1-5])\. ", text_of(child)) if etree.QName(child).localname == "p" else None
        if match:
            headings[int(match.group(1))] = child
    if sorted(headings) != [1, 2, 3, 4, 5]:
        raise ValueError(f"Şablonda beş başlık bulunamadı: {sorted(headings)}")
    return tables, headings


def _fill_info(info_table, info: dict) -> None:
    """Bilgi tablosu: etiket hücresinin sağındaki değer hücresi doldurulur."""
    pending = dict(info)
    for row in info_table.findall("w:tr", NS):
        cells = row.findall("w:tc", NS)
        for label_cell, value_cell in zip(cells[0::2], cells[1::2], strict=True):
            label = text_of(label_cell).strip()
            if label in pending:
                fill_cell(value_cell, pending.pop(label))
    if pending:
        raise ValueError(f"Bilgi tablosunda bulunamayan alanlar: {list(pending)}")


def _fill_summary(placeholder, paragraphs: list[str]) -> None:
    """1. Dönem özeti: başlıktan sonraki yer tutucu paragraf ve gerekirse kopyaları."""
    base_rpr = first_text_rpr(placeholder)
    previous = placeholder
    for index, paragraph_text in enumerate(paragraphs):
        target = placeholder if index == 0 else copy.deepcopy(placeholder)
        fill_paragraph(target, paragraph_text, base_rpr, italic=False)
        if index:
            previous.addnext(target)
        previous = target


def _fill_sections(headings: dict, specs: dict, note_template) -> None:
    """2-5. Başlıktan sonraki tablo doldurulur; notlar tablonun altına eklenir."""
    for section in (2, 3, 4, 5):
        table = headings[section].getnext()
        if etree.QName(table).localname != "tbl":
            raise ValueError(f"{section}. başlıktan sonra tablo yok.")
        spec = specs[str(section)]
        fill_table(table, spec)
        anchor = table
        for note in spec.get("notes", []):
            paragraph = note_paragraph(note_template, note)
            anchor.addnext(paragraph)
            anchor = paragraph


def _core_properties(core_xml: bytes, core: dict) -> bytes:
    root = etree.fromstring(core_xml)
    core_ns = {
        "dc": "http://purl.org/dc/elements/1.1/",
        "cp": "http://schemas.openxmlformats.org/package/2006/metadata/core-properties",
        "dcterms": "http://purl.org/dc/terms/",
    }
    now = datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")
    values = (
        ("dc:title", core["title"]),
        ("dc:creator", core["creator"]),
        ("dc:description", core["description"]),
        ("cp:lastModifiedBy", core["creator"]),
        ("dcterms:created", now),
        ("dcterms:modified", now),
    )
    for xpath, value in values:
        element = root.find(xpath, core_ns)
        if element is not None:
            element.text = value
    return etree.tostring(root, xml_declaration=True, encoding="UTF-8", standalone=True)


def build(template: Path, content: dict, output: Path) -> None:
    with zipfile.ZipFile(template) as source:
        entries = [(info, source.read(info.filename)) for info in source.infolist()]
    files = {info.filename: data for info, data in entries}

    root = etree.fromstring(files["word/document.xml"])
    tables, headings = _template_parts(root)
    for heading in headings.values():
        keep_with_next(heading)  # Başlık sayfa sonunda tablosundan ayrı kalmasın
    if content["template_check"]["banner_contains"] not in text_of(tables[0]):
        raise ValueError("Şablon üst bilgi bandı beklenen metni içermiyor.")

    _fill_info(tables[1], content["info"])
    placeholder = headings[1].getnext()
    _fill_summary(placeholder, content["summary"])
    _fill_sections(headings, content["tables"], placeholder)
    files["word/document.xml"] = etree.tostring(root, xml_declaration=True, encoding="UTF-8", standalone=True)
    files["docProps/core.xml"] = _core_properties(files["docProps/core.xml"], content["core"])

    output.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_DEFLATED) as target:
        for info, _ in entries:
            target.writestr(info.filename, files[info.filename])


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--template", type=Path, required=True)
    parser.add_argument("--content", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args(argv)
    content = json.loads(args.content.read_text(encoding="utf-8"))
    build(args.template, content, args.output)
    print(f"Rapor yazıldı: {args.output}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
