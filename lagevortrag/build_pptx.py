"""Erzeugt die PPTX-Fassung des Lagevortrags 07.11.2026, 08:00 Uhr (Inhalt = HTML-Fassung).
Aufruf: python3 lagevortrag/build_pptx.py"""
from pathlib import Path
from pptx import Presentation
from pptx.util import Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE, MSO_CONNECTOR
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.dml import MSO_LINE_DASH_STYLE

OUT = Path(__file__).with_name("2026-11-07_0800_Lagevortrag_FueSt_HiOrg.pptx")
PX = 9525  # 1 px (bei 1280x720) in EMU
ROT, GRUEN, GELB, BLAU = RGBColor(0xC8, 0x10, 0x2E), RGBColor(0x2E, 0x7D, 0x32), RGBColor(0xE6, 0xA1, 0), RGBColor(0x1B, 0x3C, 0x8F)
SCHWARZ, GRAU, HELL, WEISS = RGBColor(0x11, 0x11, 0x11), RGBColor(0x99, 0x99, 0x99), RGBColor(0xEE, 0xEE, 0xEE), RGBColor(0xFF, 0xFF, 0xFF)
FONT = "Arial"

prs = Presentation()
prs.slide_width, prs.slide_height = Emu(1280 * PX), Emu(720 * PX)
LEER = prs.slide_layouts[6]


def p(v):
    return Emu(int(v * PX))


def text(slide, x, y, w, h, runs, size=24, color=SCHWARZ, bold=False, align=PP_ALIGN.LEFT, anchor=MSO_ANCHOR.TOP, italic=False):
    """runs: str oder Liste von Absätzen; Absatz = str oder Liste (text, fett)-Tupel; '• ' am Anfang = Aufzählung."""
    tb = slide.shapes.add_textbox(p(x), p(y), p(w), p(h))
    tf = tb.text_frame
    tf.word_wrap = True
    tf.vertical_anchor = anchor
    for m in ("margin_left", "margin_right", "margin_top", "margin_bottom"):
        setattr(tf, m, 0)
    for i, para in enumerate([runs] if isinstance(runs, str) else runs):
        par = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        par.alignment = align
        teile = [(para, bold)] if isinstance(para, str) else para
        for t, fett in teile:
            r = par.add_run()
            r.text = t
            f = r.font
            f.name, f.size, f.bold, f.italic = FONT, Pt(size * 0.75), fett, italic
            f.color.rgb = color
    return tb


def rect(slide, x, y, w, h, fill, line=None, lw=3, dash=False, shape=MSO_SHAPE.RECTANGLE):
    s = slide.shapes.add_shape(shape, p(x), p(y), p(w), p(h))
    s.shadow.inherit = False
    if fill is None:
        s.fill.background()
    else:
        s.fill.solid()
        s.fill.fore_color.rgb = fill
    if line is None:
        s.line.fill.background()
    else:
        s.line.color.rgb = line
        s.line.width = p(lw)
        if dash:
            s.line.dash_style = MSO_LINE_DASH_STYLE.DASH
    return s


def linie(slide, x1, y1, x2, y2, color=SCHWARZ, dash=False):
    c = slide.shapes.add_connector(MSO_CONNECTOR.STRAIGHT, p(x1), p(y1), p(x2), p(y2))
    c.line.color.rgb = color
    c.line.width = p(3)
    if dash:
        c.line.dash_style = MSO_LINE_DASH_STYLE.DASH


def rahmen(titel, rechts, nr, fuss="Lagevortrag zur Eröffnung der Stabsarbeit"):
    s = prs.slides.add_slide(LEER)
    text(s, 56, 36, 800, 56, titel, size=40, bold=True)
    text(s, 700, 56, 524, 30, rechts, size=20, color=RGBColor(0x55, 0x55, 0x55), align=PP_ALIGN.RIGHT)
    rect(s, 56, 95, 1168, 4, ROT)
    text(s, 56, 684, 700, 22, fuss, size=15, color=RGBColor(0x77, 0x77, 0x77))
    text(s, 1100, 684, 124, 22, f"{nr} / 5", size=15, color=RGBColor(0x77, 0x77, 0x77), align=PP_ALIGN.RIGHT)
    return s


