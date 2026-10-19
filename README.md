# Grotius O&A · Rechtspraak-overhoorapp

Overhoorapp voor de verplichte rechtspraak van de Grotius Specialisatieopleiding Onderneming en Aansprakelijkheid 2026. Werkt als PWA op pc en iPhone via GitHub Pages.

Sinds 14 oktober 2026 beperkt tot rechtspraak. De eerdere kaartenapp (439 kaarten met wetsartikelen, rechtsleer en casus) staat in `archief/2026.10.14 kaarten-app (v1-v6)/`.

## Bron

`../2026.08.19 Grotius O&A - Rechtspraak per module.docx` is leidend. Dat document bevat per uitspraak: verwijzing (ECLI + vindplaats), kern, feiten, leerstuk, bepalend artikel met wettekst, rechtsregel in eigen woorden, verband met andere uitspraken en het letterlijke citaat. Bijlage A verantwoordt afwijkingen van de syllabi (onder meer gecorrigeerde ECLI's).

`generator/parse_rechtspraak.py` leest dat document en schrijft `cases.json` en `cases.js` (vereist Python met `python-docx`). Na een wijziging in het document: `python generator/parse_rechtspraak.py` draaien vanuit de map overhoor-app, `CACHE_NAME` in `sw.js` verhogen, committen en pushen. Verbanden tussen uitspraken worden herkend op de naam zoals die in het verband-blok staat, ook zonder toevoeging tussen haken; Deloitte/Hassink wordt genoemd maar is geen eigen uitspraak in het document en blijft dus zonder link.

## Bestanden

| Bestand | Functie |
|---|---|
| `index.html` | De app (één bestand: opmaak, logica, vijf oefenvormen) |
| `cases.json` | 190 unieke uitspraken, 19 modules (alleen uitspraken uit de jurisprudentielijsten van de syllabi; module 22 heeft geen voorgeschreven rechtspraak). Een uitspraak die in meer modules staat is één kaart met alle modules in `modules` en de rechtsregel uit de andere module in `invalshoeken` |
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

Bij elke essentie zijn uitklapbaar: feiten, letterlijk citaat, verband (uitgaand én inkomend, klikbaar), wettekst, bron en een knop "Vraag Claude" die claude.ai opent met de uitspraak als vraag. De bron noemt de pdf-pagina van de syllabus; een klikbare link naar de pdf verschijnt alleen als `index.html` rechtstreeks vanaf de pc wordt geopend (browsers staan geen link van een website naar een lokaal bestand toe).

Na het pushen van een nieuwe versie haalt de app die bij de volgende opening zelf op en herlaadt één keer; tijdens een ronde wacht hij daarmee tot de ronde klaar is.

## Dubbele uitspraken

De generator voegt vermeldingen met dezelfde ECLI samen tot één kaart (14 vermeldingen, onder meer Vivat/ATF = Soldeermachine, Opsluiting in vriescel = B/Br, en de drie deelregels van de overzichtsuitspraak planschade). Die kaart doet mee bij elke module waarin de uitspraak voorkomt. Afwijkende rechtsregels uit de andere module staan als extra blok bij de essentie; andere roepnamen staan onder de naam en zijn doorzoekbaar. De app zet eerdere voortgang van de verdwenen kaarten automatisch over (lijst `samengevoegd` in cases.json).

## Voortgang

Per uitspraak: ken ik / ken ik nog niet / nieuw. Opgeslagen in de browser van het apparaat (localStorage). Uitspraken met "ken ik nog niet" komen in een ronde drie keer zo vaak als gekende uitspraken; nieuwe twee keer zo vaak.

Tab "Meer": voortgang per module, en export/import als code om voortgang tussen pc en iPhone over te zetten. Import voegt samen; per uitspraak wint de nieuwste beoordeling.

## Publiceren

GitHub Desktop → repository overhoor-app → wijzigingen controleren → Summary invullen → Commit to main → Push origin. Na ongeveer een minuut staat de nieuwe versie online; op de iPhone de app sluiten en opnieuw openen.
