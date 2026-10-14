#!/usr/bin/env python3
"""Parse '2026.08.19 Grotius O&A - Rechtspraak per module.docx' naar cases.json."""
import json, re, sys
from pathlib import Path
from docx import Document

"""
Gebruik:  python parse_rechtspraak.py [pad naar Grotius-map]
Standaard: de Grotius-map twee niveaus boven dit script (Grotius/Algemeen/overhoor-app/generator/).
Schrijft cases.json en cases.js in de overhoor-app-map. Verhoog daarna CACHE_NAME in sw.js.
"""
HERE = Path(__file__).resolve().parent
GROTIUS = Path(sys.argv[1]) if len(sys.argv) > 1 else HERE.parent.parent.parent
SRC = GROTIUS / 'Algemeen' / '2026.08.19 Grotius O&A - Rechtspraak per module.docx'
OUT = HERE.parent / 'cases.json'
OUT_JS = HERE.parent / 'cases.js'

d = Document(str(SRC))
paras = d.paragraphs

# Module-titels en docenten
modules = {}
cases = []
cur_mod = None
cur_mod_title = None
i = 0
n = len(paras)

def txt(p):
    return p.text.strip()

# Verzamel blokken per Heading 3
blocks = []
cur = None
for idx, p in enumerate(paras):
    style = p.style.name
    t = txt(p)
    if style == 'Heading 1':
        m = re.match(r'Module (\d+)\s*[—–-]\s*(.+)', t)
        if m:
            cur_mod = m.group(1).zfill(2)
            cur_mod_title = m.group(2).strip()
            modules[cur_mod] = {'titel': cur_mod_title, 'docent': ''}
        else:
            cur_mod = None
        if cur: blocks.append(cur); cur = None
        continue
    if cur_mod and style == 'Normal' and t.startswith('Docent:') and not cur:
        m = re.match(r'Docent:\s*(.+?)\s*·', t)
        if m: modules[cur_mod]['docent'] = m.group(1).strip()
        continue
    if style == 'Heading 3' and cur_mod:
        if cur: blocks.append(cur)
        m = re.match(r'(\d+)\.(\d+)\s+(.+)', t)
        cur = {'module': cur_mod, 'nr': int(m.group(2)) if m else None,
               'naam': m.group(3).strip() if m else t, 'lines': []}
        continue
    if style == 'Heading 2' and cur_mod:
        # thematisch tussenkopje binnen module
        if cur: blocks.append(cur); cur = None
        continue
    if cur is not None and t:
        cur['lines'].append(t)
if cur: blocks.append(cur)

print(f'Blokken (uitspraken): {len(blocks)}')

WET_END = re.compile(r'(geldend per|geldend vanaf|Wetboek|Verordening|Verdrag|Richtlijn).*\d{2}-\d{2}-\d{4}', re.I)

for b in blocks:
    c = {
        'id': f"{b['module']}.{b['nr']:02d}" if b['nr'] else b['module'],
        'module': b['module'],
        'nr': b['nr'],
        'naam': b['naam'],
        'verwijzing': '', 'ecli': '', 'bron_syllabus': '', 'pdf_pagina': None,
        'ook_onder': '', 'kern': '', 'feiten': '', 'leerstuk': '',
        'artikel': '', 'wettekst': [], 'rechtsregel': '', 'verband': '',
        'citaat': '', 'bron_citaat': '',
    }
    lines = b['lines']
    state = None
    for k, t in enumerate(lines):
        if k == 0 and not c['verwijzing']:
            c['verwijzing'] = t
            m = re.search(r'(ECLI:[A-Z]{2}:[A-Z0-9]+:\d{4}:[A-Z0-9.]+)', t)
            if m: c['ecli'] = m.group(1)
            continue
        if t.startswith('Bron: Syllabus') or t.startswith('Bron: syllabus module'):
            c['bron_syllabus'] = t.replace('Bron:', '').strip()
            m = re.search(r'pdf-pagina\s*(\d+)', t)
            if m: c['pdf_pagina'] = int(m.group(1))
            state = None; continue
        if t.startswith('Deze uitspraak staat ook onder'):
            c['ook_onder'] = t; state = None; continue
        if t.startswith('Kern:'):
            c['kern'] = t[5:].strip(); state = None; continue
        if t.startswith('Feiten:'):
            c['feiten'] = t[7:].strip(); state = 'feiten'; continue
        if t.startswith('Leerstuk:'):
            c['leerstuk'] = t[9:].strip(); state = 'leerstuk'; continue
        if t.startswith('Bepalend artikel:'):
            c['artikel'] = t[len('Bepalend artikel:'):].strip(); state = 'wet'; continue
        if t.startswith('Rechtsregel:'):
            c['rechtsregel'] = t[len('Rechtsregel:'):].strip(); state = 'rechtsregel'; continue
        if t.startswith('Verband:'):
            c['verband'] = t[8:].strip(); state = 'verband'; continue
        if t.startswith('Bron:'):
            c['bron_citaat'] = t[5:].strip(); state = None; continue
        if t[0] in '“"\'‘' and state in ('rechtsregel', 'verband', 'citaat', None):
            c['citaat'] = (c['citaat'] + ' ' + t).strip(); state = 'citaat'; continue
        # vervolgregels
        if state == 'wet':
            c['wettekst'].append(t)
        elif state == 'feiten':
            c['feiten'] += ' ' + t
        elif state == 'leerstuk':
            c['leerstuk'] += ' ' + t
        elif state == 'rechtsregel':
            c['rechtsregel'] += ' ' + t
        elif state == 'verband':
            c['verband'] += ' ' + t
        elif state == 'citaat':
            c['citaat'] += ' ' + t
    # wettekst: laatste regel is meestal de bronvermelding ("Burgerlijk Wetboek Boek 6, geldend per ...")
    if c['wettekst'] and WET_END.search(c['wettekst'][-1]):
        c['wettekst_bron'] = c['wettekst'].pop()
    else:
        c['wettekst_bron'] = ''
    c['wettekst'] = '\n'.join(c['wettekst'])
    # Kort artikel (eerste "art. X:Y BW")
    m = re.match(r'(art\.\s*[^·]+?)(\s*·|\s*$)', c['artikel'])
    c['artikel_kort'] = m.group(1).strip() if m else c['artikel'].split('·')[0].strip()
    # Leerstuk kort (voor het streepje)
    c['leerstuk_kort'] = c['leerstuk'].split(' — ')[0].strip() if c['leerstuk'] else ''
    cases.append(c)

