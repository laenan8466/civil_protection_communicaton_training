#!/usr/bin/env python3
"""Erzeugt aus config/, nachrichten/ und einsaetze/ die Übungsunterlagen in ausgabe/.

Teil 1 – Nachrichtenpool Stab (nachrichten/):
- Vordrucke (weißes Blatt, A5) für Nachrichten, die an der TEL (Papier) entstehen
- EDP-Blätter (A4, 1 Nachricht/Seite) für Nachrichten, die an einer FüSt (EDP) entstehen
- Übersicht für die Übungsleitung

Teil 2 – Einsätze in EDP anlegen (einsaetze/):
- A4-Blatt je Einsatz (Funk + Übungsleitung) mit Rückmeldungen, Lösung, Uhrzeiten, Feedback
- dieselben Einsätze als Vordrucke (gebündelt je Einsatz)
- Übersicht für die Übungsleitung

Aufruf: python3 generator/build.py [--nur-pruefen]
"""
import argparse
import csv
import shutil
import subprocess
import sys
from collections import Counter
from pathlib import Path

import yaml
from jinja2 import Environment, FileSystemLoader, StrictUndefined

ROOT = Path(__file__).resolve().parent.parent
CONFIG = ROOT / "config" / "stellen.yaml"
NACHRICHTEN = ROOT / "nachrichten"
EINSAETZE = ROOT / "einsaetze"
ANHAENGE = ROOT / "anhaenge"
TEMPLATES = ROOT / "generator" / "templates"
ASSETS = ROOT / "assets"
BUILD = ROOT / "build"
AUSGABE = ROOT / "ausgabe"

CHROMIUM_KANDIDATEN = [
    "/opt/pw-browsers/chromium-1243/chrome-linux64/chrome",
    "chromium",
    "chromium-browser",
    "google-chrome",
]

# Vordruck: 14 Linien à ca. 68 Zeichen (Liberation Sans 3,3 mm, fett)
VORDRUCK_ZEILEN = 14
VORDRUCK_ZEICHEN = 68

PFLICHT = ["nr", "kategorie", "von", "von_funktion", "an", "an_funktion",
           "medium", "vorrang", "betreff_art", "betreff", "text"]


RUFNAMEN = {"Joh.": "Johannes", "Akk.": "Akkon"}
REGIONEN = {"H": "Hannover", "H#": "Hannover Land"}


def sprechweise(rufname):
    """'Joh. H# 57-96-1' -> 'Johannes Hannover Land 57-96-1'"""
    name, region, nummer = rufname.rsplit(" ", 2)
    return f"{RUFNAMEN.get(name, name)} {REGIONEN.get(region, region)} {nummer}"


def lade_config():
    return yaml.safe_load(CONFIG.read_text(encoding="utf-8"))


def lade_nachrichten():
    nachrichten = []
    for pfad in sorted(NACHRICHTEN.glob("*.yaml")):
        n = yaml.safe_load(pfad.read_text(encoding="utf-8"))
        n["_datei"] = pfad.name
        n.setdefault("zur_info", [])
        n.setdefault("anhaenge", [])
        n.setdefault("bezug", None)
        n.setdefault("zeichen", "")
        n.setdefault("notiz", "")
        n["text"] = n.get("text", "").rstrip()
        # an: eine Stelle oder Liste von Stellen (Sammelruf)
        n["an_liste"] = n["an"] if isinstance(n.get("an"), list) else [n.get("an")]
        nachrichten.append(n)
    return sorted(nachrichten, key=lambda n: n["nr"])


