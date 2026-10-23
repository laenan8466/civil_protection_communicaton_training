# Fernmeldeübung Johannes Hannover – Nachrichten-Generator

Erzeugt Übungsnachrichten für eine Fernmeldeübung (Übermittlung + Dokumentation) der Malteser Hannover.
Szenario-Inspiration: KatS-Übung 2026 (Evakuierung Pflegeeinrichtung Tellkampfschule → Friederikenstift, BR Schützenplatz).

## Übende Stellen

Nur diese vier Stellen senden und empfangen. Fahrzeuge und Einheiten werden nur im Nachrichtentext genannt.

| Stelle | Rufname | Arbeitsmittel | Rolle |
|---|---|---|---|
| TEL Hannover | Joh. H 59-10-1 | 4-fach-Vordruck (Papier) | Sende-/Empfangsteil, sichtet + verteilt gemeinsam |
| FüSt Nord („UEA Nord“) | Joh. H 59-12-1 | EDP Command | Vulnerable Gruppen, Räumung Pflegeeinrichtung |
| FüSt Süd („UEA Süd“) | Joh. H 59-12-2 | EDP Command | Transportorganisation, BR Schützenplatz |
| FüSt West („UEA West“) | Joh. H 59-12-3 | EDP Command | Sanitätsdienst klassisch (UHS, San-Wache) |

Verfasser-Funktionen:
- **TEL:** S1, S2, S3, S4, S5, S6, Fachberater Sanität
- **FüSt (FüGr nach NDS-Konzept):** Leitung des Stabes, S1/4/6, S2, S3, med. Leitung

Beispiel: S1 der TEL verfasst → FmSt TEL Hannover übermittelt → FüSt Süd (59-12-2) nimmt auf, sichtet, verteilt zur Info an S2.

## Funkrufnamen

Nach Nds. MBl. 2024 Nr. 125: `Rufname Region Org-Fahrzeug-Ordnung`, z. B. `Joh. H 59-85-1`.
Rufnamen: Johannes (MHD, Joh.), Akkon (JUH, Akk.), Rotkreuz (DRK), Sama (ASB), Pelikan (DLRG), Florian (FW), Heros (THW), Kater.
Region: H = Hannover, H# = Hannover Land (Region).

## Nachrichtenfluss → Unterlagen

| Ursprung | Ziel | Einspielung durch Übungsleitung | Übende tun |
|---|---|---|---|
| TEL | FüSt | **Vordruck** (weißes Blatt A5, Verfasser-Teil ausgefüllt) | TEL sichtet/übermittelt, FüSt nimmt in EDP auf |
| FüSt | TEL | **EDP-Blatt** (zum Kopieren in EDP) | FüSt sendet, TEL nimmt auf leerem Vordruck auf |
| FüSt | FüSt | **EDP-Blatt** | beide EDP (kleiner Anteil) |

Medien: Telefon, Funk, Fax, Mail, Melder. Vorrang: normal, Sofort, Blitz (wenige Blitz).

## Nachrichtenpool

Ca. 50 Nachrichten, ohne Uhrzeiten (nur nummeriert):
- 60 % FüGr / Stab
- 20 % Transportdisposition
- 20 % Sanitätsdienst klassisch

Anhänge nur wenige, immer als Datei in `anhaenge/`.

## Aufbau

```
config/stellen.yaml        Stellen, Rufnamen, Funktionen, Rufnummern, Fahrzeug-Pool
nachrichten/NNN.yaml       eine Datei pro Nachricht
anhaenge/                  Dateien zum Anfügen in EDP
generator/build.py         validiert und erzeugt die PDFs
generator/templates/       Vordruck, EDP-Blatt, Übersicht (HTML → PDF via Chromium)
ausgabe/                   erzeugte PDFs
```

### Nachricht (YAML)

```yaml
nr: 1
kategorie: fuegr          # fuegr | transport | sandienst
von: TEL                  # TEL | NORD | SUED | WEST
von_funktion: S3
an: SUED
an_funktion: Leitung des Stabes
zur_info: [S2]
medium: Funk              # Telefon | Funk | Fax | Mail | Melder
vorrang: normal           # normal | Sofort | Blitz
betreff_art: Auftrag
betreff: Kurzer Betreff
zeichen: Mü               # Handzeichen Verfasser
bezug: null               # optional: Nr. einer anderen Übungsnachricht
anhaenge: []              # Dateinamen aus anhaenge/
text: |
  Nachrichtentext
notiz: Hinweis für die Übungsleitung (erwartete Reaktion)
```

## Nutzung

```
python3 generator/build.py              # prüfen + PDFs nach ausgabe/
python3 generator/build.py --nur-pruefen
```

Benötigt Python 3 mit `pyyaml`, `jinja2` sowie Chromium/Chrome. Die erzeugten PDFs liegen eingecheckt in `ausgabe/`.

Vordrucktext: max. ca. 14 Zeilen à 68 Zeichen, sonst bricht der Build mit Fehler ab.

Ausgabe:
- `Vordrucke_alle.pdf` + `vordrucke/Vordruck_NNN.pdf` – A5, zum Drucken
- `EDP_alle.pdf` + je sendender FüSt – A4, eine Nachricht pro Seite
- `Uebersicht_Uebungsleitung.pdf` – alle Nachrichten mit Hinweisen
- `anhaenge/`
