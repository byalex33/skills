import sys,array,math,random
# Compare high-frequency energy (whoosh/pop proxy) in the 150ms after each visual change vs random times
cuts=[float(x) for x in open(sys.argv[1])]; a=array.array('h',open(sys.argv[2],'rb').read()); sr=16000
def hf(t):
    i=int(t*sr);seg=a[i:i+int(.15*sr)]
    if len(seg)<10:return None
    d=[seg[k]-seg[k-1] for k in range(1,len(seg))]  # first difference ~ high-pass
    return 20*math.log10(math.sqrt(sum(x*x for x in d)/len(d))/32768+1e-9)
dur=len(a)/sr; random.seed(1)
c=[v for v in map(hf,cuts) if v is not None]; r=[v for v in (hf(random.uniform(0,dur-1)) for _ in range(400)) if v is not None]
c.sort();r.sort()
print(sys.argv[1],'HF median at cuts',round(c[len(c)//2],1),'random',round(r[len(r)//2],1),'| p90 cuts',round(c[int(len(c)*.9)],1),'random',round(r[int(len(r)*.9)],1))
