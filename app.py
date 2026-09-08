from pathlib import Path
import zipfile, shutil, re

bad = Path("/mnt/data/kart_highway_3d_mobile.zip")
extract = Path("/mnt/data/fix_kart")
if extract.exists():
    shutil.rmtree(extract)
extract.mkdir()

with zipfile.ZipFile(bad) as z:
    z.extractall(extract)

app = extract / "app.py"
s = app.read_text(encoding="utf-8")

# The previous packaging accidentally included the file-generation script in app.py.
# Recover the actual Streamlit source by locating the embedded source assignment if present.
if "work = Path(" in s and "zipfile.ZipFile" in s and "components.html" not in s:
    # The actual app source was constructed in the previous tool state; recreate a clean,
    # self-contained Streamlit app from scratch.
    app_source = r'''import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="3D Highway Kart", page_icon="🏎️", layout="wide")

html = r"""
<!doctype html>
<html>
<head>
<meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1, user-scalable=no">
<style>
html,body{margin:0;width:100%;height:100%;overflow:hidden;background:#111;touch-action:none}
canvas{display:block;width:100%;height:100%;touch-action:none}
#ui{position:fixed;top:10px;left:10px;z-index:5;color:#fff;font:700 18px Arial;text-shadow:0 2px 4px #000}
#mobile{position:fixed;left:0;right:0;bottom:max(10px,env(safe-area-inset-bottom));display:flex;justify-content:space-between;padding:0 12px;z-index:10;pointer-events:none}
.cluster{display:flex;gap:8px;pointer-events:auto}
.btn{width:62px;height:62px;border:2px solid #fff8;border-radius:18px;background:#1119;color:white;display:flex;align-items:center;justify-content:center;font:bold 18px Arial;user-select:none;touch-action:none;-webkit-tap-highlight-color:transparent}
.btn:active,.btn.active{background:#fff5;transform:scale(.94)}
@media(min-width:701px){#mobile{display:none}}
</style>
</head>
<body>
<div id="ui">🏎️ 3D HIGHWAY<br><span id="info">READY</span></div>
<div id="mobile">
 <div class="cluster"><div class="btn" id="left">◀</div><div class="btn" id="right">▶</div></div>
 <div class="cluster"><div class="btn" id="drift">DRIFT</div><div class="btn" id="boost">BOOST</div><div class="btn" id="gas">▲</div></div>
</div>
<script src="https://cdn.jsdelivr.net/npm/three@0.160.0/build/three.min.js"></script>
<script>
const scene=new THREE.Scene();
scene.background=new THREE.Color(0x9ed8ff);
scene.fog=new THREE.Fog(0x9ed8ff,180,700);
const camera=new THREE.PerspectiveCamera(65,innerWidth/innerHeight,.1,1200);
const renderer=new THREE.WebGLRenderer({antialias:true});
renderer.setPixelRatio(Math.min(devicePixelRatio,2)); renderer.setSize(innerWidth,innerHeight);
document.body.appendChild(renderer.domElement);

scene.add(new THREE.HemisphereLight(0xffffff,0x557755,2));
const sun=new THREE.DirectionalLight(0xffffff,2.2); sun.position.set(100,180,80); scene.add(sun);

const ground=new THREE.Mesh(new THREE.PlaneGeometry(1600,1600),new THREE.MeshLambertMaterial({color:0x6b9b5b}));
ground.rotation.x=-Math.PI/2; scene.add(ground);

const pts=[
 new THREE.Vector3(0,0,0),new THREE.Vector3(0,0,-110),new THREE.Vector3(70,0,-180),
 new THREE.Vector3(170,0,-180),new THREE.Vector3(250,0,-110),new THREE.Vector3(250,0,20),
 new THREE.Vector3(180,0,100),new THREE.Vector3(40,0,120),new THREE.Vector3(-80,0,80),
 new THREE.Vector3(-150,0,10),new THREE.Vector3(-145,0,-80),new THREE.Vector3(-80,0,-145)
];
const curve=new THREE.CatmullRomCurve3(pts,true,'catmullrom',.35);

function roadMesh(){
 const geo=new THREE.BufferGeometry(), pos=[], idx=[];
 const n=360,w=13;
 for(let i=0;i<n;i++){
   const t=i/n, p=curve.getPointAt(t), tan=curve.getTangentAt(t).normalize();
   const side=new THREE.Vector3(-tan.z,0,tan.x).normalize();
   const a=p.clone().addScaledVector(side,w), b=p.clone().addScaledVector(side,-w);
   pos.push(a.x,.05,a.z,b.x,.05,b.z);
   if(i<n-1){let j=i*2;idx.push(j,j+1,j+2,j+1,j+3,j+2)}
 }
 geo.setAttribute('position',new THREE.Float32BufferAttribute(pos,3));geo.setIndex(idx);geo.computeVertexNormals();
 const m=new THREE.MeshLambertMaterial({color:0x34363a,side:THREE.DoubleSide});
 scene.add(new THREE.Mesh(geo,m));
}
roadMesh();

for(let i=0;i<72;i++){
 const t=i/72,p=curve.getPointAt(t),tan=curve.getTangentAt(t).normalize(),side=new THREE.Vector3(-tan.z,0,tan.x).normalize();
 const s=(i%2?1:-1)*15;
 const pole=new THREE.Mesh(new THREE.CylinderGeometry(.16,.2,6,8),new THREE.MeshLambertMaterial({color:0x777777}));
 pole.position.copy(p).addScaledVector(side,s);pole.position.y=3;scene.add(pole);
 const lamp=new THREE.Mesh(new THREE.BoxGeometry(.8,.25,.8),new THREE.MeshBasicMaterial({color:0xffffcc}));
 lamp.position.copy(pole.position);lamp.position.y=6;scene.add(lamp);
}

function kart(color){
 const g=new THREE.Group();
 const body=new THREE.Mesh(new THREE.BoxGeometry(2.2,.65,3.5),new THREE.MeshLambertMaterial({color}));
 body.position.y=.65;g.add(body);
 const seat=new THREE.Mesh(new THREE.BoxGeometry(1.25,.65,1.1),new THREE.MeshLambertMaterial({color:0x202020}));
 seat.position.set(0,1.05,.35);g.add(seat);
 const nose=new THREE.Mesh(new THREE.BoxGeometry(1.5,.45,1.2),new THREE.MeshLambertMaterial({color:0xdddddd}));
 nose.position.set(0,.72,-1.25);g.add(nose);
 for(const x of [-1,1])for(const z of [-1.15,1.15]){
   const wheel=new THREE.Mesh(new THREE.CylinderGeometry(.38,.38,.3,12),new THREE.MeshLambertMaterial({color:0x151515}));
   wheel.rotation.z=Math.PI/2;wheel.position.set(x*1.15,.42,z);g.add(wheel);
 }
 return g;
}
const player=kart(0x2d7cff);scene.add(player);
const cpu=[];
[0xff4545,0xffc400,0x55dd66,0xaa66ff,0xff7a22].forEach((c,i)=>{
 const k=kart(c);scene.add(k);cpu.push({mesh:k,t:(i+1)*.015,speed:.000105+i*.000004});
});

let t=0,speed=0,drifting=false,driftCharge=0,boost=0,lap=1,started=false,finished=false;
const keys={up:false,down:false,left:false,right:false,drift:false,boost:false};
addEventListener('keydown',e=>{
 if(e.code==='ArrowUp')keys.up=true;if(e.code==='ArrowDown')keys.down=true;
 if(e.code==='ArrowLeft')keys.left=true;if(e.code==='ArrowRight')keys.right=true;
 if(e.code==='ShiftLeft'||e.code==='ShiftRight')keys.drift=true;if(e.code==='Space')keys.boost=true;
});
addEventListener('keyup',e=>{
 if(e.code==='ArrowUp')keys.up=false;if(e.code==='ArrowDown')keys.down=false;
 if(e.code==='ArrowLeft')keys.left=false;if(e.code==='ArrowRight')keys.right=false;
 if(e.code==='ShiftLeft'||e.code==='ShiftRight')keys.drift=false;if(e.code==='Space')keys.boost=false;
});

const bind=(id,key)=>{
 const el=document.getElementById(id);
 const on=(e)=>{e.preventDefault();keys[key]=true;el.classList.add('active')};
 const off=(e)=>{e.preventDefault();keys[key]=false;el.classList.remove('active')};
 el.addEventListener('pointerdown',on,{passive:false});el.addEventListener('pointerup',off,{passive:false});
 el.addEventListener('pointercancel',off,{passive:false});el.addEventListener('pointerleave',e=>{if(e.buttons===0)off(e)},{passive:false});
};
bind('left','left');bind('right','right');bind('gas','up');bind('drift','drift');bind('boost','boost');
document.addEventListener('touchmove',e=>e.preventDefault(),{passive:false});

let last=performance.now(),total=0;
function loop(now){
 const dt=Math.min((now-last)/1000,.04);last=now;total+=dt;
 if(!finished){
   const accel=keys.up?.85:-.35;
   speed+=accel*dt;
   if(keys.down)speed-=1.3*dt;
   speed=Math.max(0,Math.min(keys.boost&&boost>0?48:34,speed));
   if(keys.drift&&(keys.left||keys.right)&&speed>7){drifting=true;driftCharge+=dt*18;}
   else {if(drifting&&driftCharge>1.2)boost=Math.min(100,boost+driftCharge*2.2);drifting=false;driftCharge=0;}
   if(keys.boost&&boost>0){speed=Math.min(48,speed+12*dt);boost-=22*dt;}
   const steer=(keys.left?-1:0)+(keys.right?1:0);
   t=(t+speed*dt/curve.getLength())%1;
   const p=curve.getPointAt(t),tan=curve.getTangentAt(t).normalize();
   const side=new THREE.Vector3(-tan.z,0,tan.x);
   p.addScaledVector(side,steer*(drifting?4.5:2.2)*dt*speed/15);
   player.position.copy(p);player.position.y=.05;
   player.rotation.y=Math.atan2(tan.x,tan.z)+(drifting?steer*.18:0);
   const lapNow=Math.floor((t*2))+1;
   if(lapNow>lap)lap=lapNow;
   if(total>2&&t<.02&&lap>=2)finished=true;
   cpu.forEach(o=>{
     o.t=(o.t+o.speed*dt*speed/15)%1;
     const q=curve.getPointAt(o.t),qt=curve.getTangentAt(o.t);
     o.mesh.position.copy(q);o.mesh.position.y=.05;o.mesh.rotation.y=Math.atan2(qt.x,qt.z);
   });
   const camPos=player.position.clone().addScaledVector(tan,-11);camPos.y+=5.5;
   camera.position.lerp(camPos,.12);camera.lookAt(player.position.clone().add(new THREE.Vector3(0,1,2)));
 }
 document.getElementById('info').textContent=finished?'FINISH!':`LAP ${Math.min(lap,2)}/2  |  SPEED ${Math.round(speed)}  |  BOOST ${Math.round(boost)}`;
 renderer.render(scene,camera);requestAnimationFrame(loop);
}
camera.position.set(0,8,15);requestAnimationFrame(loop);
addEventListener('resize',()=>{camera.aspect=innerWidth/innerHeight;camera.updateProjectionMatrix();renderer.setSize(innerWidth,innerHeight)});
</script>
</body>
</html>
"""
    app_source = 'import streamlit as st\nimport streamlit.components.v1 as components\n\nst.set_page_config(page_title="3D Highway Kart", page_icon="🏎️", layout="wide")\n\nhtml = ' + repr(html) + '\n\ncomponents.html(html, height=760, scrolling=False)\n'
    app.write_text(app_source, encoding="utf-8")

out=Path("/mnt/data/kart_highway_3d_mobile_fixed.zip")
if out.exists(): out.unlink()
with zipfile.ZipFile(out,"w",zipfile.ZIP_DEFLATED) as z:
    for p in extract.rglob("*"):
        if p.is_file(): z.write(p,p.relative_to(extract))
print(out)
