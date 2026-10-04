# Fase 1 — domeinen (4-10-2026)

Scripts: `src/domeinen.py` (indeling + labels), `src/themas_drempel.py` (1c), `src/steekproef_domein.py` (beoordelingspagina). Uitvoer in de werkmap `labels/`: `domein.json` (per stuk: domein, methode, zekerheid, eventueel tweede domein), `domein_rapport.txt`, `themas_drempel.txt`.

## 1a. Domeinindeling: 13 domeinen

Afgeleid uit de beleidsvelden die iBabs zelf gebruikt (die volgen de portefeuilles en commissies), niet uit het organogram.

| Domein | iBabs-beleidsvelden | Gelabeld |
|---|---|---|
| Wonen en bouwen | Bouwen en Wonen, Wonen, Bouwen, Vastgoed, Projecten | 8.008 |
| Bestuur en organisatie | Bestuur, Organisatie, Wijken, Gebieden | 6.746 |
| Mobiliteit | Mobiliteit | 4.858 |
| Zorg, welzijn en jeugd | Zorg, Welzijn, Volksgezondheid, Jeugd | 4.220 |
| Veiligheid | Veiligheid | 3.509 |
| Buitenruimte | Buitenruimte | 3.317 |
| Cultuur en sport | Cultuur, Sport | 3.072 |
| Werk, inkomen en armoede | Werk en Inkomen, Armoedebestrijding, Schulddienstverlening, NPRZ | 2.589 |
| Economie en haven | Economie, Haven, Horeca | 2.539 |
| Klimaat en energie | Duurzaam(heid) | 1.703 |
| Samenleven en participatie | Samenleven, Integratie, Participatie | 1.536 |
| Financiën | Financiën (3 spellingen), Commissie tot Onderzoek van de Rekening | 1.315 |
| Onderwijs | Onderwijs, Onderwijs en Jeugd | 1.242 |

Onderwerpen eronder: de 38 bestaande onderwerpen uit `onderwerpen.py` (Parkeren valt onder Mobiliteit). Die indeling volgt in fase 3; nu zijn alleen de domeinen gelabeld.

**Hoe de commissies op elkaar aansluiten** (afgeleid uit de beleidsvelden van hun stukken):

| Domein | 2018–2022 | 2022–2026 | 2026– |
|---|---|---|---|
| Wonen en bouwen, Buitenruimte | Bouwen, Wonen en Buitenruimte | BWB (idem) | Bouwen en Wonen (alleen wonen); buitenruimte → Leefomgeving en Economie |
| Mobiliteit, Economie en haven, Klimaat | EDEM | MHEK | Leefomgeving en Economie |
| Veiligheid, Bestuur, Financiën | Veiligheid en Bestuur + MPOF | BOFV | Veiligheid, Bestuur en Financiën |
| Zorg, Cultuur en sport | ZOCS (ook onderwijs) | ZWCS | Zorg en Cultuur |
| Werk, Samenleven, Onderwijs | WIISA (onderwijs zat in ZOCS) | WIOSSAN | Onderwijs en Samenleven (+ werk/armoede) |

Wringt: onderwijs verhuist in 2022 van ZOCS naar WIOSSAN; buitenruimte verhuist in 2026 van de bouwcommissie naar Leefomgeving. Voor de domeinen maakt dat niet uit, want die hangen aan het beleidsveld, niet aan de commissie.

## 1b. Labels: 54.696 stuks (44.505 stukken + 10.191 agendapunten met spreekbeurten)

| Methode | Aantal | Hoe |
|---|---|---|
| bron | 30.367 | beleidsveld uit iBabs (brieven, moties, toezeggingen, vragen, raadsvoorstellen, wijkraadadviezen) en commissiekopjes zoals '1.04.02. Zorg' |
| gekoppeld | 1.364 | debat → beleidsveld van de stukken op hetzelfde agendapunt of de moties die erbij zijn ingediend |
| woordmodel | 12.923 | vooral wijkraadstukken (8.678) en debatten (3.689); getraind op de bronlabels |
| geen (regel) | 10.042 | procedureel (opening, besluitenlijst, agenda) of over alles tegelijk (wijkraadvergadering, wijkplan) |

- **Woordmodel**: 84% eens met iBabs (kruisvalidatie, 29.677 stukken). De zekerheid die het model zelf geeft, voorspelt weinig (89% bij ≥0,99).
- **Licht AI-model (Haiku) getest op 300 stukken met bekend beleidsveld**: maar 64% eens (woordmodel: 86%). Haiku kiest naar inhoud ('Cinerama' → cultuur, 'Reclamedrukwerk' → buitenruimte), iBabs naar portefeuille (→ wonen, klimaat). Het woordmodel neemt de logica van iBabs over. **Daarom geen AI ingezet: 0 tokens voor het labelen.**
- Zwakste deel: wijkraadstukken. Hun titels zijn vaak bestandsnamen ('Actiepunten.docx').

## 1c. Drempelanalyse: 40 kandidaat-thema's

'Hoofdonderwerp' telt alleen als de term in de titel staat, of minstens drie keer in de tekst en al in de eerste 150 woorden. Volledige tabel in `labels/themas_drempel.txt`.

| Drempel (stukken) | Thema's over (2018–2026 / 2022–2026) | Valt af (2022+) |
|---|---|---|
| 5 | 40 / 40 | – |
| 10, 15, 20 | 40 / 39 | Laaggeletterdheid |
| 50 | 37 / 35 | + Organisatieontwikkeling, Kansengelijkheid, Eenzaamheid, Polarisatie |
| 100 | 33 / 30 | + Informatiebeveiliging, Mentale gezondheid, Slavernijverleden, Nachteconomie, Grote evenementen |

- Drempels van 5–20 schiften niet. Pas bij 50–100 valt er iets af.
- Grootste: wijkgericht werken (8.014, vooral door de wijkraadstukken), maatschappelijk initiatief (2.745), onderzoek en evaluatie (1.643), participatie (1.375). AI en algoritmes: 139.
- 'Organisatieontwikkeling' wordt bijna nooit zo genoemd (29). Dat thema moet anders worden afgebakend.

## Controle (door Robert)

`ontwerp/steekproef-domein.html` (lokaal openen):
- **Steekproef 200**, gelaagd per methode (bron 60, woordmodel-stuk 50, woordmodel-debat 40, gekoppeld 25, geen 25), zodat de precisie per methode zichtbaar wordt. Het totaalcijfer wordt daarna gewogen naar de populatie.
- **Parkeren**: alle 665 stukken en agendapunten met 'parkeer' in de titel. De 104 die níet op Mobiliteit staan, staan bovenaan. Knop 'Rest op deze tab: goed' na het doorlopen.
- Klaar → 'Download oordelen' → bestand in `raadzoeker-werk\labels\`.
