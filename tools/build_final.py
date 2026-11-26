#!/usr/bin/env python3
"""Dönem sonu proje teslim dokümanını dersin Word şablonundan üretir (Faz 5).

Şablonun başlıkları, tablo düzeni ve biçimi korunur. Köşeli parantezli yer tutucu
paragraflar içerik dosyasındaki metinle değiştirilir; tablolar içerik dosyasından veya
doğrudan izlenebilirlik kaynaklarından üretilir:

* RTM tablosu: `docs/traceability/requirements.csv` + `docs/SRS.md` gereksinim metinleri
* Test sonuçları tablosu: `docs/TEST_RESULTS.md` (build_rtm.py çıktısı, gerçek sonuçlar)

Böylece belgedeki sayılar kanıtlarla birebir aynıdır; elle sonuç yazılmaz (PRC-06).
İçerikte kalan köşeli parantezli metin sarı vurgulanır (kullanıcının dolduracağı alan).

Kullanım:
    python tools/build_final.py --template <şablon.docx> --content docs/final/final.content.json \
        --output docs/final/SDS-07_Donem_Sonu_Teslim_Dokumani.docx

Gereksinim: lxml (requirements-docs.txt).
"""

from __future__ import annotations

import argparse
import copy
import csv
import json
import re
import struct
import sys
import zipfile
from pathlib import Path

from lxml import etree

sys.path.insert(0, str(Path(__file__).resolve().parent))
import build_report as br  # noqa: E402 - aynı klasördeki yardımcılar

NS = br.NS
w = br.w
ROOT = Path(__file__).resolve().parent.parent
R_NS = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
REL_NS = "http://schemas.openxmlformats.org/package/2006/relationships"
IMAGE_REL = "http://schemas.openxmlformats.org/officeDocument/2006/relationships/image"
EMU_PER_INCH = 914400


# --- Kaynaklardan tablo satırları -------------------------------------------------
def srs_statements(srs: Path) -> dict[str, str]:
    """SRS tablolarındaki `| FR-xx | metin | ...` satırlarından gereksinim metinleri (ilk geçiş)."""
    statements: dict[str, str] = {}
    for line in srs.read_text(encoding="utf-8").splitlines():
        m = re.match(r"^\| ((?:FR|NFR)-\d+) \| ([^|]+?) \|", line)
        if m and m.group(1) not in statements and len(m.group(2)) > 25:
            statements[m.group(1)] = m.group(2).strip()
    return statements


def rtm_rows(requirements: Path, srs: Path) -> tuple[list[list[str]], int]:
    """Kapsam içi gereksinimler (FR/NFR, öncelik, modül, testler); kapsam dışı sayısı."""
    statements = srs_statements(srs)
    rows, out_of_scope = [], 0
    with requirements.open(encoding="utf-8-sig", newline="") as handle:
        for req in csv.DictReader(handle):
            if req["week"].strip().casefold() == "kapsam dışı":
                out_of_scope += 1
                continue
            kind = "Fonksiyonel" if req["type"] == "FR" else "Fonksiyonel olmayan"
            text = statements.get(req["id"], req["title"])
            tests = ", ".join(t for t in req["tests"].split(";") if t)
            rows.append([req["id"], kind, text, req["priority"], req["modules"], tests])
    return rows, out_of_scope


def test_rows(test_results: Path) -> list[list[str]]:
    """TEST_RESULTS.md test tablosundan: kimlik, gereksinim, seviye, girdi, beklenen, sonuç."""
    rows = []
    for line in test_results.read_text(encoding="utf-8").splitlines():
        if not line.startswith("| TC-"):
            continue
        cells = [c.strip() for c in line.strip().strip("|").split(" | ")]
        tc_id, reqs, level, given, expected, _week, status = cells[:7]
        rows.append([tc_id, reqs, level, given.replace("\\|", "|"), expected.replace("\\|", "|"), status.strip("*")])
    return rows


# --- Resim ekleme ---------------------------------------------------------------
def png_size(path: Path) -> tuple[int, int]:
    data = path.read_bytes()[:24]
    if data[:8] != b"\x89PNG\r\n\x1a\n":
        raise ValueError(f"PNG değil: {path}")
    return struct.unpack(">II", data[16:24])