def karte(s, x, y, w, h, farbe, titel, kern, punkte, kern_farbe=SCHWARZ):
    rect(s, x, y, w, h, RGBColor(0xF4, 0xF4, 0xF4))
    rect(s, x, y, 8, h, farbe)
    absaetze = ([[(titel, True)]] if titel else []) + ([[(kern, True)]] if kern else []) + [(pk if pk[0][0].startswith("→") else [("•  ", False)] + pk) if isinstance(pk, list) else [("•  " + pk, False)] for pk in punkte]
    tb = text(s, x + 30, y + 16, w - 52, h - 28, absaetze, size=24)
    pars = tb.text_frame.paragraphs
    i = 0
    if titel:
        pars[0].runs[0].font.size = Pt(26 * 0.75)
        i = 1
    if kern:
        pars[i].runs[0].font.size = Pt(28 * 0.75)
        pars[i].runs[0].font.color.rgb = kern_farbe
    for par in pars[1:]:
        par.space_before = Pt(4)


# --- Folie 1: Wetter ---
KOPF = "Sa 07.11.2026 · 08:00 Uhr · FüSt HiOrg"
s = rahmen("Wetter", KOPF, 1)
karte(s, 56, 125, 1168, 300, ROT, "Heute, Samstag (DWD)", "trocken · Hochnebel · 4–8 °C", [
    [("morgens lokal ", False), ("Nebel", True), (", Sicht eingeschränkt", False)],
    [("früh örtlich ", False), ("leichter Frost", True), (" 0 bis −2 °C (Glätte)", False)],
    "Wind schwach aus O–SO",
    "nachmittags kaum Auflockerung",
    [("→ Kälteschutz für Patienten und Kräfte", True)],
])

# --- Folie 2: Friederikenstift ---
s = rahmen("Friederikenstift: Verkehr", KOPF, 2, fuss="Quelle: Übungsbefehl LHH, 1.6")
text(s, 56, 116, 1168, 30, [[("Calenberger Str. gesperrt", True), (" (Regelrettung) · Anlieferung ", False),
                            ("nur Haupteingang Humboldtstraße", True)]], size=22)
s.shapes[-1].text_frame.paragraphs[0].runs[0].font.color.rgb = ROT
s.shapes.add_picture(str(Path(__file__).with_name("Lageskizze_Friederikenstift.jpg")), p(160), p(158), width=p(960))

# --- Folie 3: Eigene Lage / Ausblick ---
s = rahmen("Eigene Lage · Ausblick", KOPF, 3)
karte(s, 56, 125, 570, 210, GRUEN, "BR Schützenplatz", "voraussichtlich eingerichtet", ["Meldekopf Schützenplatz"])
karte(s, 654, 125, 570, 210, GRUEN, "Verpflegung", "läuft (voraussichtlich)", [
    "Lunchpakete JUH: FRW-1 ab 07:30, Schützenplatz ab 08:00",
])
karte(s, 56, 360, 1168, 110, BLAU, "Als Nächstes erwartet",
      "Einrichtung TEL Schadensraum → Befehl der TEL an FüSt HiOrg", [])

# --- Folie 4: Führungsorganisation (Koordinaten wie SVG der HTML-Fassung, Versatz 56/125) ---
s = rahmen("Führungsorganisation", "Stand 08:00 Uhr", 4, fuss="grau gestrichelt = noch nicht eingerichtet")
OX, OY = 56, 125


def L(x1, y1, x2, y2, **kw):
    linie(s, OX + x1, OY + y1, OX + x2, OY + y2, **kw)


def kreis(cx, cy, r, grau=False, kappe=False, linienfarbe=None):
    if kappe:  # Führungskappe: schwarzer Kreisabschnitt oben (Sehne)
        rect(s, OX + cx - r, OY + cy - r, 2 * r, 2 * r, HELL if grau else WEISS, None, shape=MSO_SHAPE.OVAL)
        k = rect(s, OX + cx - r, OY + cy - r, 2 * r, 2 * r, RGBColor(0xBB, 0xBB, 0xBB) if grau else SCHWARZ, shape=MSO_SHAPE.CHORD)
        k.adjustments[0], k.adjustments[1] = 205 * 0.6, 335 * 0.6  # Grad (python-pptx: Wert/100000, OOXML: 60000stel Grad)
    c = rect(s, OX + cx - r, OY + cy - r, 2 * r, 2 * r, None if kappe else (HELL if grau else WEISS),
             linienfarbe or (GRAU if grau else SCHWARZ), dash=grau, shape=MSO_SHAPE.OVAL)
    return c


