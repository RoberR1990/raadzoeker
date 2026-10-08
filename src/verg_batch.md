# Draaiboek: terugwerkend vergaderingen samenvatten (één golf)

Werkmap: `D:\Raadzoeker` (Bash: `cd /d/Raadzoeker`, altijd `PYTHONUTF8=1`). Doel: vergaderingen van raad en commissies sinds VANAF samenvatten, nieuwste eerst.

1. **Budget checken** met `mcp__ccd_session_mgmt__get_usage` (laad via ToolSearch). Stop zonder iets te doen als het weekverbruik ≥ 80% is of het 5-uursvenster ≥ 70%.
2. **Lijst maken**: `PYTHONUTF8=1 python src/verg_batch.py lijst VANAF 12` (maakt de zuinige invoerpakketten en print `datum agendaId woorden naam`). Is de lijst leeg: klaar, meld dat.
3. **Groeperen**: verdeel de 12 over 4 groepen van samen ca. 20-25k woorden (een raadsvergadering > 20k woorden alleen of met één kleine erbij).
4. **Per groep één Agent** (subagent_type general-purpose, model `sonnet`, run_in_background true), alle 4 in één bericht, met deze prompt (pad = eerste 8 tekens van het agendaId):
   > Lees eerst D:\Raadzoeker\src\verg_prompt.md: dat is de opdracht. Voer die opdracht achtereenvolgens uit voor deze vergaderingen, één voor één (schrijf het uitvoerbestand van de ene vergadering voordat je aan het invoerbestand van de volgende begint; gebruik voor elke vergadering alleen haar eigen invoer):
   > 1. in: D:\Downloads Chrome\raadzoeker-werk\verg\in_XXXXXXXX.txt  uit: D:\Downloads Chrome\raadzoeker-werk\verg\uit_XXXXXXXX.json
   > (enz.)
   > Antwoord aan het eind alleen met de uitvoerpaden.
5. **Wachten** tot alle 4 klaar zijn (meldingen komen vanzelf; niet pollen).
6. **Controleren en publiceren**: `PYTHONUTF8=1 python src/verg_batch.py check` (citaatcontrole, schrapt wat niet letterlijk klopt, schrijft `docs/verg/`). Een FOUT bij één vergadering: noteren, verder gaan.
7. **Online zetten**: `git add -A docs/verg && git commit -m "Vergaderingen: N vergaderingen samengevat (terugwerkend)" && git pull --rebase --autostash && git push`. Commit-bericht eindigen met `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`.
8. Herhaal vanaf stap 1 zolang het aantal toegestane golven niet bereikt is.
9. **Melden** (kort, Nederlands, bullets): hoeveel samengevat, hoeveel nog te doen, geschrapte beweringen, verbruik voor/na.

Niet doen: andere bestanden aanpassen, Opus-subagents gebruiken, meer dan het toegestane aantal golven.
