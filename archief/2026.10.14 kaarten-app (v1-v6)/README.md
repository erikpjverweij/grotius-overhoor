# Grotius Overhoor-app

Overhoorapp voor de Grotius-specialisatieopleiding Onrechtmatige daad & Aansprakelijkheid 2026. Gebouwd als Progressive Web App (PWA) — werkt in elke browser, te installeren op je iPhone-startscherm, werkt offline.

## Structuur

| Bestand                  | Wat                                                                 |
|--------------------------|---------------------------------------------------------------------|
| `index.html`             | De volledige app (HTML + JS + Tailwind via CDN in één bestand)      |
| `cards.json`             | Database met alle overhoorkaarten (gebruikt door GitHub Pages)      |
| `cards.js`               | Zelfde data als JS-variabele (gebruikt bij lokaal openen via file://) |
| `manifest.webmanifest`   | PWA-metadata (naam, iconen, kleuren)                                |
| `sw.js`                  | Service worker voor offline gebruik en cards.json-refresh           |
| `icon-192.png` / `512`   | App-iconen voor op het startscherm                                  |

## Fase 1 — lokaal testen

1. Open de map `C:\Users\ErikVerweij\Claude\Grotius\Algemeen\overhoor-app\` in Windows Verkenner.
2. Rechtermuisklik op `index.html` → "Openen met" → kies een browser (Chrome, Edge, Firefox).
3. Je ziet de app met 10 mock-kaarten over modules 1, 2 en 5.
4. Test: filter toepassen, "Start overhoor", antwoord tonen, "Ken ik" / "Herhalen" klikken, terug naar hoofdmenu.

> Let op: de service worker (offline-ondersteuning) werkt pas als de app via `http(s)://` draait, niet via `file:///`. Voor lokaal testen is dat geen probleem — de app werkt prima lokaal, alleen offline-cache staat nog uit. Kaarten worden lokaal geladen uit `cards.js` (JS-variabele), en op GitHub Pages uit `cards.json` (fetch). De generator schrijft beide altijd tegelijk.

## Fase 2 — op GitHub Pages zetten

### Eenmalig

1. Ga naar https://github.com/new terwijl je ingelogd bent als **erikpjverweij**.
2. Repository-naam: `grotius-overhoor`. Zet op **Public** (anders werkt Pages niet op een gratis account). "Add README" uit laten staan.
3. Open PowerShell of Git Bash in deze map en voer uit:

```bash
cd "C:\Users\ErikVerweij\Claude\Grotius\Algemeen\overhoor-app"
git init
git add .
git commit -m "Fase 1: app-skelet met mock-data"
git branch -M main
git remote add origin https://github.com/erikpjverweij/grotius-overhoor.git
git push -u origin main
```

4. In GitHub: **Settings → Pages → Source → Deploy from branch → `main` / root → Save**.
5. Na ~1 minuut staat de app op `https://erikpjverweij.github.io/grotius-overhoor/`.

### iPhone-installatie

1. Open de URL in **Safari** op je iPhone.
2. Druk op de deelknop (vierkantje met pijltje omhoog).
3. Scrol omlaag → "Zet op beginscherm".
4. De app staat nu als icoon op je startscherm en opent zonder adresbalk, als een echte app.

### Updates

Elke keer als ik (of jij) de app of `cards.json` bijwerkt:

```bash
cd "C:\Users\ErikVerweij\Claude\Grotius\Algemeen\overhoor-app"
git add .
git commit -m "Nieuwe kaarten: module X"
git push
```

GitHub Pages deployt automatisch binnen een minuut. De app laadt `cards.json` "network first" — je ziet nieuwe kaarten zodra je online bent, maar offline kun je blijven werken met de versie die het laatst gecached was.

## Fase 3 en verder

Zie de hoofdplanning in het gesprek. Kaartengeneratie uit PDF-syllabi gebeurt in een apart Python-script in `Algemeen/overhoor-generator/` (nog aan te maken in Fase 3).

## Privacy

- Er is geen backend, geen login, geen tracking.
- Voortgang ("ken ik" / "herhalen") staat alleen lokaal in je browser (`localStorage`). Wissel je van apparaat, dan begin je daar met een blanco voortgang.
- GitHub-repo is public (nodig voor gratis Pages). Als je bang bent dat anderen de kaartenset vinden: die bevat alleen korte citaten uit publieke juridische bronnen en de syllabi zijn leermateriaal dat in de opleiding met alle deelnemers wordt gedeeld. Geen persoonlijke of vertrouwelijke informatie.
