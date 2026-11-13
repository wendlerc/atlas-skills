import numpy as np,wave
from pathlib import Path
sr=48000;D=15;n=D*sr;m=np.zeros((n,2));rng=np.random.default_rng(95)
def add(at,s,pan=0):
 i=round(at*sr);l=min(len(s),n-i)
 if l>0:m[i:i+l]+=s[:l,None]*np.sqrt([.5-.45*pan,.5+.45*pan])
def tone(at,f,d,a,dec,pan=0):
 t=np.arange(int(d*sr))/sr;add(at,a*(1-np.exp(-t/.008))*np.exp(-t/dec)*(np.sin(2*np.pi*f*t)+.15*np.sin(2*np.pi*2*f*t)),pan)
def noise(d,hz):
 a=rng.normal(0,1,int(d*sr));f=np.fft.rfftfreq(len(a),1/sr);a=np.fft.irfft(np.fft.rfft(a)*np.exp(-f/hz),n=len(a));return a/a.std()
for p in [-.7,.7]:
 t=np.arange(n)/sr;add(0,.013*noise(D,650)*(1+.18*np.sin(t*1.3)),p)
for beat in np.arange(.17,D,.105):
 if 6.9<beat<7.28 or 13.8<beat:continue
 t=np.arange(1700)/sr;add(beat,.021*noise(len(t)/sr,3800)*np.exp(-t/.006),rng.uniform(-.55,.55))
for at in [1.3,2.5,5.4,7.10,9.2]:
 t=np.arange(sr//2)/sr;add(at,.18*np.sin(2*np.pi*(42*t+1.75*(1-np.exp(-t*11))))*np.exp(-t*12)*(1-np.exp(-t*65)),-.4)
for at,f in [(1.8,1310),(1.825,2030),(4.05,1280),(8.94,950)]:
 tone(at,f,.4,.042,.11,.45)
for at,key in [(0.22,55),(1.02,62),(2.2,67),(3.42,69),(4.47,62),(5.1,57),(5.9,64),(6.7,67),(7.72,71),(8.15,67),(9.42,64),(10.2,60),(11.2,67),(12.1,69),(13.2,64),(14,60)]:
 tone(at,440*2**((key-69)/12),1,.095,.31,np.sin(at)*.45)
m*=np.minimum(1,np.arange(n)/sr/.05)[:,None]*np.minimum(1,(n-np.arange(n))/sr/.5)[:,None];m*=.79/np.max(abs(m))
with wave.open(str(Path(__file__).resolve().parent / 'crumb-sound.wav'),'wb') as w:w.setnchannels(2);w.setsampwidth(2);w.setframerate(sr);w.writeframes((m*32767).astype('<i2').tobytes())