def kasten(x, y, w, h, z1, z2, grau=True):
    rect(s, OX + x, OY + y, w, h, HELL if grau else WEISS, GRAU if grau else SCHWARZ, dash=grau)
    farbe = GRAU if grau else SCHWARZ
    text(s, OX + x, OY + y + 14, w, 26, z1, size=20, bold=True, color=farbe, align=PP_ALIGN.CENTER)
    text(s, OX + x, OY + y + 40, w, 24, z2, size=18, color=farbe, align=PP_ALIGN.CENTER)


# Linien
L(584, 110, 584, 188); L(584, 312, 584, 350); L(646, 250, 716, 250); L(180, 350, 1000, 350)
L(180, 350, 180, 380, color=GRAU, dash=True); L(460, 350, 460, 374, color=GRAU, dash=True)
L(460, 466, 460, 486, color=GRAU, dash=True); L(730, 350, 730, 380, color=GRAU, dash=True)
L(1000, 350, 1000, 374)

# TEL
rect(s, OX + 474, OY + 20, 220, 90, WEISS, SCHWARZ)
rect(s, OX + 474, OY + 20, 220, 16, SCHWARZ)
text(s, OX + 474, OY + 44, 220, 34, "TEL", size=30, bold=True, align=PP_ALIGN.CENTER)
text(s, OX + 474, OY + 78, 220, 26, "Schadensraum", size=19, align=PP_ALIGN.CENTER)
text(s, OX + 710, OY + 52, 260, 24, "Einrichtung erwartet", size=18, color=BLAU, italic=True)

# FüSt HiOrg
rect(s, OX + 510, OY + 176, 148, 148, None, ROT, lw=5, shape=MSO_SHAPE.OVAL)
kreis(584, 250, 62, kappe=True)
text(s, OX + 522, OY + 236, 124, 30, "FüSt", size=26, bold=True, align=PP_ALIGN.CENTER)
text(s, OX + 522, OY + 268, 124, 26, "HiOrg", size=22, align=PP_ALIGN.CENTER)
text(s, OX + 240, OY + 238, 200, 26, "eigene Stelle", size=20, bold=True, color=ROT, align=PP_ALIGN.RIGHT)

# Fm BSt
kreis(756, 250, 40)
text(s, OX + 716, OY + 230, 80, 44, ["Fm", "BSt"], size=18, bold=True, align=PP_ALIGN.CENTER)

# unterstellt (grau = noch nicht da)
kasten(90, 380, 180, 78, "UEA", "Tellkampfschule")
kreis(460, 420, 46, grau=True, kappe=True)
text(s, OX + 414, OY + 404, 92, 44, ["Transp.", "Orga"], size=17, bold=True, color=GRAU, align=PP_ALIGN.CENTER)
kasten(370, 486, 180, 66, "UEA", "Patiententransport")
kasten(640, 380, 180, 78, "UEA", "Friederikenstift")

# BR Schützenplatz (aktiv): Meldekopf = Stelle, gelb, Fahrzeug + M
kreis(1000, 420, 46, linienfarbe=SCHWARZ)
s.shapes[-1].fill.solid(); s.shapes[-1].fill.fore_color.rgb = RGBColor(0xFF, 0xE6, 0x00)
text(s, OX + 970, OY + 384, 60, 32, "M", size=26, bold=True, align=PP_ALIGN.CENTER)
rect(s, OX + 976, OY + 420, 48, 20, WEISS, SCHWARZ, lw=2.5)
for rx in (987, 1013):
    rect(s, OX + rx - 5, OY + 441, 10, 10, WEISS, SCHWARZ, lw=2.5, shape=MSO_SHAPE.OVAL)
text(s, OX + 880, OY + 478, 240, 26, "BR Schützenplatz", size=20, bold=True, align=PP_ALIGN.CENTER)
text(s, OX + 880, OY + 504, 240, 24, "Meldekopf", size=18, align=PP_ALIGN.CENTER)

# --- Folie 5: Real ---
s = rahmen("Reale Einsätze haben Vorrang", KOPF, 5)
karte(s, 56, 140, 1168, 270, ROT, "", "„Real – Real – Real“", [
    [("Funkmeldung zu realen Lagen beginnt mit ", False), ("„Real – Real – Real“", True)],
    "Reale Einsatzfahrten haben immer Vorrang",
    "Übungsleitung ist weisungsbefugt",
    [("Notfälle: sofort Übungsleitung informieren, RTW über ", False), ("112", True)],
], kern_farbe=ROT)
k = s.shapes[-1].text_frame.paragraphs
k[0].runs[0].font.size = Pt(54 * 0.75)

prs.save(OUT)
print(OUT)
