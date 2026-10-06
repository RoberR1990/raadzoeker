# Customer-journey-analyse raadzoeker — 6 oktober 2026

Doel: kijken of de site makkelijk en goed werkt vóór de brede livegang, en concrete aanpassingen voorstellen.

## Inhoudsopgave

1. Oordeel in het kort
2. Aanpak en beperkingen
3. Persona's en hun journey
4. Rode draden over alle persona's
5. Jouw losse punten: oordeel en advies
6. Startpagina: drie opties en mijn aanbeveling
7. Navigatie en informatiearchitectuur: voorstel
8. Prioriteitenlijst (voor livegang, kort erna, later)
9. Redesign of niet?

---

## 1. Oordeel in het kort

- **De inhoud is sterk, de schil eromheen hapert.** Dossierpagina's (Parkeren, Handhaving), de wijkpagina, de briefing, volgen en de citaatcontrole kregen van alle persona's 4-5 uit 5. Waar het misgaat: het mobiele menu, de dubbele zoekingang, de Gebieden-ingang en een paar kapotte of inconsistente onderdelen.
- **Geen volledig redesign nodig.** Het inhoudsmodel (dossier, gebied, vergadering, zoeken) klopt met hoe ambtenaren denken. Herzie wel de kop/navigatie, de startpagina en de zoekstroom. Die drie samen voelen voor een bezoeker wel als een nieuwe site.
- **Vóór livegang moeten er 9 dingen opgelost worden** (sectie 8): mobiel menu, zoekstroom, 'Lees het hele debat', de cijfers die tussen dossier, briefing en deelkaart verschillen, de samenvatting bij Dakloosheid, irrelevante vergaderverslagen bovenaan Zoeken, deellinks zonder voorvertoning, klikbare matrix en de kop die op twee regels valt.

## 2. Aanpak en beperkingen

- Vijf persona's, elk gespeeld door een aparte subagent (Sonnet). Die klikte met Playwright door de lokale kopie van de site, op desktop (1440×900) en mobiel (390×844), en voerde 5-7 concrete taken uit. Daarnaast een mechanische toegankelijkheidsaudit met axe-core (Haiku) en een bronnenonderzoek naar startpagina's en hero's (Sonnet).
- De ruwe rapporten staan niet in git, alleen in de scratchpad van deze sessie. Dit document is de samenvatting.
- **Beperkingen.** Dit zijn gesimuleerde gebruikers, geen echte, dus het is een expert-review in persona-vorm. Toets de 3-4 grootste punten met 5 echte collega's (30 minuten per persoon, hardop denken). De toegankelijkheidsaudit was deels onbetrouwbaar: Haiku verzon een journey erbij en verwisselde dingen. Hieronder staan alleen de axe-telling en metingen die ik heb kunnen controleren of die door andere agents bevestigd zijn. Laadtijden zijn lokaal gemeten en zeggen dus weinig over 4G.

## 3. Persona's en hun journey

Score per taak: 1 = lukt niet, 5 = moeiteloos.

### A. Beleidsmaker: wil parkeren bijhouden (laptop, soms telefoon)
| Taak | Score | Opmerking |
|---|---|---|
| Dossier Parkeren vinden | 4 | Via wolk of chip in 1 klik |
| Wat is er net besproken | 5 | 'Net besproken' staat bovenaan het dossier |
| Toezeggingen over de termijn | 4 | 3 klikken; gesorteerd op datum in plaats van achterstand (754 dagen staat onder 502) |
| **Wat staat de komende weken op de agenda** | **2** | 'Komt eraan' toont afdoeningsdata, geen vergaderingen. `verg/vooruit.json` heeft bij geen enkel punt een gekoppeld dossier, dus ook de agenda op Vergaderingen helpt niet |
| Volgen en terugkomen | 4 | Werkt, maar alleen in deze browser; geen e-mail |
| Delen via Teams | 4 | Werkt; geen voorvertoning (zie D) |

