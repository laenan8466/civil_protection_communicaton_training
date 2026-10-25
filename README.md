# Communication Exercise Johannes Hannover – Message Generator

Generates exercise material for a communication exercise (message transmission + documentation) of the Malteser Hannover.
Scenario inspiration: KatS exercise 2026 (evacuation of the care facility Tellkampfschule → Friederikenstift, staging area Schützenplatz).

All generated documents are in German, because the exercise is German. Field values in the YAML files (e.g. `Funk`, `Blitz`, `einfach`) therefore stay German as well.

## Participating stations

Only these four stations send and receive. Vehicles and units are only mentioned in message texts.

| Station | Call sign | Tool | Role |
|---|---|---|---|
| TEL Hannover | Joh. H 59-10-1 | 4-part message form (paper) | send/receive section, screens + distributes jointly |
| FüSt Nord („UEA Nord“) | Joh. H 59-12-1 | EDP Command (message module) | vulnerable groups, evacuation of care facility |
| FüSt Süd („UEA Süd“) | Joh. H 59-12-2 | EDP Command | transport organisation, staging area Schützenplatz |
| FüSt West („UEA West“) | Joh. H 59-12-3 | EDP Command | classic medical service (first aid post, medical watch) |

Author functions:
- **TEL:** S1, S2, S3, S4, S5, S6, Fachberater Sanität (medical specialist advisor)
- **FüSt (command group per Lower Saxony concept):** Leitung des Stabes (head of staff), S1/4/6, S2, S3, med. Leitung (medical lead)

Example: S1 of the TEL writes → signal office TEL Hannover transmits → FüSt Süd (59-12-2) receives, screens, distributes for info to S2.

## Call signs

Per Nds. MBl. 2024 No. 125: `Name Region Org-Vehicle-Order`, e.g. `Joh. H 59-85-1`.
Names: Johannes (MHD, Joh.), Akkon (JUH, Akk.), Rotkreuz (DRK), Sama (ASB), Pelikan (DLRG), Florian (fire brigade), Heros (THW), Kater.
Region: H = Hannover (city), H# = Hannover Land (region).

## Part 1: Message pool (staff) – message flow → documents

| Origin | Target | Injected by exercise control as | Participants do |
|---|---|---|---|
| TEL | FüSt | **message form** (white A5 sheet, author section pre-filled) | TEL screens/transmits, FüSt records in EDP |
| FüSt | TEL | **EDP sheet** (copy into EDP) | FüSt sends, TEL records on blank form |
| FüSt | FüSt | **EDP sheet** | both EDP (small share) |

Media: Telefon, Funk (radio), Fax, DFÜ (data transmission, here e-mail; the route is shown under "Rufnummer" on the form), Melder (runner). Priority: normal, Sofort (immediate), Blitz (flash – few, only for danger to life or operations).

The recipient on form/EDP is always just the counterpart station (e.g. "TEL Hannover"). Which function the message is meant for and who gets it for info is only shown as a note for exercise control at the bottom of the sheet – the screener decides.

Outside the transport dispatch, units are moved, not individual vehicles.

About 50 messages, without times (numbered only):
- 60 % command group / staff
- 20 % transport dispatch
- 20 % classic medical service

Few attachments, always as a file in `anhaenge/`.

## Part 2: Creating incidents in EDP

30 incidents (15 transport organisation, 15 medical service), each 7 easy / 4 medium / 4 hard, sorted from easy to hard:
- **Level 1 easy (`einfach`):** all details incl. patient name
- **Level 2 medium (`mittel`):** details missing (e.g. no patient name), delivered later by a feedback report
- **Level 3 hard (`schwer`):** no address, but a landmark (Hannover) or a location description ("Georgengarten, left of the Leibniztempel")

The order always comes from TEL **Florian H 01-13-1** to **Transportdisposition** (transport dispatch) or **EA Sanitätsdienst** (medical service section). Each incident has 1–2 feedback reports from the vehicle handling it (call sign from `config/stellen.yaml` → `fahrzeuge`). Incidents are created in EDP (not in Command – that is only the message module).

Exercise control injects each incident either by radio (one A4 sheet per incident, feedback reports on the same page) or by message form (bundled, one page per message). The difficulty level is printed on every sheet.

```yaml
# einsaetze/E07_t_lehmann.yaml
nr: 7
bereich: transport        # transport | sandienst
schwierigkeit: einfach    # einfach | mittel | schwer
meldung: {von_funktion: S3, medium: Funk, vorrang: normal, betreff: ..., zeichen: Ri, text: ...}
rueckmeldungen:
  - {von: "Joh. H 59-92-1", funktion: Fahrzeugführer, zeichen: Pe, text: ...}
loesung: {stichwort: ..., ort: ..., patient: ..., ziel: ..., hinweise: ...}   # expected EDP entry
```

## Written orders (Befehle)

Separate from the message pool: written orders for preparing and running the exercise,
structured per DV 100, 3.3.3.1 and annex 4 (header, 1 situation, 2 mission, 3 execution, 4 logistics,
5 command and communication, footer with annexes, distribution, signature).