# Dubbelen: "Deze uitspraak staat ook onder 16.2 Soldeermachine." → zelfde_als = ['16.02']
for c in cases:
    c['zelfde_als'] = [f"{m}.{int(n):02d}" for m, n in re.findall(r'(\d{2})\.(\d{1,2})', c['ook_onder'])]
# Korte verwijzing voor op de kaart: instantie + datum ("HR 19 juli 2019")
for c in cases:
    m = re.match(r'^(.*?\d{4})', c['verwijzing'])
    c['verwijzing_kort'] = m.group(1) if m else c['verwijzing'][:40]

# Verband-links: zoek namen van andere uitspraken in de verband-tekst.
# Match op de volledige naam én op de naam zonder toevoeging tussen haken ("SnowWorld/ABN AMRO (liquiditeitspremie)" → "SnowWorld/ABN AMRO").
# Per link wordt de gematchte tekst bewaard (verband_links) zodat de app precies die tekst klikbaar maakt; langste match wint bij overlap.
def naamsleutel(n):
    return re.split(r'\s[\(\[]', n)[0].strip()
kandidaten = []  # (tekst, id)
for x in cases:
    for t in {x['naam'], naamsleutel(x['naam'])}:
        if len(t) >= 4:
            kandidaten.append((t, x['id']))
kandidaten.sort(key=lambda k: -len(k[0]))
for c in cases:
    c['verband_ids'] = []
    c['verband_links'] = []
    if not c['verband']:
        continue
    bezet = []  # (start, eind) van al gematchte stukken tekst
    for tekst, cid in kandidaten:
        if cid == c['id']:
            continue
        # woordgrenzen: "TMF" mag niet matchen binnen "De Boer/TMF Financial Services" (die langere naam is al eerder gematcht)
        patroon = r'(?<![\w/])' + re.escape(tekst) + r'(?![\w/])'
        for m in re.finditer(patroon, c['verband']):
            s, e = m.span()
            if any(not (e <= bs or s >= be) for bs, be in bezet):
                continue  # overlapt met een langere match
            bezet.append((s, e))
            if cid not in c['verband_ids']:
                c['verband_ids'].append(cid)
            if not any(l['id'] == cid and l['tekst'] == tekst for l in c['verband_links']):
                c['verband_links'].append({'id': cid, 'tekst': tekst})
            break

data = {
    'bron': SRC.name,
    'versie': '19 augustus 2026 (verbanden 16 sept, modules 10/20/22 9 okt 2026)',
    'modules': modules,
    'totaal': len(cases),
    'cases': cases,
}
OUT.write_text(json.dumps(data, ensure_ascii=False, separators=(',', ':')), encoding='utf-8')
print(f'Geschreven: {OUT} ({OUT.stat().st_size} bytes)')

# cases.js: zelfde data als JS-variabele (voor file:// en als offline-fallback) + mapnamen van de syllabi
# zodat de knop "Open syllabus" op de pc het juiste pdf-bestand opent.
dirs, files = {}, {}
for d_ in sorted(GROTIUS.glob('[0-9][0-9] *')):
    mod = d_.name[:2]
    for pdf in d_.glob('*.pdf'):
        if 'syllabus' in pdf.name.lower() or re.match(r'^\d+\.\s', pdf.name):
            dirs[mod] = d_.name; files[mod] = pdf.name
js = ('/* Grotius O&A · Rechtspraak — data als JS-fallback voor file:// gebruik. Gegenereerd door generator/parse_rechtspraak.py */\n'
      'window.CASES_DATA = ' + json.dumps(data, ensure_ascii=False, separators=(',', ':')) + ';\n'
      'window.MODULE_DIRS = ' + json.dumps(dirs, ensure_ascii=False) + ';\n'
      'window.MODULE_FILES = ' + json.dumps(files, ensure_ascii=False) + ';\n')
OUT_JS.write_text(js, encoding='utf-8')
print(f'Geschreven: {OUT_JS} ({OUT_JS.stat().st_size} bytes)')

# Kwaliteitsrapport
from collections import Counter
per_mod = Counter(c['module'] for c in cases)
print('\nPer module:', dict(sorted(per_mod.items())))
leeg = {k: sum(1 for c in cases if not c[k]) for k in ['verwijzing','ecli','kern','feiten','leerstuk','artikel','rechtsregel','citaat']}
print('Lege velden:', leeg)
print('Met verband:', sum(1 for c in cases if c['verband']), '| verband-links:', sum(len(c['verband_ids']) for c in cases))
print('\nVoorbeeld:')
ex = cases[0]
for k in ['id','naam','verwijzing','ecli','kern','artikel_kort','leerstuk_kort','pdf_pagina']:
    print(f'  {k}: {ex[k]}')
print(f"  rechtsregel: {ex['rechtsregel'][:200]}")
print(f"  citaat: {ex['citaat'][:150]}")