Breekpunt: vooruitkijken per dossier.

### B. Adviseur/projectleider: wil zich een dossier eigen maken
| Taak | Score | Opmerking |
|---|---|---|
| Handhaving lezen (voorbeelddossier) | 5 | Kern, stappen, akkoord, citaten: 'precies het overzicht dat ik zocht' |
| **Dakloosheid (geen voorbeelddossier)** | **2** | 'In het kort' gaat over ouderenbeleid, mantelzorg en dierenwelzijn: de domeintekst van Zorg, welzijn & jeugd staat bij een onderwerp |
| Citaat tot de bron volgen | 5 | Zin aanwijzen geeft spreker, datum en vergadering |
| Wat zei fractie X | 3 | Filter werkt, maar staat onder de resultaten |
| Akkoord | 4-5 | Ook per dossier, met paginalink |
| Briefing | 4 | Cijfers wijken af van het dossier (19 tegenover 8+6 open; 43 tegenover 45 aangenomen); akkoord en rekenkamer ontbreken |
| Verkenner | 3 | Interessant, maar geen vervolgstap voor een adviseur |

Breekpunt: de kwaliteit zakt sterk zodra je buiten de 3 voorbeelddossiers komt, en dat zie je niet aan de pagina.

### C. Wijk-/gebiedsmedewerker Feijenoord (vooral telefoon)
| Taak | Score | Opmerking |
|---|---|---|
| Feijenoord via matrix | 2 | Kolomkop niet klikbaar; vakjes 15×19 px op mobiel |
| Feijenoord via wolk | 4 | Wel moet je raden dat blauw 'gebied' betekent |
| Feijenoord via zoeken | 3 | Komt uit op `dossier.html#feijenoord`, een andere pagina dan `wijk.html#feijenoord` |
| Via menu Gebieden | 2 | Opent op Charlois; wisselen alleen via kaart of zoekveld |
| Gebiedspagina lezen | 3 | 10.800 px lang op mobiel zonder ankers; 'Wijken in Feijenoord' pas op 7.841 px |
| Wijkpagina Afrikaanderwijk | 4 | Rijk: raad, wijkraadagenda, bekendmakingen, cijfers |
| Vergelijken met ander gebied | 2 | Bestaat niet op de gebiedspagina |
| Wijkraadvergaderingen | 2 | Op Vergaderingen alleen via Archief › maand |
| Briefing en volgen | 5 | Gebied staat al geselecteerd; volgen werkt. Briefing scrolt op mobiel wel horizontaal (421 px) |

Breekpunt: de ingang. De inhoud is goed, maar je komt er moeilijk.

### D. Nieuwsgierige burger (komt via een gedeelde link op de telefoon)
| Taak | Score | Opmerking |
|---|---|---|
| Binnenkomen via dossierlink | 4 | Welkomstvenster is kort en duidelijk |
| Menu gebruiken | 2 | Loopt rechts uit beeld: Verkenner, Inzichten en Over niet te zien |
| Startpagina snappen | 3 | Duidelijk wat het is, maar 'tekst en cijfers, geen beeld' |
| Zoeken 'Coolsingel' | 2 | Resultaten pas na 4 schermen filters |
| Verkenner | 4 | 'Dit is de wow', laadt in 0,8 s; labels overlappen bij uitzoomen |
| Inzichten / Wrapped | 2 | Wrapped staat onderaan (y≈4.975) met afgekapte kaarten |
| Delen | 3 | Link geeft geen voorvertoning: deelknoppen wijzen naar `dossier.html?d=…` zonder og-tags, terwijl `deel/<slug>.html` wel bestaat. Deelkaart Parkeren zegt 'Beleidsdomeinen' en toont oude cijfers (14/5 tegenover 28/6) |
| Rondleiding | 3 | 14 stappen is te lang |

Breekpunt: mobiel menu en zoekresultaten. En wat gedeeld wordt, ziet er kaal of verouderd uit, terwijl delen jullie groeimotor is.

