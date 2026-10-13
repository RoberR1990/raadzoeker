# Draaiboek: wekelijks nieuwe vergaderingen samenvatten (Routine in Claude Code, cloudsessie)

Draait elke zaterdagochtend. De NAS heeft dan in de nacht de nieuwe raads- en commissievergaderingen opgehaald (`debat_nieuw.py`) en de debatindex bijgewerkt (`debat_index.py`); dit draaiboek vat samen wat nog geen samenvatting heeft. Geen werkmap nodig: de invoer komt uit `docs/data/debat/`.

Werk vanuit de repo-root, altijd met `export RZ_WERK=/tmp/rz-werk PYTHONUTF8=1` (lege map is goed). Eenmalig: `pip install -q zstandard beautifulsoup4 lxml`.

1. **Bijwerken**: `git fetch origin main && git checkout -B <de branch van deze sessie> origin/main` (de NAS heeft vannacht data gepusht).
2. **Lijst maken**: `python src/verg_batch.py lijst <datum van 21 dagen geleden, JJJJ-MM-DD> 12`. Die maakt de zuinige invoerpakketten in `/tmp/rz-werk/verg/` en print `datum agendaId woorden naam`. Is de lijst leeg: stop en meld 'geen nieuwe vergaderingen' (meestal: de NAS-run is mislukt of er was reces; kijk dan in `docs/data/status.json`).
3. **Groeperen**: verdeel over groepen van samen ca. 20-25k woorden (een raadsvergadering > 20k woorden alleen of met één kleine erbij); hooguit 4 groepen.
4. **Per groep één Agent** (subagent_type general-purpose, model `sonnet`, alle groepen in één bericht), met deze prompt (pad = eerste 8 tekens van het agendaId, absolute paden):
   > Lees eerst <repo>/src/verg_prompt.md: dat is de opdracht. Voer die opdracht achtereenvolgens uit voor deze vergaderingen, één voor één (schrijf het uitvoerbestand van de ene vergadering voordat je aan het invoerbestand van de volgende begint; gebruik voor elke vergadering alleen haar eigen invoer):
   > 1. in: /tmp/rz-werk/verg/in_XXXXXXXX.txt  uit: /tmp/rz-werk/verg/uit_XXXXXXXX.json
   > (enz.)
   > Antwoord aan het eind alleen met de uitvoerpaden.
5. **Controleren en publiceren**: `python src/verg_batch.py check` (citaatcontrole, schrapt wat niet letterlijk klopt, schrijft `docs/verg/` en zet de samengevatte vergaderingen als grote update in `docs/data/mijlpalen.json`, pagina 'Wat is er nieuw'). Een FOUT bij één vergadering: noteren, verder gaan.
6. **Online zetten**: alleen `docs/verg/` en `docs/data/mijlpalen.json` committen (`git add docs/verg docs/data/mijlpalen.json`), bericht `Vergaderingen: N vergaderingen samengevat (week JJJJ-WW)`, pushen naar de branch van deze sessie, een PR naar `main` maken en die zelf mergen (afspraak Robert). Elke push naar `main` zet de site online.
7. **Melden** (kort, Nederlands): welke vergaderingen samengevat, hoeveel beweringen geschrapt, wat is overgeslagen en waarom.

Niet doen: andere bestanden aanpassen (ook `docs/data/logboek.json` niet; dat is van de NAS), Opus-subagents gebruiken, meer dan 12 vergaderingen per run, de NAS-data (`docs/data/`) opnieuw maken.
Kosten: ca. 95k Sonnet-tokens per vergadering; een gewone week (1 raad + 5 à 6 commissies) ca. 0,6 mln.
