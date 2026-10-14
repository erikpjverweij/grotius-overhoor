#!/usr/bin/env python3
"""Parse '2026.08.19 Grotius O&A - Rechtspraak per module.docx' naar cases.json."""
import json, re, sys
from pathlib import Path
from docx import Document

SRC = Path('/sessions/vibrant-optimistic-goldberg/mnt/Grotius/Algemeen/2026.08.19 Grotius O&A - Rechtspraak per module.docx')
OUT = Path('/sessions/vibrant-optimistic-goldberg/mnt/outputs/cases.json')

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

# Verband-links: zoek namen van andere uitspraken in verband-tekst
namen = {x['naam']: x['id'] for x in cases}
for c in cases:
    links = []
    if c['verband']:
        for nm, cid in namen.items():
            if cid != c['id'] and nm and nm in c['verband']:
                links.append(cid)
    c['verband_ids'] = links

data = {
    'bron': SRC.name,
    'versie': '19 augustus 2026 (verbanden 16 sept, modules 10/20/22 9 okt 2026)',
    'modules': modules,
    'totaal': len(cases),
    'cases': cases,
}
OUT.write_text(json.dumps(data, ensure_ascii=False, indent=1), encoding='utf-8')
print(f'Geschreven: {OUT} ({OUT.stat().st_size} bytes)')

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