### E. Fractiemedewerker/journalist (power-user, desktop)
| Taak | Score | Opmerking |
|---|---|---|
| Exacte zin via startpagina | 2 | Enter gaat naar een dossier, niet naar citaten |
| Exacte zin via Zoeken | 3-4 | Werkt goed ('260 keer, eerste 300 gecontroleerd'), maar citaten staan onder de AI-verslagen en de overzichten |
| Filters fractie/spreker/periode | 5 | Staan in de URL, dus deelbaar |
| Of-zoeken | 4 | Werkt |
| Videomoment | 3 | Eerst Start, dan 'Spring naar'; tijdstip 'bij benadering' |
| **'Lees het hele debat'** | **1** | Opent niets: versmalt alleen het jaarfilter |
| Motie met stemuitslag | 2-3 | In Zoeken geen uitslag of status; stemtabel alleen in 3 voorbeelddossiers |
| Vragen + antwoord | 4 | Goed |
| Vergaderingen | 4 | Tijd en ▶ per agendapunt, uitkomst |
| 'bijgewerkt' | 2 | Gaat naar een FAQ-item |

Breekpunt: de zoekstroom en de link naar het debat. Ook de sprekerlijst moet opgeschoond worden: op voornaam gesorteerd, dubbelingen als 'Chantal Zeegers' en '… College', en 'Inspreker 1..23'.

## 4. Rode draden over alle persona's

1. **Mobiel menu kapot** (A, B, C, D): het menu loopt buiten beeld, er is geen hamburger, en 4 van de 8 menu-items zijn onvindbaar. Grootste probleem voor een site die via WhatsApp en Teams wordt gedeeld.
2. **Twee zoekingangen die elk iets anders doen** (B, C, E): de startpagina springt naar een dossier, Zoeken toont citaten. Niemand snapt het verschil.
3. **Inconsistente cijfers** (B, D): dossier, briefing en deelkaart tellen 'open' en 'aangenomen' verschillend, of zijn van een andere datum. Een ambtenaar die zijn leidinggevende een briefing geeft en daarop wordt tegengesproken, komt niet terug.
4. **Kwaliteitsval buiten de voorbeelddossiers** (B, E): stemtabellen, beloftespoor en een goede samenvatting zijn er alleen bij Parkeren, Handhaving en Wonen. Elders staat soms een verkeerde samenvatting (Dakloosheid).
5. **Gebieden moeilijk bereikbaar** (A, C, D): matrix niet klikbaar, Gebieden opent op Charlois, één gebied heeft twee pagina's.
6. **Wat goed werkt, unaniem:** citaat bij elke AI-zin, AI-labels, volgen met ster, briefing met één klik, deelbare URL's met filters, welkomstvenster, 'Bedoel je…', neutrale toon bij cijfers.

## 5. Jouw losse punten: oordeel en advies

