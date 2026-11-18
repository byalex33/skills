import sys,re
# beats.py cuts.txt transcript.vtt START END -> each visual change with the words spoken during it (word-level timing from VTT <c> tags)
cuts=[float(x) for x in open(sys.argv[1])]; vtt=open(sys.argv[2],encoding='utf-8').read(); a,b=float(sys.argv[3]),float(sys.argv[4])
def ts(s): h,m,x=s.split(':');return int(h)*3600+int(m)*60+float(x)
words=[]
for blk in vtt.split('\n\n'):
    m=re.search(r'(\d+:\d+:\d+\.\d+) -->',blk)
    if not m or '<c>' not in blk: continue
    line=[l for l in blk.split('\n') if '<c>' in l or re.search(r'<\d',l)]
    if not line: continue
    l=line[-1]; t0=ts(m.group(1))
    first=re.match(r'([^<]+)',l); 
    if first and first.group(1).strip(): words.append((t0,first.group(1).strip()))
    for t,w in re.findall(r'<(\d+:\d+:\d+\.\d+)><c>([^<]*)</c>',l): words.append((ts(t),w.strip()))
words.sort()
edges=[a]+[c for c in cuts if a<c<b]+[b]
for s,e in zip(edges,edges[1:]):
    txt=' '.join(w for t,w in words if s<=t<e)
    print(f"{s:6.2f} {e-s:4.1f}s | {txt}")
