# Umami op de NAS (niet in gebruik)

Sinds 8-10-2026 meet raadzoeker via Umami Cloud (Hobby); zie `ontwerp/meten.md`. Dit is de uitwijkroute als Hobby te krap blijkt (100.000 events per maand, 6 maanden bewaartijd) of als de data niet buiten de eigen server mag. Overstappen = onderaan `host` en `waar` in `docs/meet.js` aanpassen.

Doel: zien hoe raadzoeker gebruikt wordt (pagina's en knoppen), zonder cookies en zonder namen. De site stuurt gebeurtenissen naar Umami via `docs/meet.js`; zolang daar geen host en id staan, gebeurt er niets. Wat er gemeten wordt en hoe je het leest: `ontwerp/meten.md`.

## Opzet in gewone woorden

Umami is een klein programma met een database dat de tellingen bewaart. Het draait op de NAS, naast de bijwerker. Voor bezoekers is er één brievenbus naar buiten (`stats.raadzoeker.nl`) waar alleen het meetscriptje en het inleveradres doorheen mogen. Het dashboard blijft binnen je eigen netwerk.

## Stappen

1. **Mappen en geheimen.** Maak op de NAS `/volume1/docker/umami/` met daarin `db/` en `tunnel/`. Zet `compose.yaml` en een ingevulde `.env` (uit `.env.example`) in `/volume1/docker/umami/`.
2. **Tunnel maken** (eenmalig, op je pc met `cloudflared` geïnstalleerd; dit gaat met de opdrachtregel, niet via het Zero Trust-dashboard):
   - `cloudflared tunnel login` (kies de zone raadzoeker.nl)
   - `cloudflared tunnel create umami` (geeft een tunnel-id en een bestand `<id>.json`)
   - `cloudflared tunnel route dns umami stats.raadzoeker.nl`
   - Zet `<id>.json` en `config.yml` (uit `cloudflared-config.yml.example`, id ingevuld) in `/volume1/docker/umami/tunnel/`.
   - **Niet geverifieerd:** of dit werkt zonder actief Zero Trust-plan op je account. Zero Trust vroeg eerder om een kaart. Loopt `tunnel login` of `tunnel create` daarop vast, stop dan hier en kies Umami Cloud (zie onder).
3. **Starten.** Container Manager → Project → Maken → `compose.yaml` → Bouwen → Starten. Open `http://<nas>:3000`, log in met `admin` / `umami` en **wijzig het wachtwoord meteen**.
4. **Website toevoegen.** Instellingen → Websites → Toevoegen: naam `raadzoeker`, domein `raadzoeker.nl`. Kopieer de **Website-ID**.
5. **Aansluiten.** In `docs/meet.js` bovenaan `CONF`: `host:'https://stats.raadzoeker.nl'` en `id:'<Website-ID>'`; in `ontwerp.js` het versienummer van `meet.js?v=` ophogen; mergen naar `main`. Pas daarna meet de site; op Over verschijnt dan vanzelf de privacytekst met de keuze 'niet meetellen'.
6. **Controleren.** Open `https://raadzoeker.nl/?meet=debug` (toont gebeurtenissen alleen in de browserconsole, verstuurt niets; `?meet=nodebug` zet dat uit). Open daarna een gewone pagina en kijk in Umami → Realtime of je bezoek verschijnt. Test ook dat `http://stats.raadzoeker.nl/` zelf een 404 geeft (de tunnel laat alleen `script.js` en `/api/send` door).
7. **Versie vastzetten.** Noteer de Umami-versie die nu draait (rechtsonder in het dashboard) en zet in `compose.yaml` die tag in plaats van `latest`; upgraden doe je bewust.

## Back-up

De tellingen staan in `/volume1/docker/umami/db`. Neem die map mee in de bestaande NAS-back-up (of `docker exec umami-db pg_dump -U umami umami > umami.sql` voor een dump).

## Alternatief: Umami Cloud

Geen server, geen tunnel: maak een gratis account, voeg `raadzoeker.nl` toe, en zet in `meet.js` `host:'https://cloud.umami.is'`, het id, en pas `waar` aan voor de privacytekst. Alles in de site blijft gelijk. **Controleer vooraf** waar de gegevens staan en of er een verwerkersovereenkomst is, voordat dit voor collega's van de gemeente wordt gebruikt; dat heb ik niet nagegaan.

## Als je ad-blockers wilt omzeilen

Umami kan het script en het inleveradres hernoemen (`TRACKER_SCRIPT_NAME`, `COLLECT_API_ENDPOINT`). Dan ook `CONF.script` in `meet.js` en het pad in `config.yml` aanpassen. Alleen doen als blijkt dat er veel wegvalt.
