import re,sys
# Turn YouTube auto-sub VTT (rolling captions) into clean timed lines
lines=open(sys.argv[1],encoding='utf-8').read().split('\n')
out=[];t=None;seen=set()
for l in lines:
    m=re.match(r'(\d+:\d+:\d+)\.\d+ -->',l)
    if m: t=m.group(1);continue
    if not l.strip() or l.startswith(('WEBVTT','Kind:','Language:')) or '-->' in l: continue
    txt=re.sub(r'<[^>]+>','',l).strip()
    if txt and txt not in seen:
        seen.add(txt);out.append((t,txt))
for t,x in out: print(t,x)
