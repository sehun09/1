from pathlib import Path
import zipfile, shutil, textwrap

root = Path("/mnt/data/kart_highway_streamlit_final")
if root.exists():
    shutil.rmtree(root)
root.mkdir(parents=True)

app_code = r'''import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(
    page_title="3D Highway Kart",
    page_icon="🏎️",
    layout="wide",
    initial_sidebar_state="collapsed",
)

GAME_HTML = r"""
<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no, viewport-fit=cover">
<title>3D Highway Kart</title>
<style>
*{box-sizing:border-box}
html,body{
  margin:0;padding:0;width:100%;height:100%;overflow:hidden;
  background:#87ceeb;touch-action:none;
  -webkit-user-select:none;user-select:none;
  -webkit-touch-callout:none;
}
canvas{display:block;width:100%;height:100%;touch-action:none}
#hud{
  position:fixed;top:12px;left:12px;z-index:20;
  color:#fff;font-family:Arial,sans-serif;font-weight:800;
  text-shadow:0 2px 5px #000;pointer-events:none;
}
#title{font-size:20px}
#status{font-size:15px;margin-top:5px}
#countdown{
  position:fixed;left:50%;top:42%;transform:translate(-50%,-50%);
  z-index:30;color:#fff;font:bold 72px Arial;
  text-shadow:0 4px 10px #000;pointer-events:none;
}
#finish{
  display:none;position:fixed;inset:0;z-index:40;
  align-items:center;justify-content:center;flex-direction:column;
  background:rgba(0,0,0,.55);color:#fff;font-family:Arial;
}
#finish h1{font-size:54px;margin:0 0 12px}
#finish button{
  border:0;border-radius:14px;padding:14px 24px;
  font-size:20px;font-weight:800;cursor:pointer;
}
#mobileControls{
  position:fixed;left:0;right:0;bottom:max(10px,env(safe-area-inset-bottom));
  z-index:25;display:none;justify-content:space-between;
  align-items:flex-end;padding:0 12px;pointer-events:none;
}
.cluster{display:flex;gap:8px;pointer-events:auto}
.mbtn{
  width:64px;height:64px;border:2px solid rgba(255,255,255,.75);
  border-radius:18px;background:rgba(15,20,30,.60);color:#fff;
  display:flex;align-items:center;justify-content:center;
  font:bold 18px Arial;box-shadow:0 3px 12px rgba(0,0,0,.35);
  touch-action:none;-webkit-tap-highlight-color:transparent;
}
.mbtn:active,.mbtn.active{transform:scale(.93);background:rgba(255,255,255,.28)}
.mbtn.gas{font-size:30px}
@media (max-width:700px){
  #mobileControls{display:flex}
  #title{font-size:17px}
  #status{font-size:13px}
  .mbtn{width:58px;height:58px;border-radius:16px}
}
</style>
</head>
<body>

<div id="hud">
  <div id="title">🏎️ 3D HIGHWAY KART</div>
  <div id="status">LAP 1/2 · SPEED 0 · BOOST 0</div>
</div>
<div id="countdown">3</div>

<div id="finish">
  <h1>FINISH!</h1>
  <div id="finalTime" style="font-size:22px;margin-bottom:20px"></div>
  <button onclick="location.reload()">다시 하기</button>
</div>

<div id="mobileControls">
  <div class="cluster">
    <div class="mbtn" id="left">◀</div>
    <div class="mbtn" id="right">▶</div>
  </div>
  <div class="cluster">
    <div class="mbtn" id="drift">DRIFT</div>
    <div class="mbtn" id="boost">BOOST</div>
    <div class="mbtn gas" id="gas">▲</div>
  </div>
</div>

<script src="https://cdn.jsdelivr.net/npm/three@0.160.0/build/three.min.js"></script>
<script>
(() => {
"use strict";

/* -----------------------------
   기본 Three.js 설정
----------------------------- */
const scene = new THREE.Scene();
scene.background = new THREE.Color(0x9bdcff);
scene.fog = new THREE.Fog(0x9bdcff, 180, 850);

const camera = new THREE.PerspectiveCamera(
  65, innerWidth / innerHeight, 0.1, 1400
);

const renderer = new THREE.WebGLRenderer({
  antialias:true,
  powerPreference:"high-performance"
});
renderer.setPixelRatio(Math.min(devicePixelRatio || 1, 1.8));
renderer.setSize(innerWidth, innerHeight);
renderer.outputColorSpace = THREE.SRGBColorSpace;
document.body.appendChild(renderer.domElement);

scene.add(new THREE.HemisphereLight(0xffffff, 0x557755, 2.0));

const sun = new THREE.DirectionalLight(0xffffff, 2.2);
sun.position.set(180,260,100);
scene.add(sun);

/* -----------------------------
   원본 고가도로풍 레이아웃
   - 장거리 직선
   - 완만한 코너
   - 고가도로/헤어핀 느낌
   - 실제 카트라이더 맵 복제 아님
----------------------------- */
const points = [
  new THREE.Vector3(0, 0, 0),
  new THREE.Vector3(0, 0, -150),
  new THREE.Vector3(60, 0, -230),
  new THREE.Vector3(180, 0, -230),
  new THREE.Vector3(285, 0, -155),
  new THREE.Vector3(285, 0, 5),
  new THREE.Vector3(235, 0, 90),
  new THREE.Vector3(110, 0, 135),
  new THREE.Vector3(-30, 0, 130),
  new THREE.Vector3(-150, 0, 80),
  new THREE.Vector3(-205, 0, -15),
  new THREE.Vector3(-200, 0, -105),
  new THREE.Vector3(-135, 0, -185),
  new THREE.Vector3(-50, 0, -210)
];

const track = new THREE.CatmullRomCurve3(
  points, true, "catmullrom", 0.38
);

const TRACK_WIDTH = 13;
const TRACK_SAMPLES = 520;

/* -----------------------------
   지형
----------------------------- */
const ground = new THREE.Mesh(
  new THREE.PlaneGeometry(1800,1800),
  new THREE.MeshLambertMaterial({color:0x679b5a})
);
ground.rotation.x = -Math.PI/2;
ground.position.y = -0.08;
scene.add(ground);

/* -----------------------------
   도로 생성
----------------------------- */
function buildRoad(){
  const positions = [];
  const indices = [];
  const uvs = [];

  for(let i=0;i<TRACK_SAMPLES;i++){
    const t=i/TRACK_SAMPLES;
    const p=track.getPointAt(t);
    const tangent=track.getTangentAt(t).normalize();
    const side=new THREE.Vector3(-tangent.z,0,tangent.x).normalize();

    const left=p.clone().addScaledVector(side,TRACK_WIDTH);
    const right=p.clone().addScaledVector(side,-TRACK_WIDTH);

    positions.push(left.x,0.02,left.z);
    positions.push(right.x,0.02,right.z);

    uvs.push(0,t*12);
    uvs.push(1,t*12);

    const n=(i+1)%TRACK_SAMPLES;
    indices.push(i*2,i*2+1,n*2);
    indices.push(i*2+1,n*2+1,n*2);
  }

  const geo=new THREE.BufferGeometry();
  geo.setAttribute("position",new THREE.Float32BufferAttribute(positions,3));
  geo.setAttribute("uv",new THREE.Float32BufferAttribute(uvs,2));
  geo.setIndex(indices);
  geo.computeVertexNormals();

  const mesh=new THREE.Mesh(
    geo,
    new THREE.MeshLambertMaterial({color:0x303238,side:THREE.DoubleSide})
  );
  scene.add(mesh);
}
buildRoad();

/* -----------------------------
   차선 중앙선
----------------------------- */
function buildLaneMarks(){
  const geo=new THREE.BufferGeometry();
  const arr=[];
  const count=260;

  for(let i=0;i<count;i++){
    const t=i/count;
    const p=track.getPointAt(t);
    const tan=track.getTangentAt(t).normalize();
    const side=new THREE.Vector3(-tan.z,0,tan.x).normalize();
    const a=p.clone().addScaledVector(tan,1.8);
    const b=p.clone().addScaledVector(tan,5.2);
    a.y=b.y=0.08;
    arr.push(a.x,a.y,a.z,b.x,b.y,b.z);
  }

  geo.setAttribute("position",new THREE.Float32BufferAttribute(arr,3));
  const mat=new THREE.LineBasicMaterial({color:0xffffff});
  scene.add(new THREE.LineSegments(geo,mat));
}
buildLaneMarks();

/* -----------------------------
   연석
----------------------------- */
function buildCurbs(){
  const group=new THREE.Group();
  const count=180;

  for(let i=0;i<count;i++){
    const t=i/count;
    const p=track.getPointAt(t);
    const tan=track.getTangentAt(t).normalize();
    const side=new THREE.Vector3(-tan.z,0,tan.x).normalize();

    for(const sign of [-1,1]){
      const block=new THREE.Mesh(
        new THREE.BoxGeometry(2.8,0.22,0.7),
        new THREE.MeshLambertMaterial({
          color:(i%2===0)?0xf4f4f4:0xd92d2d
        })
      );
      block.position.copy(p).addScaledVector(side,sign*(TRACK_WIDTH+0.8));
      block.position.y=0.16;
      block.rotation.y=Math.atan2(tan.x,tan.z);
      group.add(block);
    }
  }
  scene.add(group);
}
buildCurbs();

/* -----------------------------
   가드레일 + 기둥
----------------------------- */
function buildGuardrails(){
  const group=new THREE.Group();
  const count=90;

  for(let i=0;i<count;i++){
    const t=i/count;
    const p=track.getPointAt(t);
    const tan=track.getTangentAt(t).normalize();
    const side=new THREE.Vector3(-tan.z,0,tan.x).normalize();

    for(const sign of [-1,1]){
      const rail=new THREE.Mesh(
        new THREE.BoxGeometry(5.5,0.42,0.12),
        new THREE.MeshLambertMaterial({color:0x777c82})
      );
      rail.position.copy(p).addScaledVector(side,sign*(TRACK_WIDTH+2.0));
      rail.position.y=0.9;
      rail.rotation.y=Math.atan2(tan.x,tan.z);
      group.add(rail);
    }
  }
  scene.add(group);
}
buildGuardrails();

/* -----------------------------
   나무
----------------------------- */
function addTree(pos, scale=1){
  const g=new THREE.Group();

  const trunk=new THREE.Mesh(
    new THREE.CylinderGeometry(.22,.32,2.2,8),
    new THREE.MeshLambertMaterial({color:0x79512f})
  );
  trunk.position.y=1.1;
  g.add(trunk);

  const crown=new THREE.Mesh(
    new THREE.ConeGeometry(1.6,3.8,8),
    new THREE.MeshLambertMaterial({color:0x2d7c3b})
  );
  crown.position.y=3.6;
  g.add(crown);

  g.position.copy(pos);
  g.scale.setScalar(scale);
  scene.add(g);
}

for(let i=0;i<80;i++){
  const t=(i/80+0.013)%1;
  const p=track.getPointAt(t);
  const tan=track.getTangentAt(t).normalize();
  const side=new THREE.Vector3(-tan.z,0,tan.x).normalize();
  const sign=i%2?1:-1;
  const offset=22+(i%5)*3;
  const pos=p.clone().addScaledVector(side,sign*offset);
  addTree(pos,0.7+(i%4)*0.13);
}

/* -----------------------------
   고가도로 느낌의 교량 지지대
----------------------------- */
function addBridgeSupport(pos){
  for(const x of [-4,4]){
    const pillar=new THREE.Mesh(
      new THREE.BoxGeometry(1.2,7,1.2),
      new THREE.MeshLambertMaterial({color:0x6f7378})
    );
    pillar.position.set(pos.x+x,3.5,pos.z);
    scene.add(pillar);
  }
  const beam=new THREE.Mesh(
    new THREE.BoxGeometry(12,0.9,1.4),
    new THREE.MeshLambertMaterial({color:0x85898d})
  );
  beam.position.set(pos.x,7.2,pos.z);
  scene.add(beam);
}

for(let i=0;i<12;i++){
  const t=0.10+i*0.055;
  const p=track.getPointAt(t%1);
  addBridgeSupport(p);
}

/* -----------------------------
   카트
----------------------------- */
function makeKart(bodyColor){
  const g=new THREE.Group();

  const body=new THREE.Mesh(
    new THREE.BoxGeometry(2.25,.68,3.5),
    new THREE.MeshLambertMaterial({color:bodyColor})
  );
  body.position.y=.7;
  g.add(body);

  const nose=new THREE.Mesh(
    new THREE.BoxGeometry(1.55,.42,1.25),
    new THREE.MeshLambertMaterial({color:0xe8e8e8})
  );
  nose.position.set(0,.85,-1.25);
  g.add(nose);

  const seat=new THREE.Mesh(
    new THREE.BoxGeometry(1.2,.7,1.05),
    new THREE.MeshLambertMaterial({color:0x171717})
  );
  seat.position.set(0,1.1,.45);
  g.add(seat);

  for(const x of [-1,1]){
    for(const z of [-1.15,1.15]){
      const wheel=new THREE.Mesh(
        new THREE.CylinderGeometry(.39,.39,.30,12),
        new THREE.MeshLambertMaterial({color:0x151515})
      );
      wheel.rotation.z=Math.PI/2;
      wheel.position.set(x*1.18,.43,z);
      g.add(wheel);
    }
  }

  const spoiler=new THREE.Mesh(
    new THREE.BoxGeometry(2.3,.18,.45),
    new THREE.MeshLambertMaterial({color:0x222222})
  );
  spoiler.position.set(0,1.12,1.55);
  g.add(spoiler);

  return g;
}

const player=makeKart(0x2778ff);
scene.add(player);

const cpuColors=[0xf23b3b,0xffc400,0x45c85a,0x9a5cff,0xff7b22];
const cpu=[];

cpuColors.forEach((color,i)=>{
  const mesh=makeKart(color);
  scene.add(mesh);
  cpu.push({
    mesh,
    t:(i+1)*0.012,
    speed:0.0104+i*0.00028,
    lane:(i%3)-1
  });
});

/* -----------------------------
   입력
----------------------------- */
const keys={
  up:false,down:false,left:false,right:false,
  drift:false,boost:false
};

addEventListener("keydown",e=>{
  if(e.code==="ArrowUp")keys.up=true;
  if(e.code==="ArrowDown")keys.down=true;
  if(e.code==="ArrowLeft")keys.left=true;
  if(e.code==="ArrowRight")keys.right=true;
  if(e.code==="ShiftLeft"||e.code==="ShiftRight")keys.drift=true;
  if(e.code==="Space")keys.boost=true;
});
addEventListener("keyup",e=>{
  if(e.code==="ArrowUp")keys.up=false;
  if(e.code==="ArrowDown")keys.down=false;
  if(e.code==="ArrowLeft")keys.left=false;
  if(e.code==="ArrowRight")keys.right=false;
  if(e.code==="ShiftLeft"||e.code==="ShiftRight")keys.drift=false;
  if(e.code==="Space")keys.boost=false;
});

function bindTouch(id,key){
  const el=document.getElementById(id);
  if(!el)return;

  const down=e=>{
    e.preventDefault();
    keys[key]=true;
    el.classList.add("active");
    try{el.setPointerCapture(e.pointerId)}catch(_){}
  };
  const up=e=>{
    e.preventDefault();
    keys[key]=false;
    el.classList.remove("active");
  };

  el.addEventListener("pointerdown",down,{passive:false});
  el.addEventListener("pointerup",up,{passive:false});
  el.addEventListener("pointercancel",up,{passive:false});
}

bindTouch("left","left");
bindTouch("right","right");
bindTouch("gas","up");
bindTouch("drift","drift");
bindTouch("boost","boost");

document.addEventListener("touchmove",e=>e.preventDefault(),{passive:false});

/* -----------------------------
   레이스
----------------------------- */
let progress=0;
let speed=0;
let boost=100;
let driftCharge=0;
let drifting=false;
let lap=1;
let started=false;
let finished=false;
let raceTime=0;

const countdown=document.getElementById("countdown");
const status=document.getElementById("status");
const finish=document.getElementById("finish");
const finalTime=document.getElementById("finalTime");

let count=3;
const countTimer=setInterval(()=>{
  count--;
  if(count>0) countdown.textContent=count;
  else if(count===0) countdown.textContent="GO!";
  else{
    countdown.style.display="none";
    started=true;
    clearInterval(countTimer);
  }
},1000);

function updatePlayer(dt){
  if(!started||finished)return;

  raceTime+=dt;

  let acceleration=keys.up ? 31 : -10;
  speed += acceleration*dt;

  if(keys.down) speed-=38*dt;

  const maxNormal=34;
  const maxBoost=49;

  if(keys.boost && boost>0){
    speed+=20*dt;
    boost-=27*dt;
  }

  speed=THREE.MathUtils.clamp(
    speed,0,(keys.boost&&boost>0)?maxBoost:maxNormal
  );

  const steer=(keys.left?-1:0)+(keys.right?1:0);

  if(keys.drift && Math.abs(steer)>0 && speed>8){
    drifting=true;
    driftCharge+=dt*(7+speed*.15);
  }else{
    if(drifting && driftCharge>=2.0){
      boost=Math.min(100,boost+driftCharge*5.0);
    }
    drifting=false;
    driftCharge=0;
  }

  const tangent=track.getTangentAt(progress).normalize();
  const length=track.getLength();

  progress += speed*dt/length;
  if(progress>=1) progress-=1;

  const p=track.getPointAt(progress);
  const tan=track.getTangentAt(progress).normalize();
  const side=new THREE.Vector3(-tan.z,0,tan.x).normalize();

  const steeringPower=drifting ? 5.3 : 2.2;
  p.addScaledVector(side,steer*steeringPower*dt*speed/12);

  player.position.copy(p);
  player.position.y=.08;

  const baseRot=Math.atan2(tan.x,tan.z);
  player.rotation.y=baseRot+(drifting?steer*.24:0);

  /* 랩 */
  const newLap=Math.floor(progress*2)+1;
  if(newLap>lap)lap=newLap;

  /* 2바퀴 완료 */
  if(raceTime>4 && progress<0.025 && lap>=2){
    finished=true;
    finish.style.display="flex";
    finalTime.textContent="기록: "+raceTime.toFixed(2)+"초";
  }
}

function updateCPU(dt){
  cpu.forEach((car,i)=>{
    car.t=(car.t+car.speed*dt)%1;
    const p=track.getPointAt(car.t);
    const tan=track.getTangentAt(car.t).normalize();
    const side=new THREE.Vector3(-tan.z,0,tan.x).normalize();

    p.addScaledVector(side,car.lane*3.2);
    car.mesh.position.copy(p);
    car.mesh.position.y=.08;
    car.mesh.rotation.y=Math.atan2(tan.x,tan.z);
  });
}

/* -----------------------------
   카메라
----------------------------- */
function updateCamera(){
  const t=track.getTangentAt(progress).normalize();
  const cam=player.position.clone().addScaledVector(t,-11);
  cam.y+=5.4;

  camera.position.lerp(cam,.11);

  const look=player.position.clone()
    .addScaledVector(t,4)
    .add(new THREE.Vector3(0,1.2,0));

  camera.lookAt(look);
}

let last=performance.now();

function animate(now){
  requestAnimationFrame(animate);

  const dt=Math.min((now-last)/1000,.04);
  last=now;

  updatePlayer(dt);
  updateCPU(dt);
  updateCamera();

  const shownLap=Math.min(lap,2);
  status.textContent=
    "LAP "+shownLap+"/2 · SPEED "+Math.round(speed)+
    " · BOOST "+Math.round(boost)+
    (drifting?" · DRIFT":"");

  renderer.render(scene,camera);
}

camera.position.set(0,7,15);
requestAnimationFrame(animate);

addEventListener("resize",()=>{
  camera.aspect=innerWidth/innerHeight;
  camera.updateProjectionMatrix();
  renderer.setSize(innerWidth,innerHeight);
});
})();
</script>
</body>
</html>
"""

components.html(GAME_HTML, height=760, scrolling=False)
'''

