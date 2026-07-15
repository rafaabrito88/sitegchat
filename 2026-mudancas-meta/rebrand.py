# -*- coding: utf-8 -*-
"""Rebrand original.html (waba.zdg.com.br) -> index.html com identidade Grupo GTI / G-Chat."""
import base64
import re

with open("original.html", encoding="utf-8") as f:
    html = f.read()

# ---------- 1. Logos (base64) ----------
with open("assets/logo-gti-gchat.png", "rb") as f:
    big_logo = base64.b64encode(f.read()).decode()
with open("logo-gti-256x256.png", "rb") as f:
    icon_logo = base64.b64encode(f.read()).decode()

# logotipo grande Z-PRO (481x186) -> logo G-Chat (mesmas dimensões)
n_big = len(re.findall(r'iVBORw0KGgoAAAANSUhEUgAAAeEAAAC6[A-Za-z0-9+/=]+', html))
html = re.sub(r'iVBORw0KGgoAAAANSUhEUgAAAeEAAAC6[A-Za-z0-9+/=]+', big_logo, html)

# ícone quadrado Z-PRO (128x128, favicon + avatar dos chats) -> ícone GTI 256
n_icon = len(re.findall(r'iVBORw0KGgoAAAANSUhEUgAAAIAAAACAC[A-Za-z0-9+/=]+', html))
html = re.sub(r'iVBORw0KGgoAAAANSUhEUgAAAIAAAACAC[A-Za-z0-9+/=]+', icon_logo, html)

# ---------- 2. Paleta: verde -> laranja GTI (#f58634), mantendo luminosidade ----------
hex_map = {
    "#081109": "#0F0B07",   # --ink (fundo principal)
    "#0C1A0F": "#181109",   # --ink2
    "#0F2114": "#1F150B",   # --panel
    "#040805": "#070503",   # body bg
    "#06130a": "#110C06",
    "#0A150D": "#150F08",
    "#0E3B22": "#3B2410",   # bolha "enviada" escura
    "#16241A": "#241B12",
    "#EAF6EC": "#F6F0EA",   # --paper
    "#DDF5E4": "#F5EADD",
    "#B9D6C2": "#D6C9B9",
    "#8AA893": "#A89A8A",   # --dim
    "#FDFFFE": "#FFFEFD",
    "#128C4B": "#C2600F",   # --green-deep -> laranja profundo
    "#25D366": "#F58634",   # --green -> laranja GTI
}
for old, new in hex_map.items():
    html = re.sub(re.escape(old), new, html, flags=re.IGNORECASE)

# WhatsApp glyph (SVG na última tela) volta a ser verde oficial do WhatsApp
html = html.replace('<path fill="#F58634" d="M380.9 97.1', '<path fill="#25D366" d="M380.9 97.1')

rgba_map = {
    "rgba(37,211,102":  "rgba(245,134,52",   # glow verde -> laranja
    "rgba(214,255,226": "rgba(255,232,214",  # linhas esverdeadas -> tom quente
    "rgba(6,12,8":      "rgba(12,9,6",
    "rgba(12,26,15":    "rgba(24,17,9",
}
for old, new in rgba_map.items():
    html = html.replace(old, new)

# ---------- 3. Textos e marca ----------
html = html.replace('alt="Z-PRO Multiatendimento"', 'alt="G-Chat · Grupo GTI"')
html = html.replace('alt="Z-PRO"', 'alt="G-Chat"')
html = html.replace("Z-PRO", "G-Chat")

html = html.replace("var QR_URL='https://www.youtube.com/@ComunidadeZDG';",
                    "var QR_URL='https://gchat.gtigrupo.com.br';")
html = html.replace("var SHARE_URL='https://waba.zdg.com.br';",
                    "var SHARE_URL='https://gchat.gtigrupo.com.br';")

# PDF: caminho relativo (funciona local e hospedado em subpasta)
html = html.replace('href="/checklist-meta-2026.pdf"', 'href="checklist-meta-2026.pdf"')

# título da aba com a marca
html = html.replace("<title>Meta vai cobrar toda mensagem · WhatsApp API 2026</title>",
                    "<title>Meta vai cobrar toda mensagem · WhatsApp API 2026 · G-Chat | Grupo GTI</title>")

with open("index.html", "w", encoding="utf-8") as f:
    f.write(html)

leftover = re.findall(r'(?i)z-?pro|zdg|comunidade', html)
# classes CSS internas (.zpro-logo, .zdg etc.) não são visíveis; conta só p/ conferência
print("big logo slots:", n_big, "| icon slots:", n_icon)
print("identificadores internos restantes (não visíveis):", sorted(set(leftover)))
print("bytes:", len(html))