| # | Jouw punt | Bevestigd? | Advies |
|---|---|---|---|
| 1 | Gebieden opent op Charlois, kaart neemt veel ruimte | Ja (A, C, D) | `wijk.html` zonder hash wordt een **overzichtspagina**, geen Charlois. Bovenaan: titel 'Gebieden', zoekveld 'wijk, straat of gebied', daaronder 14 gebiedsknoppen (op mobiel 2 kolommen) met per gebied 1 regel ('3 moties open · Tarwewijk, Carnisse…'). De kaart wordt een compacte kaart ernaast (desktop, max 280 px hoog) of klapt in onder 'Toon op kaart' (mobiel). Heb je een gebied gevolgd of eerder bezocht, dan staat dat bovenaan als 'Jouw gebied'. Op een gebiedspagina komt een vaste kiezer 'Gebied: Feijenoord ▾' naast de titel. |
| 2 | Logo onvoldoende herkenbaar | Ja; nu 46×35 px wit op groen, details vallen weg | Korte termijn: icoon 40 px hoog en woordmerk 22 px. Beter: een nieuw, eenvoudiger beeldmerk dat ook op 16 px werkt. Advies uit de vorige review: halfrond van stippen (raadzaal) met één groene stip, of een woordmerk met een loep in de 'oo'. Het huidige logo heeft te veel details (ring, spreekgestoelte, loep) voor een kopbalk. |
| — | 'onofficieel' te prominent | Deels | Kleiner mag (12 px, 70% wit, zonder scheidingsstreep), maar **niet weghalen**. De site gebruikt de officiële huisstijl, en dit woord voorkomt dat mensen hem voor de gemeente aanzien. Juridisch en voor het vertrouwen is dat het belangrijkste woord in de kop. Op mobiel valt het nu helemaal weg; zet het daar in de voettekst en het menu. |
| 3 | 'Inhoudsopgave' op 2 regels en geen toegankelijkheid | Ja. Ik ga ervan uit dat je de **menubalk** bedoelt: zodra je iets volgt verschijnt ★ en valt de kop op 1440 px op twee regels (132 px hoog; screenshot gemaakt). De meelopende inhoudsbalk in dossiers bestaat in de huidige indeling niet meer. | Kop opnieuw opbouwen (sectie 7): minder items zodat hij nooit wrapt, met `aria-current="page"` op het actieve item, een zichtbare focusring en een hamburger onder ca. 900 px. axe vond verder 9 contrastfouten (grijs op lichtgrijs, onder andere labels en meta) en een kopjessprong h1→h3 in dossiers. |
| 4 | 'bijgewerkt' moet een logboek tonen | Ja; nu linkt het naar FAQ `over.html#actueel` | Pagina `nieuw.html`: laatste 3 dagen, maximaal 50 regels, per run 'wat kwam erbij' ('+3 vergaderingen, +12 collegebrieven, +2 moties, samenvatting raad 1 okt'). Technisch: `bijwerken.sh` schrijft nu alleen `{laatste, modus, ok}`; laat het na elke run tellingen vergelijken met de vorige stand (de bestanden bestaan al: `verg/`, `volg.json`, stukken) en een regel aanhangen aan `docs/data/logboek.json` (afkappen op 50). Klein werk, en het geeft een reden om terug te komen. |
| 5 | Verkenner onder Inzichten, maar prominenter | Gedeeltelijk mee eens | De burger noemde de Verkenner 'het echte wow-moment'. Verstop hem dus niet in een submenu. Advies: Inzichten wordt een **hub** met bovenaan een grote, live Verkenner-tegel (mini-web met 'Verras me'), daaronder Wrapped (nu onderaan en afgekapt) en dan de grafieken. Uit het hoofdmenu mag hij, maar alleen als hij ook op de startpagina terugkomt (optie A/B hieronder). |
| 6 | Startpagina te weinig wow | Ja (D, hero-onderzoek) | Zie sectie 6. |
| 7 | Gebiedsnamen in 'Waar speelt wat?' klikbaar | Ja, alle 5 bevestigd (kolomkoppen zijn `<span>`) | Kolomkoppen linken naar `wijk.html#<gebied>`. Op mobiel is de matrix met vakjes van 15×19 px onbruikbaar: toon daar een lijst 'Kies gebied' of 'Kies domein' en laat de matrix weg. |
| 8 | Zoeken dubbel met de startpagina en minder functioneel | Ja (B, E). Maar de oorzaak zit omgekeerd: Zoeken is het betere gereedschap, de startpagina stuurt alleen verkeerd door | Eén zoekstroom. Startpagina en kopbalk sturen bij Enter altijd naar de resultatenpagina (`zoek.html?q=`). Daar staat bovenaan **één regel** 'Dossier: Betaald parkeren ›' (als er een match is), dan direct de citaten. De filters klappen in achter een knop 'Filters (2)' en 'Uit de vergaderverslagen' en 'In één oogopslag' komen in een smalle zijkolom of klappen in. Tijdens het typen verschijnt een suggestielijst (dossiers, gebieden, sprekers) waarmee je direct naar een pagina springt. Daarna wordt 'Zoeken' als menu-item overbodig: het zoekveld zit in de kop van elke pagina. |

