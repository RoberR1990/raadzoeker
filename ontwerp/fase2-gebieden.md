# Fase 2 — gebieden (4-10-2026)

Scripts: `src/gebieden.py` (hiërarchie, organen, vertaaltabel, koppelen) en `src/bag_straten.py` (BAG-adressen → straat → CBS-buurt). Uitvoer in de werkmap: `gebied/gebieden.json`, `labels/gebied.json` en `labels/gebied_rapport.txt`.

## 2a. Hiërarchie: stad → 14 gebieden → 71 wijken → 92 CBS-buurten

Dit kan, maar op een paar punten wringt het:
- **Het buurtniveau voegt weinig toe.** CBS deelt Rotterdam maar in 92 buurten in, ongeveer even fijn als de 71 wijken van Wijkprofiel. 64 wijken bestaan uit precies één CBS-buurt. Een fijner niveau is er niet.
- **13 CBS-buurten horen bij geen enkele wijk.** Het gaat om havens, bedrijventerreinen en water: Waalhaven, Eemhaven, Botlek, Europoort, Maasvlakte, Vondelingenplaat, Spaanse Polder, Nieuw Mathenesse, Bedrijvenpark Noord-West, Rivium, Noordzeeweg en Buitenwater. Die hangen nu direct onder de stad.
- **Groot-IJsselmonde** is in Wijkprofiel opgesplitst in Noord en Zuid, maar bij CBS één buurt. Cijfers per helft zijn er dus niet.
- **CBS-grenzen vóór 2022** krijg ik niet via PDOK. 2022–2025 zijn gelijk; voor eerdere jaren gelden de grenzen van 2024.
- **CS-kwartier** heeft vanaf 2022 geen wijkraad.

## 2b. Vertaaltabel: van gebiedscommissies naar wijkraden

Er zijn 24 oude organen: 12 gebiedscommissies, 5 wijkcomités en 7 wijkraden van vóór 2022. Er zijn 44 nieuwe: 42 wijkraden en 2 dorpsraden.

| Overgang | Aantal | Voorbeelden |
|---|---|---|
| één op één | 8 | Overschie, Hoogvliet, Pernis, Rozenburg en Hoek van Holland (worden dorpsraden), Nesselande, Zevenkamp |
| opgesplitst | 8 | Gebiedscommissies Charlois (5 wijkraden), Prins Alexander (6), Delfshaven (4), IJsselmonde (3), Kralingen-Crooswijk, Hillegersberg-Schiebroek, Centrum |
| opgegaan in een grotere wijkraad | 9 | Bergpolder, Blijdorp en Liskwartier → één wijkraad; Agniesebuurt en Provenierswijk → één; Noordereiland en Kop van Zuid-Entrepot → Entrepot-Noordereiland |

- **Grenzen gaan overal schoon over.** Wijkraden bestaan uit hele wijken, dus elke wijkraad valt binnen één gebied. Alleen CS-kwartier (Centrum) heeft geen opvolger.
- **Gat 1:** voor Noord en Feijenoord zijn geen gebiedscommissies van vóór 2022 te vinden. Die gebieden hadden toen wijkraden of wijkcomités.
- **Gat 2:** de bron (wijkraad.rotterdam.nl) begint in 2022. Vergaderingen en stukken van de gebiedscommissies van 2018–2021 heb ik niet. Voor die jaren is er dus geen bron-koppeling.
- Twee wijkraden zijn van naam veranderd en samengevoegd ('Bergpolder-Blijdorp-Liskwartier' en 'Blijdorp-Bergpolder-Liskwartier'). Carnisse-Zuiderpark is uitgebreid met Zuidplein.

## 2c. Koppelen: dekking en precisie

| Methode | Wat | Dekking | Precisie |
|---|---|---|---|
| **1. bron** | wijkraadstukken, -vergaderingen, -adviezen, -verslagen en -plannen | 14.733 stukken; 98–100% van die soorten (wijkraadadviezen 60%: de afzender staat niet altijd in de titel) | zeker |
| **2. locatie** | bekendmakingen met een locatiepunt → buurt → wijk | 79.898 van 91.960 (87%); 7% heeft geen punt; 6% ligt in een haven of bedrijventerrein | zeker |
| **3. tekst** | wijk-, gebieds- en straatnamen (4.497 BAG-straten) in titel of tekst | raadsvoorstellen 46%, collegebrieven 40%, vragen 36%, raadsdebatten 30%, commissiedebatten 24%, moties 15%, toezeggingen 11% | **90%** (Opus-toets op 100: 90 goed, 9 fout, 1 onduidelijk) |

Getoetste valkuilen:
- **Coolsingel** wordt overgeslagen: in raadsstukken betekent het bijna altijd 'het stadhuis'.
- **Zuidplein** is wijk, straat en winkelcentrum tegelijk, maar valt alle drie in de wijk Zuidplein. Klopt dus.
- **Straten in meerdere wijken:** 302 van de 4.497 straten worden aan elke wijk met minstens 20% van de adressen gekoppeld; 219 straten liggen alleen in havens of op bedrijventerreinen.
- **Persoonsnamen:**
  - Straten met de achternaam van een raadslid of wethouder (zoals Oostdijk) worden overgeslagen.
  - Hetzelfde geldt voor een straatnaam direct na voorletters, 'wethouder' of 'mevrouw'.
- **Water:** rivieren en kanalen (Nieuwe Maas, Nieuwe Waterweg, havenkanalen) worden overgeslagen.
- **Fouten die nog overblijven** (uit de toets):
  - organisatienamen: Jeugdtheater Hofplein, Diergaarde Blijdorp, atv Ommoord;
  - metoniemen: 'Wilhelminaplein' voor de rechtbank, en het briefhoofd met Wilhelminakade (het gemeentekantoor);
  - 'Rotterdam-Noord' gebruikt als 'de noordoever';
  - 2 verkeerd gekoppelde straatnamen.
- **Stadsbrede stukken:** 6.998 stukken noemen 1 gebied en 2.082 noemen er 2. 560 stukken noemen 5 of meer gebieden; die moet je als 'stadsbreed' tonen, niet als 'genoemd in' bij elke wijk.

## Advies: welk niveau tonen

- **Bron en locatie: op wijkniveau**, zonder voorbehoud.
- **Tekst: op wijkniveau, met het label 'genoemd in'.**
  - Bij 5 of meer gebieden: 'stadsbreed'.
  - Gebied = som van de wijken.
- **Buurtniveau niet als eigen laag tonen.** Het is ongeveer gelijk aan de wijk; alleen gebruiken voor kaart en CBS-cijfers.
- **Vóór 2022:** alleen de gebiedsnaam (14 gebieden), niet per wijkraad.