requirements = """streamlit>=1.40,<2.0
"""

readme = """# 3D Highway Kart — Streamlit Cloud

## 실행
1. GitHub 저장소에 `app.py`와 `requirements.txt`를 업로드합니다.
2. Streamlit Cloud에서 해당 저장소를 연결합니다.
3. Main file을 `app.py`로 지정합니다.
4. Deploy합니다.

## 조작

### PC
- ↑ : 가속
- ↓ : 브레이크
- ← / → : 조향
- Shift : 드리프트
- Space : 부스트

### 스마트폰
화면 아래 버튼을 터치합니다.
- ◀ / ▶ : 조향
- ▲ : 가속
- DRIFT : 드리프트
- BOOST : 부스트

## 특징
- Three.js 기반 3D 레이싱
- 고가도로풍의 오리지널 폐쇄형 트랙
- 2랩
- CPU 카트 5대
- 드리프트 → 부스트 게이지
- 모바일 터치 조작
- PC 키보드 조작
- Streamlit Cloud에서 별도 서버 없이 실행

실제 KartRider의 맵/캐릭터/에셋을 복제하지 않고, 고가도로 스타일의 오리지널 트랙으로 구성되어 있습니다.
"""

(root/"app.py").write_text(app_code, encoding="utf-8")
(root/"requirements.txt").write_text(requirements, encoding="utf-8")
(root/"README.md").write_text(readme, encoding="utf-8")

# Validate Python syntax before packaging.
compile(app_code, "app.py", "exec")

out = Path("/mnt/data/kart_highway_streamlit_final.zip")
if out.exists():
    out.unlink()

with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
    for p in root.iterdir():
        z.write(p, p.name)

print(f"완성: {out}")
print("파일:", [p.name for p in root.iterdir()])