## 6. Startpagina: drie opties en mijn aanbeveling

Lessen uit onderzoek (NN/g, Baymard, WCAG 2.2.2, TheyWorkForYou, Our World in Data, Spotify Wrapped):
- **Geen carrousel en geen automatisch roterende hero.** Een paneel is maar ca. 20% van de tijd zichtbaar, ca. 1% klikt, en 84% daarvan op dia 1. Een 'Netflix-hero' moet dus één statisch uitgelicht ding zijn.
- **Wow komt uit echte inhoud met een pointe, niet uit effecten.** TheyWorkForYou zet een echt debatfragment op de voorpagina; Wrapped werkt door herkenning en delen.
- **'Deze week' in plaats van 'sinds 2018'.** Dat geeft een reden om terug te komen.
- **Beweging moet pauzeerbaar zijn en `prefers-reduced-motion` respecteren.**

Bronnen: nngroup.com/articles/auto-forwarding, nngroup.com/articles/page-fold-manifesto, nngroup.com/articles/homepage-design-principles, baymard.com/blog/homepage-carousel, theyworkforyou.com, ourworldindata.org.

### Optie A — 'Deze week in de raad' (nieuwsfront met citaat-hero). Inspanning S-M
- **Boven de vouw (desktop):** brede groene band. Links een groot letterlijk citaat uit de laatste vergadering (28-32 px, enkele aanhalingstekens), met spreker, fractie, datum, '▶ Bekijk het moment' en 'Hele vergadering'. Rechts 'Komt eraan' met 3 regels. Daaronder het zoekveld met suggesties en chips. Onderaan net zichtbaar de rij 'Net besloten'.
- **Mobiel:** citaatkaart van maximaal 5 regels, zoekveld, chips, en het begin van 'Komt eraan'.
- **Data:** bestaat al: `verg/zoek.json`, `verg/koppel.json`, `verg/vooruit.json`. Citaatkeuze met een vaste regel, alleen uit mechanisch gecontroleerde citaten. 'Ander citaat' alleen op klik.
- **Wow:** echtheid. Je hoort de raad binnen 3 seconden.
- **Risico:** een citaat zonder context. Daarom altijd fractie en een link naar het hele fragment, en spreiding over fracties bewaken. In automatische ondertitels staat soms de verkeerde spreker; kies dus alleen citaten uit notulen of gecontroleerde samenvattingen.

### Optie B — 'Kies je dossier' (Netflix-achtig). Inspanning M
- Compact zoekveld bovenaan, daaronder een groot uitgelicht dossier van de week (groen vlak, 3 getallen, 'Open dossier', '☆ Volg') en rijen: 'Net besloten', 'Beloftes over de termijn', 'Dossiers in beweging', 'Per gebied'.
- **Wow:** herkenbaar Netflix-gevoel; een ambtenaar ziet direct 'zijn' dossier.
- **Risico:** horizontale rijen worden vaak gemist en zijn lastig met toetsenbord. Alleen 3 dossiers zijn echt rijk, dus de rest voelt leeg. 'Dossier van de week' is een redactionele keuze, dus onderhoud.

### Optie C — 'Jouw plek' (levende kaart als hero). Inspanning M-L
- Kaart van de gebieden en wijken als hero, met het zoekveld 'Je wijk of straat…'. Tik je op een wijk, dan opent een paneel met 3 laatste punten. Bij binnenkomst speelt de kaart één keer 2018→2026 af.
- **Wow:** de hoogste, en een persoonlijk haakje voor burgers.
- **Risico:** zwaar op telefoons. Kleuren naar aandacht lezen als een oordeel, en dat botst met jullie eigen regel 'geen stellige uitspraken'. Ambtenaren denken in dossiers, niet in kaarten. Een kaart alleen is ook niet toegankelijk.

