"""Rebuild the singer guide files using NumPy and OpenCV with EXR support."""
from pathlib import Path
import os
os.environ['OPENCV_IO_ENABLE_OPENEXR'] = '1'
import json
import cv2
import numpy as np

p = Path(__file__).resolve().parent
def quat(mat):
    k=np.empty((4,4)); k[:3,:3]=mat+mat.T-np.eye(3)*np.trace(mat)
    k[:3,3]=k[3,:3]=[mat[2,1]-mat[1,2],mat[0,2]-mat[2,0],mat[1,0]-mat[0,1]]
    k[3,3]=np.trace(mat); _,vs=np.linalg.eigh(k);q=vs[:,-1];return q if q[3]>=0 else -q
def unit(x):return x/np.linalg.norm(x)
def interp(knots,ts):
    knots=np.array(knots);x=knots[:,0];y=knots[:,1:];s=np.zeros_like(y)
    for i in range(1,len(x)-1):
        a=(y[i]-y[i-1])/(x[i]-x[i-1]);b=(y[i+1]-y[i])/(x[i+1]-x[i]);m=a*b>0;s[i,m]=2/(1/a[m]+1/b[m])
    for t in ts:
        i=min(len(x)-2,np.searchsorted(x[1:],t));h=x[i+1]-x[i];f=(t-x[i])/h
        yield (1-3*f*f+2*f**3)*y[i]+h*f*(1-f)**2*s[i]+(3*f*f-2*f**3)*y[i+1]+h*f*f*(f-1)*s[i+1]
# Camera position and heading in metres, with the railway running towards -Z.
keys=[[0,.63,1.14,2.05,-13,-9,0],[.19,-.22,.91,2.13,6,-7,4],[.40,-1.27,.79,1.62,43,-1,9],[.60,-1.74,.99,.62,72,-3,5],[.80,-1.47,1.21,-.30,109,-6,-2],[1,-.58,1.28,-.91,137,-7,-3]]
def camera(t,portrait):
 x,y,z,az,el,bank=next(interp(keys,[t]));a,b,c=np.radians([az,el,bank])
 fw=np.array([np.sin(a)*np.cos(b),np.sin(b),-np.cos(a)*np.cos(b)]);ri=unit(np.cross(fw,[0,1,0]));up=np.cross(ri,fw)
 rot=np.column_stack([ri*np.cos(c)+up*np.sin(c),up*np.cos(c)-ri*np.sin(c),-fw])
 w,h=(720,1280) if portrait else (1280,720);f=700 if portrait else 520
 return dict(extrinsics=dict(position=[x,y,z],quaternion=quat(rot).tolist(),coordinateSystem='rub'),intrinsics=dict(width=w,height=h,fx=f,fy=f,cx=w/2,cy=h/2)),rot
shapes=[]
def box(c,r):shapes.append(('box',np.array(c),np.array(r)))
def rock(c,r):shapes.append(('rock',np.array(c),np.array(r)))
rng=np.random.default_rng(13)
# Low tea table and its rim, with a cup and saucer.
rock([.03,.42,.60],[.64,.085,.52]);box([.04,.20,.60],[.14,.22,.15])
rock([.32,.61,.62],[.12,.12,.11])
# Seated mother, bent legs and arms, next to an upright piano.
rock([0,.65,-.62],[.31,.41,.21]);rock([0,1.15,-.65],[.21,.25,.19])
for x in [-.18,.18]:
 rock([x,.30,-.33],[.18,.31,.24]);rock([x,.79,-.40],[.09,.23,.09])
box([2.05,.78,-1.72],[.89,.79,.35]);box([2.05,.84,-1.23],[.91,.08,.22])
box([1.95,.44,-.81],[.52,.08,.24])
for x in [1.55,2.34]:box([x,.22,-.81],[.06,.22,.07])
for x in [-3.65,3.5]:box([x,1.7,-.5],[.1,1.72,3.85])
box([0,1.7,-3.3],[3.7,1.72,.12])
for x in [-1.55,-.08,1.35]:box([x,1.9,-3.09],[.04,.96,.04])
# Child stands beside the tea table facing Mum, with one elbow bent up to sing.
child_start=len(shapes)
paint=[]
def detail(x,y,z,rx,ry,rz,material):
 rock([.82+x,y,1.01+z],[rx,ry,rz]);paint.append(material)
hair=(32,39,53);skin=(139,179,222);knit=(65,168,224)
pants=(86,96,117);shoe=(186,203,211);wood=(55,85,132)
for side in [-1,1]:
 x=.105*side
 detail(x,.105,-.052,.083,.071,.137,shoe)
 detail(x,.263,0,.074,.157,.074,pants)
 detail(x,.468,0,.088,.154,.091,pants)
