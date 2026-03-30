from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Sequence

from PIL import Image, ImageDraw, ImageFont


BASE_DIR = Path(__file__).resolve().parent.parent
DOCS_DIR = BASE_DIR / "docs"
OUTPUT_PNG = DOCS_DIR / "car_vision_highlevel_detailed_v2.png"

WIDTH = 2600
HEIGHT = 1650


@dataclass
class Box:
    x: int
    y: int
    w: int
    h: int
    title: str
    lines: list[str]
    fill: tuple[int, int, int]
    border: tuple[int, int, int] = (56, 72, 100)

    @property
    def rect(self) -> tuple[int, int, int, int]:
        return (self.x, self.y, self.x + self.w, self.y + self.h)

    @property
    def left(self) -> tuple[int, int]:
        return (self.x, self.y + self.h // 2)

    @property
    def right(self) -> tuple[int, int]:
        return (self.x + self.w, self.y + self.h // 2)

    @property
    def top(self) -> tuple[int, int]:
        return (self.x + self.w // 2, self.y)

    @property
    def bottom(self) -> tuple[int, int]:
        return (self.x + self.w // 2, self.y + self.h)


def _load_font(size: int, bold: bool = False) -> ImageFont.ImageFont:
    candidates: list[Path] = []
    if bold:
        candidates += [Path("C:/Windows/Fonts/segoeuib.ttf"), Path("C:/Windows/Fonts/arialbd.ttf")]
    else:
        candidates += [Path("C:/Windows/Fonts/segoeui.ttf"), Path("C:/Windows/Fonts/arial.ttf")]
    candidates += [Path("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf")]

    for p in candidates:
        if p.exists():
            return ImageFont.truetype(str(p), size=size)
    return ImageFont.load_default()


def _background(draw: ImageDraw.ImageDraw) -> None:
    for y in range(HEIGHT):
        t = y / HEIGHT
        r = int(248 - 22 * t)
        g = int(251 - 16 * t)
        b = int(255 - 10 * t)
        draw.line([(0, y), (WIDTH, y)], fill=(r, g, b), width=1)


def _panel(draw: ImageDraw.ImageDraw, rect: tuple[int, int, int, int], title: str, font: ImageFont.ImageFont) -> None:
    x1, y1, x2, y2 = rect
    draw.rounded_rectangle(rect, radius=18, fill=(245, 249, 255), outline=(180, 201, 230), width=2)
    draw.rounded_rectangle((x1 + 2, y1 + 2, x2 - 2, y1 + 44), radius=16, fill=(226, 237, 252), outline=(180, 201, 230), width=2)
    draw.rectangle((x1 + 2, y1 + 30, x2 - 2, y1 + 44), fill=(226, 237, 252), outline=(226, 237, 252))
    draw.text((x1 + 14, y1 + 11), title, fill=(20, 44, 80), font=font)


def _box(draw: ImageDraw.ImageDraw, b: Box, title_font: ImageFont.ImageFont, body_font: ImageFont.ImageFont) -> None:
    x1, y1, x2, y2 = b.rect
    draw.rounded_rectangle(b.rect, radius=16, fill=b.fill, outline=b.border, width=3)
    header_h = 42
    head_fill = (max(0, b.fill[0] - 22), max(0, b.fill[1] - 22), max(0, b.fill[2] - 22))
    draw.rounded_rectangle((x1, y1, x2, y1 + header_h), radius=16, fill=head_fill, outline=b.border, width=3)
    draw.rectangle((x1, y1 + header_h - 14, x2, y1 + header_h), fill=head_fill, outline=head_fill)
    draw.text((x1 + 12, y1 + 10), b.title, fill=(18, 32, 55), font=title_font)

    cy = y1 + header_h + 10
    for line in b.lines:
        draw.text((x1 + 12, cy), line, fill=(22, 40, 68), font=body_font)
        cy += 21


def _arrow_head(draw: ImageDraw.ImageDraw, a: tuple[int, int], b: tuple[int, int], color: tuple[int, int, int]) -> None:
    ax, ay = a
    bx, by = b
    dx = bx - ax
    dy = by - ay
    length = max((dx * dx + dy * dy) ** 0.5, 1.0)
    ux = dx / length
    uy = dy / length
    px, py = -uy, ux
    head = 14
    wing = 8
    p1 = (bx, by)
    p2 = (int(bx - ux * head + px * wing), int(by - uy * head + py * wing))
    p3 = (int(bx - ux * head - px * wing), int(by - uy * head - py * wing))
    draw.polygon([p1, p2, p3], fill=color)


def _poly_arrow(
    draw: ImageDraw.ImageDraw,
    points: Sequence[tuple[int, int]],
    color: tuple[int, int, int] = (45, 86, 147),
    width: int = 4,
    label: str | None = None,
    label_font: ImageFont.ImageFont | None = None,
) -> None:
    if len(points) < 2:
        return
    draw.line(list(points), fill=color, width=width, joint="curve")
    _arrow_head(draw, points[-2], points[-1], color)

    if label and label_font:
        mid = len(points) // 2
        mx, my = points[mid]
        tw = int(draw.textlength(label, font=label_font))
        pad = 6
        draw.rounded_rectangle((mx - tw // 2 - pad, my - 14, mx + tw // 2 + pad, my + 10), radius=8, fill=(255, 255, 255))
        draw.text((mx - tw // 2, my - 11), label, fill=(22, 47, 86), font=label_font)


def build_diagram() -> None:
    DOCS_DIR.mkdir(parents=True, exist_ok=True)
    img = Image.new("RGB", (WIDTH, HEIGHT), "white")
    draw = ImageDraw.Draw(img)
    _background(draw)

    title_font = _load_font(42, bold=True)
    sub_font = _load_font(22)
    panel_font = _load_font(24, bold=True)
    box_title_font = _load_font(20, bold=True)
    box_body_font = _load_font(16)
    arrow_font = _load_font(15, bold=True)
    note_font = _load_font(17)

    draw.text((40, 20), "Car Vision RAG - High Level Architecture (Clean View)", fill=(18, 37, 73), font=title_font)
    draw.text(
        (40, 72),
        "Layout has separated Predict flow, Chat flow, and KB build pipeline to avoid arrow overlap.",
        fill=(57, 82, 120),
        font=sub_font,
    )

    runtime_panel = (40, 120, 2560, 980)
    kb_panel = (40, 1020, 1750, 1580)
    infra_panel = (1790, 1020, 2560, 1580)
    _panel(draw, runtime_panel, "A) Runtime Flows", panel_font)
    _panel(draw, kb_panel, "B) Knowledge Build Pipeline", panel_font)
    _panel(draw, infra_panel, "C) Infra, Config, Storage", panel_font)

    # Predict row
    p_ui = Box(90, 220, 270, 140, "UI Upload", ["index.html + app.js", "chon anh va submit"], (223, 240, 255))
    p_api = Box(400, 220, 300, 170, "/predict API", ["routes.py", "save upload", "run analyze_car_image"], (223, 240, 255))
    p_an = Box(740, 200, 360, 210, "Analyzer", ["detect -> crop -> classify", "structured KB + pdf KB", "set last_prediction"], (232, 245, 232))
    p_rt = Box(1140, 220, 330, 170, "Retriever", ["retrieve_pdf_knowledge()", "filter by body_type", "fallback vehicle_template"], (255, 241, 225))
    p_qd = Box(1510, 220, 330, 170, "Qdrant", ["collection: car_pdf_kb", "vector search + top-k"], (255, 241, 225))
    p_rsp = Box(1880, 220, 300, 170, "Predict Response", ["JSON: detection +", "classification + KB"], (223, 240, 255))
    p_view = Box(2220, 220, 290, 140, "UI Render", ["hien ket qua va", "ngu canh chat"], (223, 240, 255))

    # Chat row
    c_ui = Box(90, 560, 270, 140, "UI Chat", ["nhap cau hoi", "gui /chat"], (223, 240, 255))
    c_api = Box(400, 540, 300, 170, "/chat API", ["chat_routes.py", "run_in_threadpool"], (223, 240, 255))
    c_chat = Box(740, 520, 360, 210, "Chat Service", ["intent classification", "get last prediction", "build fallback answer"], (232, 245, 232))
    c_rt = Box(1140, 540, 330, 170, "Retriever", ["vehicle/company context", "Qdrant query"], (255, 241, 225))
    c_qd = Box(1510, 540, 330, 170, "Qdrant", ["return top-k docs"], (255, 241, 225))
    c_llm = Box(1880, 520, 300, 210, "LLM (Gemini)", ["llm.py", "build prompts", "generateContent"], (232, 245, 232))
    c_gm = Box(2220, 560, 290, 140, "Gemini API", ["gemini-2.5-flash", "return final text"], (238, 234, 255))

    # Runtime shared note
    c_out = Box(740, 790, 560, 130, "Chat Output", ["answer + sources + generation metadata -> UI"], (223, 240, 255))

    runtime_boxes = [p_ui, p_api, p_an, p_rt, p_qd, p_rsp, p_view, c_ui, c_api, c_chat, c_rt, c_qd, c_llm, c_gm, c_out]
    for b in runtime_boxes:
        _box(draw, b, box_title_font, box_body_font)

    # Predict arrows (single row, left -> right)
    _poly_arrow(draw, [p_ui.right, p_api.left], label="1", label_font=arrow_font)
    _poly_arrow(draw, [p_api.right, p_an.left], label="2", label_font=arrow_font)
    _poly_arrow(draw, [p_an.right, p_rt.left], label="3", label_font=arrow_font)
    _poly_arrow(draw, [p_rt.right, p_qd.left], label="4", label_font=arrow_font)
    _poly_arrow(draw, [p_qd.right, p_rsp.left], label="5", label_font=arrow_font)
    _poly_arrow(draw, [p_rsp.right, p_view.left], label="6", label_font=arrow_font)

    # Chat arrows (single row + return path)
    _poly_arrow(draw, [c_ui.right, c_api.left], label="1", label_font=arrow_font)
    _poly_arrow(draw, [c_api.right, c_chat.left], label="2", label_font=arrow_font)
    _poly_arrow(draw, [c_chat.right, c_rt.left], label="3", label_font=arrow_font)
    _poly_arrow(draw, [c_rt.right, c_qd.left], label="4", label_font=arrow_font)
    _poly_arrow(draw, [c_qd.right, c_llm.left], label="5", label_font=arrow_font)
    _poly_arrow(
        draw,
        [c_llm.right, (c_llm.right[0] + 20, c_llm.right[1] - 18), c_gm.left],
        label="6",
        label_font=arrow_font,
    )
    _poly_arrow(
        draw,
        [c_gm.left, (c_gm.left[0] - 20, c_gm.left[1] + 18), c_llm.right],
        label="7",
        label_font=arrow_font,
    )
    _poly_arrow(
        draw,
        [c_llm.bottom, (c_llm.bottom[0], 760), (c_out.top[0], 760), c_out.top],
        label="8",
        label_font=arrow_font,
    )
    _poly_arrow(
        draw,
        [c_out.bottom, (c_out.bottom[0], 950), (c_chat.bottom[0], 950), c_chat.bottom],
        label="9",
        label_font=arrow_font,
    )

    # KB build panel
    kb_pdf = Box(90, 1120, 320, 150, "PDF Sources", ["data/kb/pdfs", "01..10 docs"], (255, 241, 225))
    kb_ing = Box(470, 1110, 350, 170, "ingest_pdfs.py", ["extract text", "chunk + metadata", "output pdf_chunks.json"], (255, 241, 225))
    kb_json = Box(880, 1130, 320, 140, "pdf_chunks.json", ["data/kb/pdf_chunks.json"], (255, 241, 225))
    kb_idx = Box(1260, 1110, 350, 170, "index_pdf_chunks.py", ["reset collection", "embed + add to Qdrant"], (255, 241, 225))

    for b in [kb_pdf, kb_ing, kb_json, kb_idx]:
        _box(draw, b, box_title_font, box_body_font)

    _poly_arrow(draw, [kb_pdf.right, kb_ing.left], label="A1", label_font=arrow_font)
    _poly_arrow(draw, [kb_ing.right, kb_json.left], label="A2", label_font=arrow_font)
    _poly_arrow(draw, [kb_json.right, kb_idx.left], label="A3", label_font=arrow_font)
    _poly_arrow(
        draw,
        [kb_idx.right, (1750, kb_idx.right[1]), (1750, p_qd.bottom[1] + 10), p_qd.bottom],
        label="A4 index",
        label_font=arrow_font,
    )

    # Infra panel
    inf_model = Box(1840, 1120, 300, 180, "Model Files", ["yolo11n.pt", "classifier .pth", "body_type_classes.json"], (238, 234, 255))
    inf_cfg = Box(2180, 1120, 330, 180, "Config & Env", ["app/core/config.py", ".env (.API_KEY, limits)", "Gemini settings"], (238, 234, 255))
    inf_data = Box(1840, 1330, 670, 180, "Runtime Data", ["uploads/original + crop", "qdrant_local/storage.sqlite", "session_store last_prediction"], (238, 234, 255))
    for b in [inf_model, inf_cfg, inf_data]:
        _box(draw, b, box_title_font, box_body_font)

    draw.text((1848, 1532), "Used by Analyzer, API, Retriever, and LLM at runtime.", fill=(42, 69, 108), font=note_font)

    draw.rounded_rectangle((40, 1535, 2560, 1610), radius=12, fill=(246, 250, 255), outline=(174, 196, 227), width=2)
    draw.text(
        (58, 1558),
        "Tip: khi re-index ma gap lock 'already accessed by another instance', hay tat app dang chay truoc khi chay index_pdf_chunks.py",
        fill=(41, 65, 104),
        font=note_font,
    )

    img.save(OUTPUT_PNG, "PNG")
    print(f"Created diagram: {OUTPUT_PNG}")


if __name__ == "__main__":
    build_diagram()
