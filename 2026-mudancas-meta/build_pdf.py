# -*- coding: utf-8 -*-
"""Réplica fiel do checklist-original.pdf (waba.zdg.com.br) com identidade Grupo GTI / G-Chat.

Extrai cada retângulo e cada trecho de texto do PDF original (posição, fonte,
tamanho, cor, espaçamento) e redesenha tudo idêntico, trocando apenas:
  - paleta verde -> laranja GTI
  - ZDG -> GTI / Comunidade ZDG -> Grupo GTI / Z-PRO -> G-Chat / YouTube -> site G-Chat
"""
import warnings
warnings.filterwarnings("ignore")

import pdfplumber
from reportlab.pdfgen import canvas
from reportlab.lib.colors import Color
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

SRC = "checklist-original.pdf"
OUT = "checklist-meta-2026.pdf"

# ---------- fontes (equivalentes nativas do Windows) ----------
pdfmetrics.registerFont(TTFont("Sans", r"C:\Windows\Fonts\segoeui.ttf"))
pdfmetrics.registerFont(TTFont("Sans-Bold", r"C:\Windows\Fonts\segoeuib.ttf"))
pdfmetrics.registerFont(TTFont("Mono", r"C:\Windows\Fonts\consola.ttf"))
pdfmetrics.registerFont(TTFont("Mono-Bold", r"C:\Windows\Fonts\consolab.ttf"))

FONT_MAP = {
    "Segoe-UI-Variable-Display": "Sans",
    "Segoe-UI-Variable-Display-Bold": "Sans-Bold",
    "CascadiaCodeRoman": "Mono",
    "CascadiaCodeRoman-Bold": "Mono-Bold",
}

# ---------- mapa de cores: verde ZDG -> laranja GTI ----------
def hx(h):
    h = h.lstrip("#")
    return tuple(round(int(h[i:i+2], 16) / 255, 4) for i in (0, 2, 4))

COLOR_MAP = {
    hx("25D366"): hx("F58634"),   # verde brand -> laranja GTI
    hx("128C4B"): hx("C2600F"),   # verde profundo -> laranja profundo
    hx("081109"): hx("0F0B07"),   # tinta escura esverdeada -> escura quente
    hx("DCE6DE"): hx("E6E0D8"),   # linhas claras esverdeadas -> quentes
    hx("EAF6EC"): hx("F6F0EA"),   # painel claro esverdeado -> creme
    hx("DDF5E4"): hx("F5EADD"),   # painel verde claro -> creme laranja
    hx("F0F7F1"): hx("F7F3F0"),
    hx("E7F0E9"): hx("F0EBE7"),
}

def snap(c):
    """Casa uma cor extraída com o mapa (tolerância p/ arredondamento)."""
    if c is None or isinstance(c, str):
        return None
    c = tuple(c) if not isinstance(c, (int, float)) else (c, c, c)
    if len(c) == 1:
        c = (c[0], c[0], c[0])
    for k, v in COLOR_MAP.items():
        if max(abs(a - b) for a, b in zip(c, k)) < 0.02:
            return v
    return c

# ---------- substituições de marca ----------
def rebrand(t):
    t = t.replace("youtube.com/@ComunidadeZDG", "gchat.gtigrupo.com.br")
    t = t.replace("Comunidade ZDG", "Grupo GTI")
    t = t.replace("Z-PRO", "G-Chat")
    t = t.replace("ZDG", "GTI")
    return t

# ---------- extração ----------
pdf = pdfplumber.open(SRC)
page = pdf.pages[0]
W, PH = page.width, page.height

rects = []
for r in page.rects:
    rects.append({
        "x0": r["x0"], "y0": PH - r["bottom"], "w": r["x1"] - r["x0"],
        "h": r["bottom"] - r["top"],
        "fill": r["non_stroking_color"], "stroke": r["stroking_color"],
        "filled": r["fill"], "stroked": r["stroke"],
    })

# agrupa chars consecutivos em runs (mesma linha/fonte/tamanho/cor)
runs = []
cur = None
for ch in page.chars:
    base = ch["matrix"][5]
    key = (ch["fontname"].split("+")[1], round(ch["size"], 2),
           tuple(ch["non_stroking_color"] or ()), round(base, 1))
    if cur and cur["key"] == key and ch["x0"] - cur["x1"] < ch["size"] * 1.8:
        cur["text"] += ch["text"]
        cur["x1"] = ch["x1"]
    else:
        if cur:
            runs.append(cur)
        cur = {"key": key, "text": ch["text"], "x0": ch["x0"], "x1": ch["x1"],
               "y": base, "font": key[0], "size": ch["size"],
               "color": ch["non_stroking_color"]}
if cur:
    runs.append(cur)

# ---------- desenho ----------
c = canvas.Canvas(OUT, pagesize=(W, PH))

unmapped = set()

for r in rects:
    fill = snap(r["fill"])
    stroke = snap(r["stroke"])
    if r["fill"] == "P4" or r["stroke"] == "P4":
        # faixa do cabeçalho: gradiente diagonal escuro (verde -> tom quente)
        c.saveState()
        p = c.beginPath()
        p.rect(r["x0"], r["y0"], r["w"], r["h"])
        c.clipPath(p, stroke=0, fill=0)
        c.linearGradient(r["x0"], r["y0"] + r["h"], r["x0"] + r["w"], r["y0"],
                         (Color(*hx("0F0B07")), Color(*hx("291B0F"))),
                         (0, 1), extend=True)
        c.restoreState()
        continue
    if r["filled"] and fill:
        c.setFillColor(Color(*fill))
    if r["stroked"] and stroke:
        c.setStrokeColor(Color(*stroke))
        c.setLineWidth(1.0)
    c.rect(r["x0"], r["y0"], r["w"], r["h"],
           fill=1 if (r["filled"] and fill) else 0,
           stroke=1 if (r["stroked"] and stroke) else 0)

for run in runs:
    font = FONT_MAP.get(run["font"])
    if not font:
        unmapped.add(run["font"])
        continue
    size = run["size"]
    color = snap(run["color"]) or (0, 0, 0)
    c.setFillColor(Color(*color))
    c.setFont(font, size)
    text = rebrand(run["text"])
    span = run["x1"] - run["x0"]
    natural = pdfmetrics.stringWidth(text, font, size)
    if text != run["text"]:
        # texto trocado: largura muda -> ancora à direita se o run era do lado direito
        if run["x0"] > W * 0.55:
            c.drawString(run["x1"] - natural, run["y"], text)
        elif run["text"] == "ZDG":
            # badge do cabeçalho: centraliza no mesmo centro do original
            cx = (run["x0"] + run["x1"]) / 2
            c.drawString(cx - natural / 2, run["y"], text)
        else:
            c.drawString(run["x0"], run["y"], text)
    else:
        # preserva letter-spacing/largura original do run
        cs = (span - natural) / (len(text) - 1) if len(text) > 1 else 0
        if abs(cs) < 0.02:
            cs = 0
        c.drawString(run["x0"], run["y"], text, charSpace=cs)

c.showPage()
c.save()
if unmapped:
    print("fontes sem mapa:", unmapped)
print("runs:", len(runs), "| rects:", len(rects))
print("ok ->", OUT)