detail(0,.563,0,.183,.109,.119,pants)
detail(0,.731,0,.183,.204,.121,knit)
detail(0,.86,.012,.203,.09,.114,knit)
detail(0,.945,-.008,.068,.077,.069,skin)
detail(0,1.071,-.018,.141,.154,.123,skin)
detail(0,1.146,.011,.153,.116,.138,hair)
detail(0,1.083,.081,.148,.131,.095,hair)
for side in [-1,1]:
 detail(.129*side,1.053,.024,.041,.131,.081,hair)
 detail(.13*side,1.067,-.042,.027,.041,.022,skin)
detail(0,1.068,-.135,.031,.033,.032,skin)
detail(0,1.003,-.097,.089,.067,.059,skin)
detail(-.184,.792,-.015,.081,.102,.084,knit)
detail(-.210,.674,-.048,.064,.095,.061,knit)
detail(-.214,.563,-.065,.047,.072,.044,skin)
detail(.174,.81,-.023,.083,.094,.082,knit)
detail(.212,.749,-.076,.065,.072,.093,knit)
for t in [0,.27,.54,.81,1]:
 detail(.207-.051*t,.762+.131*t,-.095-.124*t,.052,.057,.054,knit)
detail(.153,.905,-.227,.049,.058,.046,skin)
detail(.145,.94,-.247,.023,.138,.024,wood)
for k in range(4):detail(.134,.877+k*.018,-.258,.028,.011,.019,skin)
detail(.14,.934,-.209,.024,.027,.029,skin)
detail(.141,1.094,-.247,.057,.093,.032,wood)
for row in [-.045,0,.045]:
 for col in [-.033,0,.033]:detail(.141+col,1.094+row,-.276,.011,.018,.014,hair)
detail(.143,.802,-.252,.027,.031,.015,(173,85,44))
child_end=len(shapes)

for i,t in enumerate(np.linspace(0,1,11)):
 cam,R=camera(t,False);o=np.array(cam['extrinsics']['position']);yy,xx=np.mgrid[:720,:1280].astype('float32');rays=np.stack([(xx-640)/520,(360-yy)/520,-np.ones_like(xx)],-1)@R.astype('float32').T
 col=np.zeros((*xx.shape,3),np.uint8);mask=np.zeros(xx.shape,np.uint8);dep=np.full(xx.shape,210,np.float32);dy=rays[:,:,1];sea=(0.0-o[1])/np.where(abs(dy)>.0001,dy,.0001);dep=np.where((sea>.05)&(sea<dep),sea,dep).astype('float32')
 for idx,(kind,c,r) in enumerate(shapes):
  # Bounding sphere culling saves work on objects outside the guide view.
  local=(c-o)@R;rad=np.linalg.norm(r)
  if -local[2]+rad<.1 or abs(local[0])>max(0,-local[2])*1.24+rad*2 or abs(local[1])>max(0,-local[2])*.70+rad*2:continue
  if kind=='box':
   inv=1/np.where(abs(rays)>1e-6,rays,1e-6);a=(c-r-o).astype('float32')*inv;b=(c+r-o).astype('float32')*inv;near=np.minimum(a,b).max(2);far=np.maximum(a,b).min(2);hit=(near>.04)&(far>=near)
  else:
   D=rays/r.astype('float32');O=((o-c)/r).astype('float32');aa=(D*D).sum(2);bb=D@O;disc=bb**2-aa*(O@O-1);near=(-bb-np.sqrt(np.maximum(0,disc)))/aa;hit=(disc>=0)&(near>.04)
  visible=hit&(near<dep);mask[visible]=0
  if kind=='box' and c[0]>1.4 and c[1]>.75:
   col[visible]=[60,33,26];mask[visible]=255
  if child_start<=idx<child_end:
   col[visible]=paint[idx-child_start];mask[visible]=255
  np.minimum(dep,near,out=dep,where=hit)
 prefix = p / 'guides' / f'{i:02}'
 for suffix, data in [('depth.exr', dep), ('image.png', col), ('mask.png', mask), ('depth_mask.png', np.full_like(mask,255))]:
  options = [cv2.IMWRITE_EXR_TYPE,cv2.IMWRITE_EXR_TYPE_HALF] if suffix.endswith('exr') else []
  if not cv2.imwrite(str(prefix) + '-' + suffix, data, options):
   raise RuntimeError(f'Could not write {suffix}')
 manifest = json.loads((p/'scene.json').read_text())
 manifest['guides'][i]['camera'] = cam
 manifest['reference_camera'] = camera(0,True)[0]
 (p/'scene.json').write_text(json.dumps(manifest,indent=2))
(p/'path.json').write_text(json.dumps([camera(t,True)[0] for t in np.linspace(0,1,144)],indent=2))