### Aanbeveling: A, met één rij uit B
A bewijst in één scherm wat de site anders maakt (echte woorden, videomoment, wat er nu speelt). Het is het lichtste qua prestaties en toegankelijkheid, en de data bestaat al. Voeg onder het zoekveld één rij 'Dossiers in beweging' toe (uit `volg.json`, als gewone lijst of raster, niet horizontaal scrollen) voor de ambtenaar. Zet daaronder een **Verkenner-tegel** als tweede wow (een stilstaand mini-web, 'Verras me' op klik). De woordwolk en de matrix gaan naar Inzichten en Gebieden: ze zijn nu de helft van de startpagina, maar voor geen enkele persona de beste ingang. Kaart C bewaren voor 'Mijn wijk' op de Gebieden-overzichtspagina.

Over 'professioneel maar geen wow': de huisstijl (groen, wit, Arial, geen kapitalen) laat weinig ruimte voor flair. Wow moet dus uit **schaal en ritme** komen: één groot citaat in plaats van vier gelijke tegels, ruim wit, één groen vlak per scherm, en echte beelden van de stad. Rotterdam heeft open fotomateriaal, maar check de licentie. Niet uit animaties.

## 7. Navigatie en informatiearchitectuur: voorstel

Nu: Zoeken · Vergaderingen · Domeinen · Gebieden | ★ · Verkenner · Inzichten · Over · bijgewerkt · ? (9-10 items, wrapt, onbruikbaar op mobiel).

Voorstel:
```
[logo raadzoeker · onofficieel]  [ Zoek in raad, stukken, dossiers…  / ]   Dossiers  Gebieden  Vergaderingen  Inzichten   ★3  ?
```
- **Zoekveld in de kop** vervangt het menu-item Zoeken (met de toets '/', die al bestaat).
- **'Domeinen' hernoemen naar 'Dossiers'.** Het woord 'domein' kwam bij geen enkele persona terug; iedereen zei 'dossier'. Het is ook jullie eigen redesign-principe: ambtenaren denken in dossiers.
- **Inzichten** = hub met Verkenner bovenaan, Wrapped en grafieken.
- **Over, Hulp, 'bijgewerkt' en Privacy** naar de voettekst en het ?-menu. In de kop blijft alleen een klein klokje met een stip als er iets nieuw is, dat linkt naar `nieuw.html`.
- **Mobiel (<900 px):** logo, zoekicoon, ★ en 'Menu'. Het menu opent als een paneel met de 4 hoofditems en de voettekstlinks. Overweeg een onderbalk met 4 iconen (Zoek, Dossiers, Gebieden, ★).
- **Eén pagina per gebied:** `dossier.html#feijenoord` doorsturen naar `wijk.html#feijenoord`, of samenvoegen.
- **Toegankelijkheid van de kop:** `aria-current="page"`, een focusring van 3 px zwart plus 6 px wit, het menupaneel met `aria-expanded`, en minimaal 44 px klikvlak.

## 8. Prioriteitenlijst

