# Moties en amendementen herkennen in ORI (17-10-2026)

Regels en queries: `moties_regels.json` (alle regexen getest in Python 3.13 met `re.IGNORECASE`; `titel_rx` is een lijst, probeer in volgorde). Basis: documentnamen (`@type` MediaObject, en bij Dordrecht ook AgendaItem) sinds 1-1-2022. Precisie = 30 willekeurige treffers met de hand beoordeeld op "is een ingediende motie".

| gemeente | motie-treffers (uniek) | amend. | precisie | uitslag |
|---|---|---|---|---|
| Amsterdam | 5.695 (3.258) | 686 | 30/30 | in tekst, ca. 50% |
| Den Haag | 5.112 (2.740) | 712 | 30/30 | naam (10%) + tekst (ca. 50%) |
| Eindhoven | 583 (570) | 291 | 30/30 | naam (9%) + slotregel tekst (57%) |
| Dordrecht | 769 (657) | 296 | 30/30 | naam (16%) |
| Vlaardingen | 782 (673) | 460 | 30/30 | naam (27%) |
| Utrecht | 11 (11) | 1 | 11/11 | alleen via lijsten (alleen aangenomen) |

## Per gemeente
- **Amsterdam**: `NNN.JJ Motie <achternaam c.s.> inzake <titel>`; ook `accent`, `_`, `Motie 021 …`. Indieners (achternamen) en titel goed te splitsen. Uitslag staat in het kopblok van het motiedocument (`… | Status | Onderwerp | <datum> | <nr> | Verworpen | …`); bij de rest staat letterlijk "Status" (versie van vóór de stemming). Bijlage-kopieën in raadsvoorstellen zijn uitgesloten.
- **Den Haag**: `K.1 HvDH motie <titel>` of `PvdD.9 motie <titel>`; indiener is een fractie. Staart AANGEHOUDEN/GEWIJZIGD/INGETROKKEN is uitslag. Aangenomen/verworpen alleen uit de tekst ("Uitslag stemming:", bij ca. de helft ingevuld). `RIS… Afdoening motie` is uitgesloten maar goede kruisverwijzing.
- **Eindhoven**: `Titel (Motie M5)`, `VM3 Vrije motie - titel (fracties)`, `Aangenomen Amendement A3 …`. Codes (M1, VM1) herhalen per vergadering: koppel met datum. "Niet ingediend" is uitgesloten.
- **Dordrecht**: `M5  Motie titel.pdf`, `Stemming Motie M5 titel.pdf`, agendapunt `44: M3 Motie Vreemd aan de orde …`. Per motie vaak twee documenten. Indieners staan bijna nooit in de naam. "Stemming"-bladen hebben geen tekstlaag. "Concept …" uitgesloten (ontwerp).
- **Vlaardingen**: `M7. Motie titel - fractie(s) [- aangenomen]`, datumprefix `20250612 Motie …`. Fracties na laatste " - "; bij titels met eigen " - " loopt een stuk titel in `indieners`.
- **Utrecht**: losse moties staan er nauwelijks (11 documenten sinds 2022). Moties zitten wel in 223 PDF-lijsten ("Lijst aangenomen moties …", "Motielijst …", "Lijst toezeggingen-moties-brieven …"): ca. 618 verschillende motiecodes `Mnnn` met indiener, beleidsveld en deadline. Codes zijn betrouwbaar (29/30 in steekproef), titels staan kolomsgewijs over meerdere regels, dus slechts deels bruikbaar. De lijsten bevatten ook moties van vóór 2022. Afdoeningsbrieven geven code + titel. Amendementen: zo goed als niet.

## Zoekvorm
`ori_query` per gemeente: `bool` met filter `@type`, filter `last_discussed_at >= 2022-01-01`, `query_string` op `name` ("motie* OR amendement*") en `must_not` op afdoening/raadsbrief/lijst/overzicht e.d. Daarna de regex client-side. Geen `name.keyword` in ORI, dus regexp-queries op de naam werken niet. Maximaal 10.000 treffers per verzoek: knip op maand (`last_discussed_at` gte/lt). Gemeten recall t.o.v. de brede lokale telling: Amsterdam, Den Haag, Dordrecht 99,7-100%; Eindhoven 96%; Vlaardingen 93,5%; Utrecht 91%.

## Onzekerheden
- Precisie is gemeten op "is het een motie-document", niet op de juistheid van de afgeleide indieners/titel; die zijn alleen steekproefsgewijs bekeken (Amsterdam, Vlaardingen goed; tweedelige achternamen zonder tussenvoegsel gaan mis).
- Elke motie komt meerdere keren voor (meerdere vergaderingen/versies): ontdubbel op (gemeente, code/nummer, datum).
- Recall van de regex zelf is niet gemeten (alleen een steekproef van wat niet gevangen werd: vooral bijlagen, afwijkende schrijfwijzen en moties zonder nummer).
- Uitslag in tekst: bij Amsterdam en Den Haag is een leeg veld niet hetzelfde als "geen uitslag bekend"; nooit uitslag gokken.
- Aannames niet gecontroleerd: dat een afdoeningsbrief alleen bij aangenomen moties hoort (Amsterdam, Den Haag).
