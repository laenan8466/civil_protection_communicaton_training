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

## Teil 2: Einsätze in EDP anlegen

30 Einsätze (15 Transportorganisation, 15 Sanitätsdienst), je 7 einfach / 4 mittel / 4 schwer, sortiert von einfach nach schwer:
- **Stufe 1 einfach:** alle Angaben inkl. Patientenname
- **Stufe 2 mittel:** Angaben fehlen (z. B. kein Patientenname), kommen mit Rückmeldung
- **Stufe 3 schwer:** keine Adresse, sondern Objekt (Hannover) oder Ortsbeschreibung („Georgengarten, links vom Leibniztempel“)

Auftrag immer von TEL **Florian H 01-13-1** an **Transportdisposition** bzw. **EA Sanitätsdienst**. Dazu je 1–2 Rückmeldungen des bearbeitenden Fahrzeugs (Rufname aus `config/stellen.yaml` → `fahrzeuge`). Einsätze werden in EDP angelegt (nicht in Command – das ist nur das Nachrichtenmodul).

Die Übungsleitung gibt jeden Einsatz entweder per Funk (A4-Blatt je Einsatz, Rückmeldungen auf derselben Seite) oder per Vordruck (gebündelt, je Meldung eine Seite). Schwierigkeit steht auf jedem Blatt.

```yaml
# einsaetze/E07_t_lehmann.yaml
nr: 7
bereich: transport        # transport | sandienst
schwierigkeit: einfach    # einfach | mittel | schwer
meldung: {von_funktion: S3, medium: Funk, vorrang: normal, betreff: ..., zeichen: Ri, text: ...}
rueckmeldungen:
  - {von: "Joh. H 59-92-1", funktion: Fahrzeugführer, zeichen: Pe, text: ...}
loesung: {stichwort: ..., ort: ..., patient: ..., ziel: ..., hinweise: ...}
```

## Aufbau

```
config/stellen.yaml        Stellen, Rufnamen, Funktionen, Rufnummern, Fahrzeug-Pool, Teil-2-Einstellungen
nachrichten/NNN.yaml       Teil 1: eine Datei pro Nachricht
einsaetze/ENN_*.yaml       Teil 2: eine Datei pro Einsatz inkl. Rückmeldungen und Lösung
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
- Ausgabe: `ausgabe/0_Allgemein/Befehle/Befehl_NNN.pdf`, dazu `Befehl_Vorlage.pdf` als leeres Formular.

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

Ausgabe (alles PDF, `00_LIESMICH.pdf` erklärt die Ordner):

```
ausgabe/
  00_LIESMICH.pdf
  0_Allgemein/
    Kommunikationsplan.pdf                    Skizze angelehnt an DV 102
    Befehle/                                  schriftliche Befehle + leere Vorlage (A4)
  1_Nachrichtenpool_Stab/
    UEL_Uebersicht_Nachrichten.pdf            Übungsleitung, mit Uhrzeit-/Feedbackspalten
    Vordrucke_A5_TEL_alle.pdf                 + Vordrucke_A5_einzeln/
    EDP_Texte_alle.pdf                        + EDP_Texte_59-12-x_*.pdf je FüSt
    Anhaenge/                                 Original + PDF
  2_Einsaetze_EDP/
    UEL_Uebersicht_Einsaetze.pdf              Übungsleitung, mit Uhrzeit-/Feedbackspalten
    Funk_und_UEL_A4_je_Einsatz.pdf            1 Seite je Einsatz inkl. Rückmeldungen, Lösung, Feedback
    Vordrucke_A5_Einsaetze_gebuendelt.pdf     je Einsatz Auftrag + Rückmeldungen
    Vordrucke_A5_einzeln/Einsatz_ENN_StufeX.pdf
```
