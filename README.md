# Grotius O&A · Rechtspraak-overhoorapp

Overhoorapp voor de verplichte rechtspraak van de Grotius Specialisatieopleiding Onderneming en Aansprakelijkheid 2026. Werkt als PWA op pc en iPhone via GitHub Pages.

Sinds 14 oktober 2026 beperkt tot rechtspraak. De eerdere kaartenapp (439 kaarten met wetsartikelen, rechtsleer en casus) staat in `archief/2026.10.14 kaarten-app (v1-v6)/`.

## Bron

`../2026.08.19 Grotius O&A - Rechtspraak per module.docx` is leidend. Dat document bevat per uitspraak: verwijzing (ECLI + vindplaats), kern, feiten, leerstuk, bepalend artikel met wettekst, rechtsregel in eigen woorden, verband met andere uitspraken en het letterlijke citaat. Bijlage A verantwoordt afwijkingen van de syllabi (onder meer gecorrigeerde ECLI's).

`generator/parse_rechtspraak.py` leest dat document en schrijft `cases.json` en `cases.js`. Na een wijziging in het document: script draaien, cache-versie in `sw.js` verhogen, committen en pushen.

## Bestanden

| Bestand | Functie |
|---|---|
| `index.html` | De app (één bestand: opmaak, logica, vijf oefenvormen) |
| `cases.json` | 214 uitspraken, 20 modules; wordt network-first geladen |
| `cases.js` | Zelfde data als JS-variabele, voor gebruik vanaf `file://` en als offline-fallback; bevat ook de mapnamen van de syllabi voor de knop "Open syllabus" |
| `sw.js` | Service worker. `CACHE_NAME` verhogen bij elke wijziging aan index.html |
| `manifest.webmanifest`, `icon-*.png` | PWA-configuratie |

## Oefenvormen

1. Naam → essentie: naam in beeld, klik "Essentie weergeven", beoordeel jezelf met "Ken ik" of "Ken ik nog niet".
2. Essentie → naam: rechtsregel in beeld, bedenk de naam, klik "Naam weergeven".
3. Meerkeuze naam: rechtsregel in beeld, vier namen.
4. Meerkeuze essentie: naam in beeld, vier rechtsregels.
5. Leerstuk → uitspraken: wetsartikel in beeld, kies alle uitspraken die erbij horen (zes opties, twee tot drie juist).

Afleiders bij meerkeuze komen eerst uit het verband-blok van de uitspraak, dan uit dezelfde module, dan uit uitspraken over hetzelfde artikel. Uitspraken die in twee modules staan, verschijnen nooit als afleider van zichzelf.

Bij elke essentie zijn uitklapbaar: feiten, letterlijk citaat, verband, wettekst, bron (met link naar de syllabus-pdf op de juiste pagina; werkt alleen op de pc waar de Grotius-map staat) en een knop "Vraag Claude" die claude.ai opent met de uitspraak als vraag.

## Voortgang

Per uitspraak: ken ik / ken ik nog niet / nieuw. Opgeslagen in de browser van het apparaat (localStorage). Uitspraken met "ken ik nog niet" komen in een ronde drie keer zo vaak als gekende uitspraken; nieuwe twee keer zo vaak.

Tab "Meer": voortgang per module, en export/import als code om voortgang tussen pc en iPhone over te zetten. Import voegt samen; per uitspraak wint de nieuwste beoordeling.

## Publiceren

GitHub Desktop → repository overhoor-app → wijzigingen controleren → Summary invullen → Commit to main → Push origin. Na ongeveer een minuut staat de nieuwe versie online; op de iPhone de app sluiten en opnieuw openen.
