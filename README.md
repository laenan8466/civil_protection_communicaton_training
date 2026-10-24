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

Medien: Telefon, Funk, Fax, DFÜ, Melder. DFÜ = Datenfernübertragung (hier: Mail); der Weg steht auf dem Vordruck unter Rufnummer. Vorrang: normal, Sofort, Blitz (wenige Blitz, nur bei Gefahr für Leben/laufenden Betrieb).

Empfänger auf Vordruck/EDP ist immer nur die Gegenstelle (z. B. „TEL Hannover“). Für wen die Nachricht gedacht ist und wer sie zur Info bekommt, steht nur als Info für die Übungsleitung unten auf dem Blatt – das entscheidet der Sichter.

Außerhalb der Transportdispo werden Einheiten bewegt, keine einzelnen Fahrzeuge.

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
befehle/vorlage.yaml       Vorlage schriftlicher Befehl (DV 100)
befehle/NNN_*.yaml         ein schriftlicher Befehl pro Datei
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
an: SUED                  # Sammelruf: an: [NORD, SUED, WEST]
an_funktion: Leitung des Stabes
zur_info: [S2]
medium: Funk              # Telefon | Funk | Fax | DFÜ | Melder
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

## Befehle

Getrennt vom Nachrichtenpool: schriftliche Befehle zur Vorbereitung und Durchführung des Übungsbetriebs,
gegliedert nach DV 100, 3.3.3.1 und Anlage 4 (Kopf, 1 Lage, 2 Auftrag, 3 Durchführung, 4 Versorgung,
5 Führung und Kommunikation, Fuß mit Anlagen, Verteiler, Unterschrift).

- `befehle/vorlage.yaml` kopieren nach `befehle/NNN_kurzname.yaml` und ausfüllen. Leere Felder werden im PDF
  zu Schreiblinien (Datum/Uhrzeit, Zeiten, Unterschrift handschriftlich).
- Pflicht: `nr`, `betreff`, `befehlende_stelle`, `an`, `auftrag`. `notiz` erscheint nicht auf dem Befehl.
- Ausgabe: `ausgabe/befehle/Befehl_NNN.pdf`, dazu `Befehl_Vorlage.pdf` als leeres Formular.

| Nr | Betreff |
|---|---|
| 001 | Aufbau Übungsbetrieb Führungsstelle in der Fahrzeughalle (59-12-1 mit Vorzelt, 59-10-1 als Übungsleitung) |

## Nutzung

```
python3 generator/build.py              # prüfen + PDFs nach ausgabe/
python3 generator/build.py --nur-pruefen
```

Benötigt Python 3 mit `pyyaml`, `jinja2` sowie Chromium/Chrome. Die erzeugten PDFs liegen eingecheckt in `ausgabe/`.

Vordruck nach NLBK-Ausfüllhilfe (01/2024), Layout wie KSK-Vordruck: Die erste Zeile der Nachricht ist der Betreff (Inhaltszeile), bei `bezug` folgt „Bezug: Nachricht „…““. Unter Rufnummer steht je nach Medium Telefonnummer, Mailadresse (DFÜ) oder Funkrufname. Datum, Uhrzeit beim Absender bleibt leer: Die Übungsleitung trägt sie beim Einspielen von Hand als taktische Zeit ein (z. B. 241105oct26).

Vordrucktext (inkl. Betreff und Bezug): max. ca. 14 Zeilen à 68 Zeichen, sonst bricht der Build mit Fehler ab.

Ausgabe:
- `Vordrucke_alle.pdf` + `vordrucke/Vordruck_NNN.pdf` – A5, zum Drucken
- `EDP_alle.pdf` + je sendender FüSt – A4, eine Nachricht pro Seite
- `Uebersicht_Uebungsleitung.pdf` – alle Nachrichten mit Hinweisen
- `Kommunikationsplan.pdf` – Skizze angelehnt an DV 102
- `anhaenge/` – Original + PDF-Fassung je Anhang
- `befehle/` – schriftliche Befehle + leere Vorlage (A4)