DRAWING = """<w:drawing xmlns:w="{w}" xmlns:wp="http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing"
 xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main"
 xmlns:pic="http://schemas.openxmlformats.org/drawingml/2006/picture" xmlns:r="{r}">
<wp:inline distT="0" distB="0" distL="0" distR="0"><wp:extent cx="{cx}" cy="{cy}"/><wp:docPr id="{id}" name="{name}" descr="{descr}"/>
<a:graphic><a:graphicData uri="http://schemas.openxmlformats.org/drawingml/2006/picture"><pic:pic>
<pic:nvPicPr><pic:cNvPr id="{id}" name="{name}"/><pic:cNvPicPr/></pic:nvPicPr>
<pic:blipFill><a:blip r:embed="{rid}"/><a:stretch><a:fillRect/></a:stretch></pic:blipFill>
<pic:spPr><a:xfrm><a:off x="0" y="0"/><a:ext cx="{cx}" cy="{cy}"/></a:xfrm><a:prstGeom prst="rect"><a:avLst/></a:prstGeom></pic:spPr>
</pic:pic></a:graphicData></a:graphic></wp:inline></w:drawing>"""


class Images:
    def __init__(self, files: dict):
        self.files = files
        self.rels = etree.fromstring(files["word/_rels/document.xml.rels"])
        self.count = 0
        types = etree.fromstring(files["[Content_Types].xml"])
        ct = "{http://schemas.openxmlformats.org/package/2006/content-types}"
        if not any(d.get("Extension") == "png" for d in types.findall(f"{ct}Default")):
            default = etree.SubElement(types, f"{ct}Default")
            default.set("Extension", "png")
            default.set("ContentType", "image/png")
            files["[Content_Types].xml"] = etree.tostring(
                types, xml_declaration=True, encoding="UTF-8", standalone=True
            )

    def paragraph(self, template_p, path: Path, alt: str, width_in: float):
        self.count += 1
        name = f"sds07_diyagram_{self.count}.png"
        self.files[f"word/media/{name}"] = path.read_bytes()
        rid = f"rIdSds{self.count}"
        rel = etree.SubElement(self.rels, f"{{{REL_NS}}}Relationship")
        rel.set("Id", rid)
        rel.set("Type", IMAGE_REL)
        rel.set("Target", f"media/{name}")
        px_w, px_h = png_size(path)
        cx = int(width_in * EMU_PER_INCH)
        cy = int(cx * px_h / px_w)
        max_cy = int(7.0 * EMU_PER_INCH)
        if cy > max_cy:
            cx, cy = int(cx * max_cy / cy), max_cy
        p = copy.deepcopy(template_p)
        for run in p.findall("w:r", NS):
            p.remove(run)
        ppr = p.find("w:pPr", NS)
        if ppr is None:
            ppr = etree.SubElement(p, w("pPr"))
            p.remove(ppr)
            p.insert(0, ppr)
        jc = ppr.find("w:jc", NS)
        if jc is None:
            jc = etree.SubElement(ppr, w("jc"))
        jc.set(w("val"), "center")
        run = etree.SubElement(p, w("r"))
        xml = DRAWING.format(w=br.W_NS, r=R_NS, cx=cx, cy=cy, id=1000 + self.count, name=name, descr=alt, rid=rid)
        run.append(etree.fromstring(xml))
        return p

    def save(self):
        self.files["word/_rels/document.xml.rels"] = etree.tostring(
            self.rels, xml_declaration=True, encoding="UTF-8", standalone=True
        )


TBLPR_AFTER_LAYOUT = {"tblCellMar", "tblLook", "tblCaption", "tblDescription"}


def fix_layout(table, total: int) -> None:
    """Sabit tablo düzeni: Word sütunları içeriğe göre yeniden hesaplamaz, verilen genişlikleri kullanır."""
    tblpr = table.find("w:tblPr", NS)
    tblw = tblpr.find("w:tblW", NS)
    if tblw is not None:
        tblw.set(w("type"), "dxa")
        tblw.set(w("w"), str(total))
    layout = tblpr.find("w:tblLayout", NS)
    if layout is None:
        layout = etree.Element(w("tblLayout"))
        position = len(tblpr)
        for index, child in enumerate(tblpr):
            if etree.QName(child).localname in TBLPR_AFTER_LAYOUT:
                position = index
                break
        tblpr.insert(position, layout)
    layout.set(w("type"), "fixed")