### Vóór livegang (moet)
| # | Wat | Waarom | Inspanning |
|---|---|---|---|
| 1 | Mobiel menu (hamburger of paneel) en een kop die op desktop nooit wrapt | 4 van 8 menu-items onvindbaar op mobiel; kop van 132 px na Volgen | S |
| 2 | Eén zoekstroom: Enter gaat altijd naar resultaten, dossier als bovenste regel; citaten eerst, filters inklapbaar | Punt 8; mobiel 4 schermen tot het eerste resultaat | M |
| 3 | 'Lees het hele debat' → `vergadering.html?id=…` op het agendapunt | Werkt nu niet | S |
| 4 | Eén telregel voor 'open', 'te laat' en 'aangenomen' in dossier, briefing en deelkaart; deelkaarten opnieuw maken in de nachtelijke run | Tegenstrijdige cijfers schaden het vertrouwen | S-M |
| 5 | Onderwerp zonder eigen samenvatting: geen domeintekst tonen, maar 'Nog geen samenvatting voor dit onderwerp' | Dakloosheid toont dierenwelzijn | S |
| 6 | 'Uit de vergaderverslagen' alleen tonen bij een echte treffer in de tekst | Irrelevante bovenste resultaten | S |
| 7 | Deelknoppen en 'Kopieer link' naar `deel/<slug>.html` (met og-tags) laten wijzen; label 'Dossier' in plaats van 'Beleidsdomeinen' | Voorvertoning is de groeimotor | S |
| 8 | Matrix: kolomkoppen klikbaar; op mobiel een lijst in plaats van de matrix | Punt 7 | S |
| 9 | Contrast: 9 axe-fouten (grijze meta-tekst donkerder, min. 4,5:1), kopjesvolgorde in dossiers | Toegankelijkheid voor een gemeentelijk publiek | S |

### Kort erna
- Gebieden-overzicht in plaats van Charlois, met gebiedskiezer en een compacte kaart (punt 1).
- Startpagina optie A met de rij 'Dossiers in beweging' en de Verkenner-tegel (punt 6).
- `nieuw.html` en `logboek.json` (punt 4).
- Menu naar 4 items, 'Domeinen' wordt 'Dossiers', Inzichten als hub met Verkenner en Wrapped bovenaan (punt 5).
- Nieuw beeldmerk; 'onofficieel' kleiner (punt 2).
- 'Op de agenda' per dossier: `vooruit.json` aan dossiers koppelen, ook als er niets gepland is ('niets de komende 3 weken'); filter 'Alleen wat ik volg' op Vergaderingen.
- 'Over de termijn' sorteren op achterstand.
- Gebiedspagina: ankerbalk (Kort · Wijken · Moties · Debatten · Wijkraden · Cijfers), wijkenlijst en kerncijfers hoger, 's/f/v' voluit schrijven.
- Rondleiding naar maximaal 5 stappen; het balkje 'korte uitleg?' pas na de eerste scroll.
- Briefing op mobiel zonder horizontale scroll; akkoord en rekenkamer erin.

### Later
- Moties in Zoeken met uitslag, status en een knop 'officiële tekst'; stemtabel ook voor dossiers buiten de 3 voorbeelden en voor verworpen moties.
- Sprekerlijst opschonen (achternaam, rol, dubbelingen samenvoegen); knop 'kopieer citaat met bron'.
- Volgen draagbaar maken: wekelijkse e-mail of een deelbare volglijst.
- Gebieden vergelijken (2 kolommen; de Verkenner kan dit al).
- Wijkraadvergaderingen als filter op Vergaderingen.
- Videomoment: directe link met tijdstempel.

## 9. Redesign of niet?

**Geen volledig redesign.** Wel een herziening van de schil in 2-3 weken werk:
(1) kop en navigatie, (2) zoekstroom, (3) startpagina A, (4) Gebieden-overzicht.

De dossier-, wijk-, vergader- en briefingpagina's blijven inhoudelijk zoals ze zijn; daar zit de waarde, en de persona's gaven ze de hoogste scores. Een volledige redesign kost veel en lost het echte risico niet op: inconsistente cijfers en een wisselende kwaliteit buiten de voorbeelddossiers. Dat zijn data- en pijplijnzaken (punten 4-6 van de lijst), en die zie je in geen enkel ontwerp terug totdat een gebruiker erover struikelt.

**Voorgestelde review-gate:** eerst de 9 punten 'vóór livegang' (fase A). Daarna een schets van startpagina A en de nieuwe kop als klikbaar ontwerp in `docs/ontwerp/` (fase B). Toets die met 5 collega's uit de vier doelgroepen, en bouw pas daarna.