- Copy `befehle/vorlage.yaml` to `befehle/NNN_shortname.yaml` and fill it in. Empty fields become writing lines
  in the PDF (date/time, times, signature by hand).
- Required: `nr`, `betreff`, `befehlende_stelle`, `an`, `auftrag`. `notiz` does not appear on the order.
- Output: `ausgabe/0_Allgemein/Befehle/Befehl_NNN.pdf`, plus `Befehl_Vorlage.pdf` as a blank form.

| No | Subject |
|---|---|
| 001 | Aufbau Übungsbetrieb Führungsstelle in der Fahrzeughalle (59-12-1 with front tent, 59-10-1 as exercise control) |

## Separator sheet (Trennblatt)

`trennblatt/trennblatt.html` reproduces the NLBK sheet "4-Fach-Nachrichtenvordruck, Ausfüllhilfe und Verteilung" (01/2024) as an A4 landscape separator to put between the form sets so nothing is copied through. The middle is exactly A5 wide (148 mm) and is covered by the inserted form; the filling hints sit on the visible left and right margins (74.5 mm each). Malteser branding (Palatino, Malteser red, official logo from `presentations-revealjs/styles/malteser`). Texts adapted to the KSK form as in the presentation deck "Vierfachvordruck" (DFÜ, tactical time, sender fields, screener section). Output: `ausgabe/0_Allgemein/Trennblatt_Vierfachvordruck_A4.pdf`.

## Repository layout

```
config/stellen.yaml        stations, call signs, functions, phone numbers, vehicle pool, part-2 settings
nachrichten/NNN.yaml       part 1: one file per message
einsaetze/ENN_*.yaml       part 2: one file per incident incl. feedback reports and solution
befehle/vorlage.yaml       template for written orders (DV 100)
befehle/NNN_*.yaml         one written order per file
trennblatt/                separator sheet for the 4-part form (HTML source + official Malteser logo)
anhaenge/                  attachments for EDP
generator/build.py         validates and generates the PDFs
generator/templates/       form, EDP sheet, overviews etc. (HTML → PDF via Chromium)
ausgabe/                   generated PDFs
```

### Message (YAML, part 1)

```yaml
nr: 1
kategorie: fuegr          # fuegr | transport | sandienst
von: TEL                  # TEL | NORD | SUED | WEST
von_funktion: S3
an: SUED                  # broadcast: an: [NORD, SUED, WEST]
an_funktion: Leitung des Stabes
zur_info: [S2]
medium: Funk              # Telefon | Funk | Fax | DFÜ | Melder
vorrang: normal           # normal | Sofort | Blitz
betreff_art: Auftrag
betreff: Short subject
zeichen: Mü               # author's initials
bezug: null               # optional: no. of another exercise message
anhaenge: []              # file names from anhaenge/
text: |
  Message text
notiz: Note for exercise control (expected reaction)
```

## Usage

```
python3 generator/build.py              # validate + generate PDFs into ausgabe/
python3 generator/build.py --nur-pruefen # validate only
```

Requires Python 3 with `pyyaml` and `jinja2`, plus Chromium/Chrome. The generated PDFs are committed in `ausgabe/`.

Message form per NLBK filling guide (01/2024), layout like the KSK form: the first line of the message is the subject (content line); with `bezug`, "Bezug: Nachricht „…“" follows. Under "Rufnummer" the form shows the phone number, e-mail address (DFÜ) or call sign, depending on the medium. Date/time of the sender stays empty: exercise control writes it by hand as tactical time when injecting (e.g. 241105oct26).

Form text (incl. subject and reference): max. approx. 14 lines of 68 characters, otherwise the build fails.

Output (all PDF, `00_LIESMICH.pdf` explains the folders):

```
ausgabe/
  00_LIESMICH.pdf
  0_Allgemein/
    Kommunikationsplan.pdf                    communication plan, sketch based on DV 102
    Befehle/                                  written orders + blank template (A4)
    Trennblatt_Vierfachvordruck_A4.pdf        separator sheet: filling guide + distribution, Malteser branding
  1_Nachrichtenpool_Stab/
    UEL_Uebersicht_Nachrichten.pdf            exercise control, with time/feedback columns
    Vordrucke_A5_TEL_alle.pdf                 + Vordrucke_A5_einzeln/
    EDP_Texte_alle.pdf                        + EDP_Texte_59-12-x_*.pdf per FüSt
    Anhaenge/                                 original + PDF
  2_Einsaetze_EDP/
    UEL_Uebersicht_Einsaetze.pdf              exercise control, with time/feedback columns
    Funk_und_UEL_A4_je_Einsatz.pdf            one page per incident incl. feedback reports, solution, feedback
    Vordrucke_A5_Einsaetze_gebuendelt.pdf     per incident: order + feedback reports
    Vordrucke_A5_einzeln/Einsatz_ENN_StufeX.pdf
```
