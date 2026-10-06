# Opdracht: samenvatting van één vergadering van de Rotterdamse gemeenteraad of een raadscommissie

Je maakt twee samenvattingen van één vergadering voor een site voor ambtenaren en inwoners: een korte (1 minuut lezen) en een uitgebreide (5 tot 9 minuten lezen).

Lees het hele invoerbestand met de Read-tool (in delen met offset/limit als het lang is; lees ALLES voordat je schrijft). Het bestand bevat per agendapunt de beurten: `#U<nr> [h:mm:ss] Naam (Fractie): tekst`. Het is automatische ondertiteling: er staan herkenningsfouten in en `[…]` betekent ingekort. Agendapunten met "(procedureel, niet samenvatten)" sla je over.

Schrijf daarna met de Write-tool het uitvoerbestand: geldige JSON met precies deze vorm:

{
 "kort": [ {"zin": "<één zin>", "u": "U<nr>", "citaat": "<6 tot 20 woorden letterlijk uit die beurt>"} ],
 "agendapunten": [
  {"nr": "<nummer uit de kop, bv. 9.4>",
   "titel": "<korte titel in gewone taal, max 8 woorden>",
   "wat": "<2 tot 3 zinnen: waar ging het over en wat was de kern van het debat>",
   "fracties": [ {"wie": "<fractienaam precies zoals tussen haakjes in de bron>", "punt": "<één zin: wat deze fractie vond of vroeg>", "u": "U<nr>", "citaat": "<6 tot 25 woorden letterlijk>"} ],
   "college": [ {"wie": "<naam zoals in de bron, bv. Chantal Zeegers>", "punt": "<één zin: reactie of standpunt van wethouder/burgemeester>", "u": "U<nr>", "citaat": "<6 tot 25 woorden letterlijk>"} ],
   "uitkomst": "<één zin over de afloop, alleen als die letterlijk blijkt (motie aangenomen/verworpen, voorstel ingediend, vervolg afgesproken); anders lege string>",
   "toezeggingen": [ {"wat": "<één zin: wat het college beloofde>", "u": "U<nr>", "citaat": "<6 tot 25 woorden letterlijk>"} ]
  }
 ]
}

Regels:
- Nederlands, neutraal en zakelijk, gewone taal, korte zinnen. Geen oordeel, geen bijvoeglijke naamwoorden als 'fel' of 'sterk', geen ranglijst van fracties.
- Gebruik ALLEEN wat in de bron staat. Verzin niets en vul niets aan uit eigen kennis. Noem geen cijfers tenzij ze letterlijk in de bron staan.
- "kort": 5 tot 7 zinnen samen ongeveer 120 tot 160 woorden; de belangrijkste onderwerpen en uitkomsten van de hele vergadering.
- "agendapunten": alle inhoudelijke punten, in de volgorde van de vergadering. Per punt hooguit 6 fracties (de duidelijkste bijdragen) en hooguit 2 collegeleden. Samen ongeveer 1.000 tot 1.600 woorden voor een raadsvergadering, minder voor een korte commissie.
- "citaat" moet tekens-voor-teken gekopieerd zijn uit de beurt met dat #U-nummer (zelfde woorden, volgorde en leestekens), zonder de naam ervoor en zonder `[…]`. Kies een stuk zonder herkenningsfouten. Beweringen waarvan het citaat niet letterlijk in díe beurt staat, worden na afloop automatisch geschrapt. Kun je geen citaat vinden, laat de bewering dan weg.
- "wie" bij fracties: alleen de fractie uit die beurt. Een beurt zonder fractie (voorzitter, adviseur, inspreker) hoort niet bij "fracties". Insprekers en ambtenaren noem je niet bij naam.
- Lees GEEN andere bestanden dan het invoerbestand.

Antwoord na het schrijven alleen met het pad van het uitvoerbestand.
