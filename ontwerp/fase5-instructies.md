# Fase 5: stemmen en zoeklog aanzetten (eenmalig, ca. 10 minuten)

De pagina Ideeën en de zoeklog werken al zonder database: Ideeën toont dan de lijst zonder stemknoppen ("Stemmen is nog niet actief") en de zoeklog doet niets. Zodra de database gekoppeld is, werkt alles vanzelf.

## Stappen in het Cloudflare-dashboard

1. **Database maken.** Workers & Pages → D1 SQL Database → *Create*. Naam: `raadzoeker`.
2. **Tabellen en ideeën vullen.** Open de database → tab *Console*. Plak de inhoud van `db/schema.sql` uit de repo en klik *Execute*. Daarmee komen er 3 tabellen en 11 ideeën in.
3. **Koppelen aan de site.** Workers & Pages → project `raadzoeker` → *Settings* → *Bindings* (of *Functions* → *D1 database bindings*) → *Add* → D1 database:
   - Variable name: `DB`
   - Database: `raadzoeker`
   - Doe dit voor *Production* (en eventueel *Preview*).
4. **Opnieuw publiceren.** *Deployments* → bij de laatste deployment *Retry deployment* (of laat mij een kleine wijziging pushen).
5. **Controleren.** Open https://raadzoeker.pages.dev/ontwerp/ideeen.html. Boven de lijst staat nu "Je hebt nog 3 stemmen".

## Hoe het werkt

- `functions/api/ideeen.js`: lijst en stemmen. Wie je bent komt uit Cloudflare Access (header `Cf-Access-Authenticated-User-Email`); opgeslagen wordt alleen een SHA-256-hash, geen e-mailadres. Maximaal 3 stemmen op ideeën die nog niet gebouwd zijn; intrekken kan altijd; bij status *gebouwd* komt de stem vrij.
- `functions/api/log.js`: anonieme zoeklog (zoekopdracht, aantal resultaten, pagina, dag). Geen persoon, geen tijdstip.
- Een idee op *gepland* of *gebouwd* zetten: in de D1-console `UPDATE ideeen SET status='gebouwd' WHERE id=…;`
- Zoekopdrachten zonder resultaat bekijken: `SELECT q, COUNT(*) n FROM zoeklog WHERE n=0 GROUP BY q ORDER BY n DESC;`
