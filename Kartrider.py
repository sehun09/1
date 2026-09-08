from pathlib import Path
import zipfile

app_code = r'''import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="Kart Highway 3D", page_icon="🏎️", layout="centered")

HTML = r"""
<!doctype html>
<html lang="ko">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Kart Highway 3D</title>
<style>
html,body{margin:0;padding:0;background:#10141a;overflow:hidden;font-family:Arial,sans-serif}
#game{position:relative;width:100%;height:760px;overflow:hidden;background:#79cfff}
#game canvas{display:block;width:100%;height:100%}
#hud{position:absolute;top:14px;left:14px;right:14px;z-index:5;color:#fff;display:flex;justify-content:space-between;pointer-events:none;text-shadow:2px 2px 3px #000}
.box{background:rgba(0,0,0,.45);padding:9px 13px;border-radius:10px;margin-bottom:6px;font-weight:700}
#boostWrap{width:210px}
#boost{height:13px;background:#222;border:2px solid #fff;border-radius:10px;overflow:hidden}
#boostFill{height:100%;width:0%;background:#00eaff}
#count{position:absolute;z-index:10;inset:0;display:flex;align-items:center;justify-content:center;color:#fff;font-size:100px;font-weight:900;text-shadow:5px 5px #000;pointer-events:none}
#menu{position:absolute;z-index:20;inset:0;display:flex;flex-direction:column;align-items:center;justify-content:center;background:linear-gradient(#0005,#0009);color:#fff;text-align:center}
#menu h1{font-size:58px;margin:0 0 10px;text-shadow:5px 5px #000}
#menu button{border:0;border-radius:14px;padding:17px 50px;background:#00c853;color:#fff;font-size:24px;font-weight:800;cursor:pointer;box-shadow:0 5px #087f23}
#finish{position:absolute;z-index:15;inset:0;display:none;align-items:center;justify-content:center;text-align:center;color:#fff;font-size:52px;font-weight:900;text-shadow:4px 4px #000;background:#0004}
#touch{position:absolute;z-index:8;left:15px;right:15px;bottom:15px;display:flex;justify-content:space-between;pointer-events:none}
.grp{display:flex;gap:9px}
.touchBtn{width:62px;height:62px;border-radius:50%;border:2px solid #fff;background:#0008;color:#fff;font-size:25px;font-weight:800;pointer-events:auto;touch-action:none}
@media(max-width:600px){#game{height:650px}#menu h1{font-size:40px}#boostWrap{width:145px}.touchBtn{width:56px;height:56px}}
</style>
</head>
<body>
<div id="game">
<div id="hud">
<div><div class="box">🏁 LAP <span id="lap">1</span>/2</div><div class="box">🏆 <span id="rank">1</span>위</div></div>
<div><div class="box">⏱️ <span id="time">0.00</span></div><div class="box">💨 DRIFT BOOST</div><div class="box" id="boostWrap"><div id="boost"><div id="boostFill"></div></div></div></div>
</div>
<div id="count"></div>
<div id="finish"></div>
<div id="menu"><h1>🏎️ KART HIGHWAY 3D</h1><p>고가도로 스타일의 3D 스피드 트랙</p><p>↑ 가속　↓ 브레이크　← → 조향　SHIFT 드리프트　SPACE 부스터</p><button id="start">레이스 시작</button></div>
<div id="touch">
<div class="grp"><button class="touchBtn" id="l">◀</button><button class="touchBtn" id="r">▶</button></div>
<div class="grp"><button class="touchBtn" id="b">SHIFT</button><button class="touchBtn" id="g">▲</button><button class="touchBtn" id="bo">💨</button></div>
</div>
</div>

<script src="https://cdn.jsdelivr.net/npm/three@0.160.0/build/three.min.js"></script>
<script>
const root=document.getElementById('game');
const scene=new THREE.Scene();
scene.background=new THREE.Color(0x78cfff);
scene.fog=new THREE.Fog(0x78cfff,80,650);

const camera=new THREE.PerspectiveCamera(62,1,0.1,1200);
const renderer=new THREE.WebGLRenderer({antialias:true});
renderer.setPixelRatio(Math.min(devicePixelRatio,2));
renderer.shadowMap.enabled=true;
renderer.shadowMap.type=THREE.PCFSoftShadowMap;
root.insertBefore(renderer.domElement,root.firstChild);

function resize(){
  const w=root.clientWidth,h=root.clientHeight;
  renderer.setSize(w,h,false);
  camera.aspect=w/h; camera.updateProjectionMatrix();
}
addEventListener('resize',resize); resize();

scene.add(new THREE.HemisphereLight(0xbdefff,0x46613d,2.0));
const sun=new THREE.DirectionalLight(0xffffff,2.2);
sun.position.set(100,180,80); sun.castShadow=true; scene.add(sun);

const ground=new THREE.Mesh(
  new THREE.PlaneGeometry(2200,2200),
  new THREE.MeshStandardMaterial({color:0x4b9d43,roughness:1})
);
ground.rotation.x=-Math.PI/2; ground.position.y=-0.08; ground.receiveShadow=true; scene.add(ground);

/* ---------- Track: original highway-style layout ---------- */
const pts=[
[-170,0,170],[-70,0,190],[50,0,175],[155,0,110],
[205,3,20],[185,5,-80],[115,8,-145],[15,10,-165],
[-70,11,-145],[-135,8,-85],[-155,4,-5],[-125,0,70],
[-55,0,95],[20,0,80],[80,0,25],[55,0,-40],
[5,0,-55],[-45,0,-20],[-35,0,45],[35,0,70],
[115,0,40],[155,0,-20],[140,0,-90],[80,0,-120],
[5,0,-115],[-60,0,-75],[-95,0,-5],[-75,0,70]
].map(p=>new THREE.Vector3(p[0],p[1],p[2]));

const curve=new THREE.CatmullRomCurve3(pts,true,'catmullrom',0.5);
const N=900;
const samples=[];
for(let i=0;i<N;i++) samples.push(curve.getPointAt(i/N));

const roadWidth=18;
const roadGeo=new THREE.BufferGeometry();
const verts=[],uv=[],idx=[];
for(let i=0;i<N;i++){
  const t=i/N, p=curve.getPointAt(t), q=curve.getPointAt((i+1)/N);
  let tangent=q.clone().sub(p).normalize();
  let side=new THREE.Vector3(-tangent.z,0,tangent.x).normalize();
  verts.push(p.x-side.x*roadWidth/2,p.y,p.z-side.z*roadWidth/2);
  verts.push(p.x+side.x*roadWidth/2,p.y,p.z+side.z*roadWidth/2);
  uv.push(i/N,0,i/N,1);
}
for(let i=0;i<N;i++){
  const a=i*2,b=i*2+1,c=((i+1)%N)*2,d=((i+1)%N)*2+1;
  idx.push(a,c,b,b,c,d);
}
roadGeo.setAttribute('position',new THREE.Float32BufferAttribute(verts,3));
roadGeo.setAttribute('uv',new THREE.Float32BufferAttribute(uv,2));
roadGeo.setIndex(idx); roadGeo.computeVertexNormals();
const road=new THREE.Mesh(roadGeo,new THREE.MeshStandardMaterial({color:0x3c3f45,roughness:.9}));
road.receiveShadow=true; scene.add(road);

/* center dashed line */
for(let i=0;i<N;i+=12){
  const p=curve.getPointAt(i/N), q=curve.getPointAt((i+4)/N);
  const len=p.distanceTo(q);
  const m=new THREE.Mesh(new THREE.BoxGeometry(.35,.035,len),new THREE.MeshStandardMaterial({color:0xffffff}));
  m.position.copy(p); m.position.y+=.05;
  m.lookAt(q.x,p.y+.05,q.z); scene.add(m);
}

/* curbs and roadside lamps */
function addBox(x,y,z,sx,sy,sz,color){
  const m=new THREE.Mesh(new THREE.BoxGeometry(sx,sy,sz),new THREE.MeshStandardMaterial({color}));
  m.position.set(x,y,z); m.castShadow=true; scene.add(m); return m;
}
for(let i=0;i<N;i+=7){
  const p=curve.getPointAt(i/N),q=curve.getPointAt((i+1)/N);
  const t=q.clone().sub(p).normalize(), side=new THREE.Vector3(-t.z,0,t.x).normalize();
  const c=i%14===0?0xffffff:0xe63232;
  for(const s of [-1,1]) addBox(p.x+side.x*s*(roadWidth/2+0.7),p.y+.16,p.z+side.z*s*(roadWidth/2+0.7),1.4,.32,1.4,c);
}
for(let i=0;i<N;i+=35){
  const p=curve.getPointAt(i/N),q=curve.getPointAt((i+1)/N);
  const t=q.clone().sub(p).normalize(), side=new THREE.Vector3(-t.z,0,t.x).normalize();
  for(const s of [-1,1]){
    const x=p.x+side.x*s*15,z=p.z+side.z*s*15;
    addBox(x,4,z,.25,8,.25,0x444444);
    const lamp=addBox(x,8,z,1.2,.18,1.2,0xfff3a0);
  }
}

/* elevated bridge supports: gives the track a high-way feel */
for(let i=0;i<18;i++){
  const t=(i*0.055+0.15)%1,p=curve.getPointAt(t);
  addBox(p.x, -3, p.z, 1.2, 6, 1.2, 0x777777);
}

/* trees */
for(let i=0;i<100;i++){
  const a=Math.random()*Math.PI*2,r=90+Math.random()*180;
  const x=Math.cos(a)*r,z=Math.sin(a)*r;
  const trunk=addBox(x,2,z,1.2,4,1.2,0x70452a);
  const crown=new THREE.Mesh(new THREE.SphereGeometry(4+Math.random()*3,10,8),new THREE.MeshStandardMaterial({color:0x16752e}));
  crown.position.set(x,6,z); crown.castShadow=true; scene.add(crown);
}

/* ---------- Kart ---------- */
function makeKart(color){
  const g=new THREE.Group();
  const body=new THREE.Mesh(new THREE.BoxGeometry(2.4,.65,3.6),new THREE.MeshStandardMaterial({color,metalness:.15,roughness:.55}));
  body.position.y=.65; body.castShadow=true; g.add(body);
  const nose=new THREE.Mesh(new THREE.BoxGeometry(1.8,.35,1.2),new THREE.MeshStandardMaterial({color:0xffffff}));
  nose.position.set(0,.88,-1.15); g.add(nose);
  const seat=new THREE.Mesh(new THREE.BoxGeometry(1.25,.9,1.1),new THREE.MeshStandardMaterial({color:0x222222}));
  seat.position.set(0,1.15,.55); g.add(seat);
  const helmet=new THREE.Mesh(new THREE.SphereGeometry(.68,20,14),new THREE.MeshStandardMaterial({color:0x167cff}));
  helmet.scale.set(1,1.05,.95); helmet.position.set(0,1.85,.35); helmet.castShadow=true; g.add(helmet);
  for(const x of [-1.15,1.15]) for(const z of [-1.15,1.15]){
    const w=new THREE.Mesh(new THREE.CylinderGeometry(.45,.45,.35,16),new THREE.MeshStandardMaterial({color:0x111111}));
    w.rotation.z=Math.PI/2; w.position.set(x,.45,z); w.castShadow=true; g.add(w);
  }
  return g;
}
const playerKart=makeKart(0x087cff); scene.add(playerKart);

/* CPU */
const cpus=[];
for(let i=0;i<5;i++){
  const k=makeKart([0xff3333,0xffd000,0x9c55ff,0x00c987,0xff7b00][i]);
  scene.add(k);
  cpus.push({mesh:k,s:(i+1)*.02+0.01,progress:(i+1)*.012});
}

/* ---------- Input / physics ---------- */
const key={l:false,r:false,g:false,b:false,d:false};
addEventListener('keydown',e=>{
  if(e.key==='ArrowLeft')key.l=true;
  if(e.key==='ArrowRight')key.r=true;
  if(e.key==='ArrowUp')key.g=true;
  if(e.key==='ArrowDown')key.b=true;
  if(e.key==='Shift')key.d=true;
  if(e.code==='Space'){key.boost=true;e.preventDefault();}
});
addEventListener('keyup',e=>{
  if(e.key==='ArrowLeft')key.l=false;
  if(e.key==='ArrowRight')key.r=false;
  if(e.key==='ArrowUp')key.g=false;
  if(e.key==='ArrowDown')key.b=false;
  if(e.key==='Shift')key.d=false;
  if(e.code==='Space')key.boost=false;
});
function hold(id,k){
  const el=document.getElementById(id);
  el.addEventListener('pointerdown',e=>{e.preventDefault();key[k]=true});
  el.addEventListener('pointerup',()=>key[k]=false);
  el.addEventListener('pointercancel',()=>key[k]=false);
  el.addEventListener('pointerleave',()=>key[k]=false);
}
hold('l','l');hold('r','r');hold('g','g');hold('b','b');hold('bo','boost');hold('b','d');

let running=false, countdown=0, startTime=0, elapsed=0;
let distance=0, speed=0, lateral=0, driftCharge=0, lap=1, angle=0;
const maxSpeed=34, accel=25, brake=38;

function trackPose(u){
  u=((u%1)+1)%1;
  const p=curve.getPointAt(u), q=curve.getPointAt((u+.002)%1);
  const t=q.clone().sub(p).normalize();
  return {p,t};
}
function update(dt){
  if(!running)return;
  elapsed=(performance.now()-startTime)/1000;
  if(key.g)speed+=accel*dt; else speed-=10*dt;
  if(key.b)speed-=brake*dt;
  speed=THREE.MathUtils.clamp(speed,0,maxSpeed*(key.boost&&driftCharge>15?1.38:1));
  let steer=(key.r?1:0)-(key.l?1:0);
  if(key.d && Math.abs(steer)>0){
    speed*=1-0.015*dt;
    lateral+=steer*dt*(4.5+speed*.05);
    driftCharge+=dt*28;
    angle=THREE.MathUtils.lerp(angle,steer*.42,.18);
  }else{
    lateral=THREE.MathUtils.lerp(lateral,0,dt*.8);
    angle=THREE.MathUtils.lerp(angle,0,.15);
    if(driftCharge>30 && !key.d) driftCharge=Math.min(100,driftCharge);
  }
  lateral=THREE.MathUtils.clamp(lateral,-6.5,6.5);
  if(key.boost && driftCharge>5) driftCharge=Math.max(0,driftCharge-dt*48);
  distance+=speed*dt/145;
  if(distance>=1){distance-=1;lap++; if(lap>2){finish();return;}}
  const pose=trackPose(distance);
  const side=new THREE.Vector3(-pose.t.z,0,pose.t.x).normalize();
  playerKart.position.copy(pose.p).add(side.multiplyScalar(lateral));
  playerKart.position.y+=.55;
  playerKart.rotation.y=Math.atan2(pose.t.x,pose.t.z)+angle;
  const look=pose.p.clone().add(pose.t.clone().multiplyScalar(12));
  camera.position.lerp(playerKart.position.clone().add(new THREE.Vector3(0,5,10)),.12);
  camera.lookAt(look);
  for(let i=0;i<cpus.length;i++){
    cpus[i].progress+=dt*(0.010+i*.00035);
    const cp=trackPose(cpus[i].progress);
    cpus[i].mesh.position.copy(cp.p);
    cpus[i].mesh.position.y+=.55;
    cpus[i].mesh.rotation.y=Math.atan2(cp.t.x,cp.t.z);
  }
  document.getElementById('lap').textContent=Math.min(lap,2);
  document.getElementById('time').textContent=elapsed.toFixed(2);
  document.getElementById('boostFill').style.width=driftCharge+'%';
  document.getElementById('rank').textContent=1+cpus.filter(c=>c.progress>distance).length;
}
function finish(){
  running=false;
  const rank=document.getElementById('rank').textContent;
  const f=document.getElementById('finish');
  f.innerHTML='🏁 FINISH!<br><span style="font-size:30px">'+rank+'위 · '+elapsed.toFixed(2)+'초</span>';
  f.style.display='flex';
  setTimeout(()=>{document.getElementById('menu').style.display='flex';document.getElementById('start').textContent='다시 시작';},1800);
}

document.getElementById('start').onclick=()=>{
  document.getElementById('menu').style.display='none';
  document.getElementById('finish').style.display='none';
  distance=0;lap=1;speed=0;lateral=0;driftCharge=0;angle=0;elapsed=0;
  for(let i=0;i<cpus.length;i++)cpus[i].progress=(i+1)*.012;
  const c=document.getElementById('count');
  let n=3;c.textContent=n;
  const timer=setInterval(()=>{
    n--;
    if(n>0)c.textContent=n;
    else{c.textContent='GO!';running=true;startTime=performance.now();setTimeout(()=>c.textContent='',600);clearInterval(timer);}
  },850);
};

/* render */
function animate(){
  requestAnimationFrame(animate);
  update(Math.min(.035,clock.getDelta()));
  renderer.render(scene,camera);
}
const clock=new THREE.Clock();
camera.position.set(0,7,12);
camera.lookAt(0,0,0);
animate();
</script>
</body>
</html>
"""

components.html(HTML, height=780, scrolling=False)
'''

req = "streamlit>=1.40.0\n"

base = Path("/mnt/data/kart_highway_3d")
base.mkdir(exist_ok=True)
(base/"app.py").write_text(app_code, encoding="utf-8")
(base/"requirements.txt").write_text(req, encoding="utf-8")

zip_path = Path("/mnt/data/kart_highway_3d.zip")
with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as z:
    z.write(base/"app.py", "app.py")
    z.write(base/"requirements.txt", "requirements.txt")

print(zip_path)
