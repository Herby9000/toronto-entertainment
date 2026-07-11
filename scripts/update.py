#!/usr/bin/env python3
"""Build a validated six-month listing. Network/source failure never overwrites good data."""
import json,re,sys,urllib.request
from datetime import datetime,date,timedelta,timezone
from html import unescape
from pathlib import Path
ROOT=Path(__file__).parents[1]; OUT=ROOT/'data/events.json'; UA={'User-Agent':'TorontoEntertainment/1.0 (+https://github.com/Herby9000/toronto-entertainment)'}
def get(url): return urllib.request.urlopen(urllib.request.Request(url,headers=UA),timeout=30).read().decode('utf8','ignore')
def songkick():
 s=get('https://www.songkick.com/metro-areas/27396-canada-toronto'); out=[]
 for raw in re.findall(r'<script[^>]*application/ld\+json[^>]*>(.*?)</script>',s,re.S|re.I):
  try: docs=json.loads(raw); docs=docs if isinstance(docs,list) else [docs]
  except Exception: continue
  for x in docs:
   if not isinstance(x,dict) or not x.get('startDate') or not x.get('location'): continue
   title=re.sub(r'\s+@.*$','',x.get('name','')).strip(); venue=x.get('location',{}).get('name','Toronto')
   out.append({'title':title,'date':x['startDate'][:10],'venue':venue,'description':f'{title} live in Toronto. Follow the source for times, age restrictions and tickets.','url':x.get('url'),'category':'Music','audience':'all'})
 return out
def rom():
 s=get('https://www.rom.on.ca/whats-on'); out=[]
 # Official exhibition cards expose title, link and an Until date.
 for m in re.finditer(r'<a href="([^"]+)"[^>]*>[\s\S]{0,4000}?field--label-hidden">([^<]+)</span>[\s\S]{0,800}?Until <time datetime="(\d{4}-\d\d-\d\d)',s):
  out.append({'title':unescape(m.group(2).strip()),'date':date.today().isoformat(),'venue':'Royal Ontario Museum','description':f'On view through {m.group(3)}. An easy museum outing for curious adults and kids.','url':'https://www.rom.on.ca'+m.group(1),'category':'Live Events','audience':'family'})
 return out
def valid(events):
 lo=date.today(); hi=lo+timedelta(days=183); req={'title','date','venue','description','url','category','audience'}; seen=set(); good=[]
 for e in events:
  try:d=date.fromisoformat(e['date'])
  except Exception:continue
  key=(e.get('title','').lower(),e.get('date'),e.get('venue','').lower())
  if req<=e.keys() and lo<=d<=hi and e['category'] in {'Music','Comedy','Live Events'} and str(e['url']).startswith('http') and key not in seen:seen.add(key);good.append(e)
 return sorted(good,key=lambda x:(x['date'],x['title']))
def main():
 old=json.loads(OUT.read_text()) if OUT.exists() else {'events':[]}; fresh=[]; errors=[]
 for name,fn in [('Songkick',songkick),('ROM',rom)]:
  try:
   got=fn(); fresh+=got
   if not got: errors.append(name+': no parseable events')
  except Exception as e: errors.append(name+': '+str(e))
 merged=valid(fresh+old.get('events',[]))
 if not merged: print('Refusing to replace data with an empty listing',file=sys.stderr); return 1
 payload={'updated':datetime.now(timezone.utc).isoformat(),'events':merged,'source_status':errors or ['All sources responded']}; tmp=OUT.with_suffix('.tmp');tmp.write_text(json.dumps(payload,indent=2)+'\n');json.loads(tmp.read_text());tmp.replace(OUT)
 print(f'Wrote {len(merged)} verified events; '+('; '.join(errors) if errors else 'all sources healthy'))
if __name__=='__main__':raise SystemExit(main())