# --- Doldurma -------------------------------------------------------------------
def replace_placeholder(paragraph, blocks: list, images: Images) -> None:
    """Yer tutucu paragrafı bir veya daha çok paragraf/resimle değiştirir; biçimi korur."""
    base_rpr = br.first_text_rpr(paragraph)
    anchor = paragraph
    first = True
    for block in blocks:
        if isinstance(block, dict) and "image" in block:
            new_p = images.paragraph(paragraph, ROOT / block["image"], block.get("alt", ""), block.get("width_in", 6.0))
            anchor.addnext(new_p)
            anchor = new_p
            if block.get("caption"):
                cap = br.note_paragraph(paragraph, block["caption"])
                anchor.addnext(cap)
                anchor = cap
            continue
        if first:
            br.fill_paragraph(paragraph, block, base_rpr, italic=False)
            first = False
            continue
        new_p = copy.deepcopy(paragraph)
        br.fill_paragraph(new_p, block, base_rpr, italic=False)
        anchor.addnext(new_p)
        anchor = new_p
    if first:  # yalnız resim verildiyse yer tutucu paragraf kalkar
        paragraph.getparent().remove(paragraph)


def build(template: Path, content: dict, output: Path) -> list[str]:
    with zipfile.ZipFile(template) as source:
        entries = [(info, source.read(info.filename)) for info in source.infolist()]
    files = {info.filename: data for info, data in entries}
    root = etree.fromstring(files["word/document.xml"])
    images = Images(files)

    paragraphs = {}
    for p in root.iter(w("p")):
        text = br.text_of(p).strip()
        if text:
            paragraphs.setdefault(text, []).append(p)
    for placeholder, blocks in content["paragraphs"].items():
        hits = paragraphs.get(placeholder, [])
        if len(hits) != 1:
            raise ValueError(f"Yer tutucu {len(hits)} kez bulundu: {placeholder[:70]!r}")
        replace_placeholder(hits[0], blocks if isinstance(blocks, list) else [blocks], images)

    sources = {
        "rtm": lambda: rtm_rows(ROOT / "docs/traceability/requirements.csv", ROOT / "docs/SRS.md")[0],
        "tests": lambda: test_rows(ROOT / "docs/TEST_RESULTS.md"),
    }
    tables = root.findall(".//w:tbl", NS)
    for spec in content["tables"]:
        matches = [t for t in tables if br.text_of(t.find("w:tr", NS)).startswith(spec["expect_header"])]
        if len(matches) != 1:
            raise ValueError(f"Tablo {len(matches)} kez bulundu: {spec['expect_header']!r}")
        table_spec = dict(spec)
        if "source" in spec:
            table_spec["rows"] = sources[spec["source"]]()
        if "width_ratios" in spec:  # şablonun toplam genişliği içerik sütunlarına oranlanır
            total = sum(int(c.get(w("w"))) for c in matches[0].findall("w:tblGrid/w:gridCol", NS))
            ratios = spec["width_ratios"]
            table_spec["widths"] = [int(total * r / sum(ratios)) for r in ratios]
        br.fill_table(matches[0], table_spec)
        if "width_ratios" in spec:
            fix_layout(matches[0], sum(table_spec["widths"]))
        for p in matches[0].find("w:tr", NS).iter(w("p")):  # başlık satırı ilk veri satırından ayrılmasın
            br.keep_with_next(p)
        if spec.get("note"):
            matches[0].addnext(br.note_paragraph(root.find(".//w:body/w:p", NS), spec["note"]))

    remaining = sorted({br.text_of(p) for p in root.iter(w("p")) if re.fullmatch(r"\[[^\]]+\]", br.text_of(p).strip())})
    images.save()
    files["word/document.xml"] = etree.tostring(root, xml_declaration=True, encoding="UTF-8", standalone=True)
    files["docProps/core.xml"] = br._core_properties(files["docProps/core.xml"], content["core"])
    output.parent.mkdir(parents=True, exist_ok=True)
    names = [info.filename for info, _ in entries] + [n for n in files if n.startswith("word/media/sds07_")]
    with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_DEFLATED) as target:
        for name in names:
            target.writestr(name, files[name])
    return remaining


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--template", type=Path, required=True)
    parser.add_argument("--content", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args(argv)
    content = json.loads(args.content.read_text(encoding="utf-8"))
    remaining = build(args.template, content, args.output)
    print(f"Belge yazıldı: {args.output}")
    if remaining:
        print("Doldurulmamış yer tutucular:", "; ".join(remaining), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
