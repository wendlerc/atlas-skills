from pathlib import Path
import cv2,numpy as np,subprocess
p=Path(__file__).resolve().parents[1]
out=p/'the-crumb-run.mp4'
cmd=['ffmpeg','-loglevel','error','-y','-f','rawvideo','-pix_fmt','bgr24','-s','720x1280','-r','24','-i','-','-i',str(Path(__file__).resolve().parent / 'crumb-sound.wav'),'-vf','scale=in_range=full:out_range=tv:out_color_matrix=bt709,format=yuv420p','-c:v','libx264','-crf','16','-preset','fast','-colorspace','bt709','-color_primaries','bt709','-color_trc','bt709','-c:a','aac','-b:a','224k','-movflags','+faststart',str(out)]
def feelers(im,t):
 # Short close-focus silhouettes move independently as the worker probes its path.
 overlay=im[1010:].copy()
 for side in [-1,1]:
  phase=t*3.8+side*.9
  tip=np.array([360+side*(202+24*np.sin(phase)),146+25*np.sin(phase*.72+side)])
  elbow=np.array([360+side*(132+13*np.sin(phase-.7)),187+10*np.cos(phase)])
  root=np.array([360+side*92,290])
  half=elbow*.6+tip*.4+[0,-6]
  for a,b,r in [(root,elbow,5),(elbow,half,3),(half,tip,2)]:
   cv2.line(overlay,tuple(a.astype(int)),tuple(b.astype(int)),(29,33,39),r,cv2.LINE_AA)
 detail=cv2.GaussianBlur(overlay,(0,0),1.4)
 im[1010:]=cv2.addWeighted(im[1010:],.38,detail,.62,0)
 return im
with subprocess.Popen(cmd,stdin=subprocess.PIPE) as ff:
 for s in ['dawn','noon','dusk']:
  frames=sorted((p/(s+'-flight')).glob('frames_*_image.jpg'));assert len(frames)==120
  for i,f in enumerate(frames):
   im=feelers(cv2.imread(str(f)),i/24+5*["dawn","noon","dusk"].index(s))
   if s=='dusk' and i>=111:im=np.uint8(im*np.cos((i-110)/9*np.pi/2)**1.2)
   ff.stdin.write(im.tobytes())
 ff.stdin.close();assert ff.wait()==0
