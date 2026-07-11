#!/usr/bin/env python3
import json,re,sys
from datetime import date,timedelta
from pathlib import Path
r=Path(__file__).parents[1]; errors=[]
for f in ['index.html','style.css','app.js','data/events.json','LICENSE','README.md']:
 if not (r/f).exists():errors.append('missing '+f)
try:
 d=json.loads((r/'data/events.json').read_text()); ev=d['events']; keys={'title','date','venue','description','url','category','audience'};seen=set(); hi=date.today()+timedelta(days=183)
 for i,e in enumerate(ev):
  if not keys<=e.keys():errors.append(f'event {i} missing fields');continue
  day=date.fromisoformat(e['date']); key=(e['title'].lower(),e['date'],e['venue'].lower())
  if not date.today()<=day<=hi:errors.append(f'event {i} out of range')
  if key in seen:errors.append(f'event {i} duplicate')
  seen.add(key)
  if not re.match(r'https://',e['url']):errors.append(f'event {i} insecure source')
except Exception as e:errors.append(str(e))
if errors: print('\n'.join('FAIL '+x for x in errors));sys.exit(1)
from collections import Counter
print(f'PASS: {len(ev)} valid unique events in six-month horizon');print('Counts:',dict(Counter(x['category'] for x in ev)))