def pruefe(cfg, nachrichten):
    fehler = []
    stellen = cfg["stellen"]
    nummern = Counter(n.get("nr") for n in nachrichten)
    for nr, anzahl in nummern.items():
        if anzahl > 1:
            fehler.append(f"Nr. {nr} mehrfach vergeben")
    for n in nachrichten:
        ort = f"{n['_datei']}:"
        for feld in PFLICHT:
            if not n.get(feld):
                fehler.append(f"{ort} Pflichtfeld '{feld}' fehlt")
        if fehler and fehler[-1].startswith(ort):
            continue
        if n["von"] not in stellen:
            fehler.append(f"{ort} unbekannte Stelle von='{n['von']}'")
            continue
        unbekannt = [a for a in n["an_liste"] if a not in stellen]
        if unbekannt:
            fehler.append(f"{ort} unbekannte Stelle an={unbekannt}")
            continue
        if n["von"] in n["an_liste"]:
            fehler.append(f"{ort} von und an sind gleich")
        if n["von_funktion"] not in stellen[n["von"]]["funktionen"]:
            fehler.append(f"{ort} Funktion '{n['von_funktion']}' gibt es bei {n['von']} nicht")
        for a in n["an_liste"]:
            for f in [n["an_funktion"], *n["zur_info"]]:
                if f not in stellen[a]["funktionen"]:
                    fehler.append(f"{ort} Funktion '{f}' gibt es bei {a} nicht")
        if n["medium"] not in cfg["medien"]:
            fehler.append(f"{ort} unbekanntes Medium '{n['medium']}'")
        if n["vorrang"] not in cfg["vorrang"]:
            fehler.append(f"{ort} unbekannte Vorrangstufe '{n['vorrang']}'")
        if n["betreff_art"] not in cfg["betreff_arten"]:
            fehler.append(f"{ort} unbekannte Betreff-Art '{n['betreff_art']}'")
        if n["kategorie"] not in cfg["kategorien"]:
            fehler.append(f"{ort} unbekannte Kategorie '{n['kategorie']}'")
        if n["bezug"] is not None and n["bezug"] not in nummern:
            fehler.append(f"{ort} Bezug auf unbekannte Nr. {n['bezug']}")
        if stellen[n["von"]]["arbeitsmittel"] == "vordruck":
            zeilen = sum(max(1, -(-len(z) // VORDRUCK_ZEICHEN)) for z in n["text"].splitlines())
            if zeilen > VORDRUCK_ZEILEN:
                fehler.append(f"{ort} Text zu lang für Vordruck (ca. {zeilen} von {VORDRUCK_ZEILEN} Zeilen)")
        for a in n["anhaenge"]:
            if not (ANHAENGE / a).is_file():
                fehler.append(f"{ort} Anhang '{a}' fehlt in anhaenge/")
    return fehler


def lade_einsaetze():
    einsaetze = []
    for pfad in sorted(EINSAETZE.glob("*.yaml")):
        e = yaml.safe_load(pfad.read_text(encoding="utf-8"))
        e["_datei"] = pfad.name
        einsaetze.append(e)
    return sorted(einsaetze, key=lambda e: e["nr"])


def pruefe_einsaetze(cfg, einsaetze):
    fehler = []
    ec = cfg["einsaetze"]
    tel_funktionen = next(s["funktionen"] for s in cfg["stellen"].values() if s["arbeitsmittel"] == "vordruck")
    fahrzeuge = {f["rufname"] for f in cfg["fahrzeuge"]}
    nummern = Counter(e.get("nr") for e in einsaetze)
    fehler += [f"Einsatz Nr. {nr} mehrfach vergeben" for nr, a in nummern.items() if a > 1]
    for e in einsaetze:
        ort = f"{e['_datei']}:"
        if e.get("bereich") not in ec["empfaenger"]:
            fehler.append(f"{ort} unbekannter Bereich '{e.get('bereich')}'")
        if e.get("schwierigkeit") not in ec["schwierigkeiten"]:
            fehler.append(f"{ort} unbekannte Schwierigkeit '{e.get('schwierigkeit')}'")
        m = e.get("meldung") or {}
        for feld in ("von_funktion", "medium", "vorrang", "betreff", "text"):
            if not m.get(feld):
                fehler.append(f"{ort} meldung.{feld} fehlt")
        if m.get("von_funktion") and m["von_funktion"] not in tel_funktionen:
            fehler.append(f"{ort} Funktion '{m['von_funktion']}' gibt es bei der TEL nicht")
        rms = e.get("rueckmeldungen") or []
        if not 1 <= len(rms) <= 2:
            fehler.append(f"{ort} 1–2 Rückmeldungen erwartet, gefunden {len(rms)}")
        for i, r in enumerate(rms, 1):
            if r.get("von") not in fahrzeuge:
                fehler.append(f"{ort} Rückmeldung {i}: '{r.get('von')}' fehlt in config fahrzeuge")
            if not r.get("text"):
                fehler.append(f"{ort} Rückmeldung {i}: Text fehlt")
        for i, x in enumerate([m, *rms]):
            if x.get("medium", "Funk") not in cfg["medien"]:
                fehler.append(f"{ort} unbekanntes Medium '{x.get('medium')}'")
            if x.get("vorrang", "normal") not in cfg["vorrang"]:
                fehler.append(f"{ort} unbekannte Vorrangstufe '{x.get('vorrang')}'")
            zeilen = sum(max(1, -(-len(z) // VORDRUCK_ZEICHEN)) for z in x.get("text", "").splitlines())
            if zeilen > VORDRUCK_ZEILEN:
                fehler.append(f"{ort} Meldung {i}: Text zu lang für Vordruck (ca. {zeilen} Zeilen)")
        for feld in ("stichwort", "ort", "patient", "ziel", "hinweise"):
            if feld not in (e.get("loesung") or {}):
                fehler.append(f"{ort} loesung.{feld} fehlt")
    return fehler


def aufbereiten_einsaetze(cfg, einsaetze):
    ec = cfg["einsaetze"]
    for e in einsaetze:
        e["id"] = f"E{e['nr']:02d}"
        e["stufe"] = ec["schwierigkeiten"][e["schwierigkeit"]]["stufe"]
        e["punkte"] = "●" * e["stufe"] + "○" * (3 - e["stufe"])
        e["empfaenger"] = ec["empfaenger"][e["bereich"]]
        e["bereich_name"] = ec["bereiche"][e["bereich"]]
        m = e["meldung"]
        e["meldungen"] = [{"titel": "Auftrag", "von_rufname": ec["absender"]["rufname"],
                           "von_name": ec["absender"]["name"], "von_funktion": m["von_funktion"],
                           "medium": m["medium"], "vorrang": m["vorrang"], "betreff": m["betreff"],
                           "zeichen": m.get("zeichen", ""), "text": m["text"].rstrip()}]
        for i, r in enumerate(e["rueckmeldungen"], 1):
            e["meldungen"].append({"titel": f"Rückmeldung {i}", "von_rufname": r["von"], "von_name": r["von"],
                                   "von_funktion": r.get("funktion", "Fahrzeugführer"),
                                   "medium": r.get("medium", "Funk"), "vorrang": r.get("vorrang", "normal"),
                                   "betreff": "", "zeichen": r.get("zeichen", ""), "text": r["text"].rstrip()})
        e["feedback_linien"] = 12 if len(e["meldungen"]) == 2 else 7


def einsatz_vordrucke(cfg, e):
    """Pseudo-Nachrichten für vordruck.html: Auftrag + Rückmeldungen."""
    ec = cfg["einsaetze"]
    seiten = []
    gesamt = len(e["meldungen"])
    for i, m in enumerate(e["meldungen"], 1):
        abs_name = f"{m['von_name']} {m['von_rufname']}" if m["von_name"] != m["von_rufname"] else m["von_rufname"]
        seiten.append({
            "nr_str": f"{e['id']}_{i}",
            "medium": m["medium"], "vorrang": m["vorrang"], "text": m["text"],
            "an_stelle": {"name": e["empfaenger"]},
            "rufnummer": {"Telefon": ec["telefon"], "Mail": ec["mail"]}.get(m["medium"], ""),
            "von_stelle": {"name": abs_name}, "von_funktion": m["von_funktion"], "zeichen": m["zeichen"],
            "an_funktion": "", "zur_info": [],
            "fuss": (f"<b>Einsatz {e['id']}</b> · {m['titel']} ({i}/{gesamt}) · "
                     f"<b>Stufe {e['stufe']} {e['schwierigkeit']} {e['punkte']}</b> · {e['bereich_name']}"),
        })
    return seiten


def statistik_einsaetze(cfg, einsaetze):
    zeilen = [f"{len(einsaetze)} Einsätze, {sum(len(e['rueckmeldungen']) for e in einsaetze)} Rückmeldungen"]
    for b, name in cfg["einsaetze"]["bereiche"].items():
        st = Counter(e["schwierigkeit"] for e in einsaetze if e["bereich"] == b)
        zeilen.append(f"  {name:<22} " + ", ".join(f"{k} {st.get(k, 0)}" for k in cfg["einsaetze"]["schwierigkeiten"]))
    vr = Counter(e["meldung"]["vorrang"] for e in einsaetze)
    zeilen.append("  Vorrang Aufträge: " + ", ".join(f"{k} {vr.get(k, 0)}" for k in cfg["vorrang"]))
    return "\n".join(zeilen)


def anreichern(cfg, nachrichten):
    stellen = cfg["stellen"]
    for n in nachrichten:
        von = stellen[n["von"]]
        ziele = [stellen[a] for a in n["an_liste"]]
        if len(ziele) == 1:
            an = ziele[0]
        else:
            # Sammelruf: gemeinsame Erreichbarkeit nur, wenn bei allen gleich
            an = {"name": ", ".join(z["name"] for z in ziele),
                  "rufname": ", ".join(z["rufname"] for z in ziele)}
            for feld in ("telefon", "fax", "mail"):
                werte = {z[feld] for z in ziele}
                an[feld] = werte.pop() if len(werte) == 1 else ""
        n["nr_str"] = f"{n['nr']:03d}"
        n["von_stelle"] = von
        n["an_stelle"] = an
        n["arbeitsmittel"] = von["arbeitsmittel"]
        n["rufnummer"] = {
            "Telefon": an["telefon"],
            "Fax": an["fax"],
            "Mail": an["mail"],
            "Funk": "",
            "Melder": "",
        }[n["medium"]]


def statistik(cfg, nachrichten):
    gesamt = len(nachrichten)
    zeilen = [f"{gesamt} Nachrichten"]
    kat = Counter(n["kategorie"] for n in nachrichten)
    for key, k in cfg["kategorien"].items():
        ist = kat.get(key, 0)
        zeilen.append(f"  {k['name']:<22} {ist:3d}  ({ist / gesamt:5.0%}, Soll {k['soll']:.0%})")
    am = Counter(n["arbeitsmittel"] for n in nachrichten)
    zeilen.append(f"  Vordruck (TEL→FüSt)    {am.get('vordruck', 0):3d}")
    zeilen.append(f"  EDP (FüSt→…)           {am.get('edp', 0):3d}")
    vr = Counter(n["vorrang"] for n in nachrichten)
    zeilen.append("  Vorrang: " + ", ".join(f"{k} {vr.get(k, 0)}" for k in cfg["vorrang"]))
    return "\n".join(zeilen)


def finde_chromium():
    for k in CHROMIUM_KANDIDATEN:
        pfad = shutil.which(k) or (k if Path(k).is_file() else None)
        if pfad:
            return pfad
    sys.exit("Chromium nicht gefunden – Pfad in CHROMIUM_KANDIDATEN ergänzen.")


def drucke(chromium, html: Path, pdf: Path):
    pdf.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(
        [chromium, "--headless", "--no-sandbox", "--disable-gpu", "--no-pdf-header-footer",
         f"--print-to-pdf={pdf}", html.as_uri()],
        check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
    )


def rendere(env, vorlage, ziel: Path, **ctx):
    ziel.write_text(env.get_template(vorlage).render(**ctx), encoding="utf-8")
    return ziel


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--nur-pruefen", action="store_true", help="nur validieren, nichts erzeugen")
    args = ap.parse_args()

    cfg = lade_config()
    nachrichten = lade_nachrichten()
    einsaetze = lade_einsaetze()
    fehler = pruefe(cfg, nachrichten) + pruefe_einsaetze(cfg, einsaetze)
    if fehler:
        print("FEHLER:\n  " + "\n  ".join(fehler))
        sys.exit(1)
    anreichern(cfg, nachrichten)
    aufbereiten_einsaetze(cfg, einsaetze)
    print("Teil 1 – Nachrichtenpool Stab\n" + statistik(cfg, nachrichten))
    print("Teil 2 – Einsätze\n" + statistik_einsaetze(cfg, einsaetze))
    if args.nur_pruefen:
        return

    env = Environment(loader=FileSystemLoader(TEMPLATES), undefined=StrictUndefined,
                      trim_blocks=True, lstrip_blocks=True)
    env.filters["sprechweise"] = sprechweise
    chromium = finde_chromium()

    if BUILD.exists():
        shutil.rmtree(BUILD)
    BUILD.mkdir()
    shutil.copy(ASSETS / "style.css", BUILD / "style.css")
    if AUSGABE.exists():
        shutil.rmtree(AUSGABE)
    AUSGABE.mkdir()

    ctx = {"cfg": cfg}
    allg = AUSGABE / "0_Allgemein"
    teil1 = AUSGABE / "1_Nachrichtenpool_Stab"
    teil2 = AUSGABE / "2_Einsaetze_EDP"

    # ---------- Teil 1: Nachrichtenpool Stab ----------
    vordrucke = [n for n in nachrichten if n["arbeitsmittel"] == "vordruck"]
    edp = [n for n in nachrichten if n["arbeitsmittel"] == "edp"]

    drucke(chromium, rendere(env, "vordruck.html", BUILD / "vordrucke.html", nachrichten=vordrucke, **ctx),
           teil1 / "Vordrucke_A5_TEL_alle.pdf")
    for n in vordrucke:
        html = rendere(env, "vordruck.html", BUILD / f"vordruck_{n['nr_str']}.html", nachrichten=[n], **ctx)
        drucke(chromium, html, teil1 / "Vordrucke_A5_einzeln" / f"Vordruck_{n['nr_str']}.pdf")

    # EDP: alle + je sendender Stelle (die Stelle, an deren EDP eingespielt wird)
    drucke(chromium, rendere(env, "edp.html", BUILD / "edp.html", nachrichten=edp, **ctx),
           teil1 / "EDP_Texte_alle.pdf")
    for key, stelle in cfg["stellen"].items():
        auswahl = [n for n in edp if n["von"] == key]
        if not auswahl:
            continue
        name = stelle["rufname"].split()[-1]
        html = rendere(env, "edp.html", BUILD / f"edp_{key}.html", nachrichten=auswahl, **ctx)
        drucke(chromium, html, teil1 / f"EDP_Texte_{name}_{stelle['name'].replace(' ', '_')}.pdf")

    drucke(chromium, rendere(env, "uebersicht.html", BUILD / "uebersicht.html",
                             nachrichten=nachrichten, statistik=statistik(cfg, nachrichten), **ctx),
           teil1 / "UEL_Uebersicht_Nachrichten.pdf")

    # Anhänge: Original + PDF-Fassung
    if any(n["anhaenge"] for n in nachrichten):
        shutil.copytree(ANHAENGE, teil1 / "Anhaenge")
        for datei in sorted(ANHAENGE.iterdir()):
            titel = datei.stem.replace("_", " ")
            if datei.suffix.lower() == ".csv":
                with datei.open(encoding="utf-8") as f:
                    kopf, *zeilen = list(csv.reader(f, delimiter=";"))
                html = rendere(env, "anhang.html", BUILD / f"anhang_{datei.stem}.html",
                               titel=titel, bild=None, kopf=kopf, zeilen=zeilen)
            elif datei.suffix.lower() in (".png", ".jpg", ".jpeg", ".svg"):
                shutil.copy(datei, BUILD / datei.name)
                html = rendere(env, "anhang.html", BUILD / f"anhang_{datei.stem}.html",
                               titel=titel, bild=datei.name)
            else:
                continue
            drucke(chromium, html, teil1 / "Anhaenge" / f"{datei.stem}.pdf")

    # ---------- Teil 2: Einsätze in EDP anlegen ----------
    drucke(chromium, rendere(env, "einsatz_a4.html", BUILD / "einsaetze_a4.html", einsaetze=einsaetze, **ctx),
           teil2 / "Funk_und_UEL_A4_je_Einsatz.pdf")
    alle_vd = [v for e in einsaetze for v in einsatz_vordrucke(cfg, e)]
    drucke(chromium, rendere(env, "vordruck.html", BUILD / "einsaetze_vordrucke.html", nachrichten=alle_vd, **ctx),
           teil2 / "Vordrucke_A5_Einsaetze_gebuendelt.pdf")
    for e in einsaetze:
        html = rendere(env, "vordruck.html", BUILD / f"einsatz_{e['id']}.html",
                       nachrichten=einsatz_vordrucke(cfg, e), **ctx)
        drucke(chromium, html, teil2 / "Vordrucke_A5_einzeln" / f"Einsatz_{e['id']}_Stufe{e['stufe']}.pdf")
    drucke(chromium, rendere(env, "einsaetze_uebersicht.html", BUILD / "einsaetze_uebersicht.html",
                             einsaetze=einsaetze, statistik=statistik_einsaetze(cfg, einsaetze), **ctx),
           teil2 / "UEL_Uebersicht_Einsaetze.pdf")

    # ---------- Allgemein ----------
    texte = [n["text"] for n in nachrichten] + [m["text"] for e in einsaetze for m in e["meldungen"]] \
        + [m["von_rufname"] for e in einsaetze for m in e["meldungen"]]
    drucke(chromium, rendere(env, "kommplan.html", BUILD / "kommplan.html", k=cfg["kommunikation"],
                             genannt=[f for f in cfg["fahrzeuge"] if any(f["rufname"] in t for t in texte)], **ctx),
           allg / "Kommunikationsplan.pdf")
    drucke(chromium, rendere(env, "liesmich.html", BUILD / "liesmich.html", anzahl_nachrichten=len(nachrichten),
                             anzahl_einsaetze=len(einsaetze), **ctx),
           AUSGABE / "00_LIESMICH.pdf")
    print(f"Ausgabe in {AUSGABE.relative_to(ROOT)}/")


if __name__ == "__main__":
    main()
