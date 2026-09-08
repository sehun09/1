import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(
    page_title="3D Highway Kart",
    page_icon="🏎️",
    layout="wide",
)

GAME = r"""
<!DOCTYPE html>
<html>
<head>
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<style>
html,body{
    margin:0;
    padding:0;
    width:100%;
    height:100%;
    overflow:hidden;
    background:#87ceeb;
    font-family:Arial,sans-serif;
}
#game{
    position:fixed;
    left:0;
    top:0;
    width:100vw;
    height:100vh;
}
canvas{
    display:block;
    width:100%;
    height:100%;
}
#hud{
    position:fixed;
    top:18px;
    left:20px;
    color:white;
    font-weight:bold;
    text-shadow:0 3px 7px #000;
    z-index:10;
    pointer-events:none;
}
.title{
    font-size:28px;
}
.info{
    margin-top:8px;
    font-size:19px;
}
#count{
    position:fixed;
    left:50%;
    top:50%;
    transform:translate(-50%,-50%);
    color:white;
    font-size:90px;
    font-weight:bold;
    text-shadow:0 5px 15px #000;
    z-index:20;
}
#buttons{
    position:fixed;
    bottom:25px;
    left:0;
    right:0;
    display:flex;
    justify-content:space-between;
    padding:0 25px;
    z-index:30;
    pointer-events:none;
}
.side{
    display:flex;
    gap:12px;
}
button{
    pointer-events:auto;
    width:72px;
    height:72px;
    border:0;
    border-radius:20px;
    background:rgba(0,0,0,.65);
    color:white;
    font-size:30px;
    font-weight:bold;
    touch-action:none;
}
#boost{
    width:90px;
    font-size:18px;
}
</style>
</head>

<body>

<div id="game"></div>

<div id="hud">
    <div class="title">🏎️ 3D HIGHWAY KART</div>
    <div class="info">
        LAP <span id="lap">1</span>/2
        · SPEED <span id="speed">0</span>
        · BOOST <span id="boostText">100</span>
    </div>
</div>

<div id="count">3</div>

<div id="buttons">
    <div class="side">
        <button id="left">◀</button>
        <button id="right">▶</button>
    </div>
    <div class="side">
        <button id="brake">▼</button>
        <button id="gas">▲</button>
        <button id="boost">BOOST</button>
    </div>
</div>

<script>
const canvas=document.createElement("canvas");
document.getElementById("game").appendChild(canvas);

const gl=canvas.getContext("webgl",{antialias:true});

if(!gl){
    document.getElementById("count").innerText="WebGL 없음";
    throw new Error("WebGL not supported");
}

/* ---------------- SHADER ---------------- */

const vs=`
attribute vec3 position;
uniform mat4 projection;
uniform mat4 rotation;
uniform vec3 offset;
uniform float scale;

void main(){
    vec3 p=position*scale+offset;
    p=vec3(
        rotation[0].x*p.x+rotation[1].x*p.y+rotation[2].x*p.z,
        rotation[0].y*p.x+rotation[1].y*p.y+rotation[2].y*p.z,
        rotation[0].z*p.x+rotation[1].z*p.y+rotation[2].z*p.z
    );
    gl_Position=projection*vec4(p,1.0);
}
`;

const fs=`
precision mediump float;
uniform vec4 color;
void main(){
    gl_FragColor=color;
}
`;

function shader(type,src){
    const s=gl.createShader(type);
    gl.shaderSource(s,src);
    gl.compileShader(s);
    return s;
}

const program=gl.createProgram();
gl.attachShader(program,shader(gl.VERTEX_SHADER,vs));
gl.attachShader(program,shader(gl.FRAGMENT_SHADER,fs));
gl.linkProgram(program);
gl.useProgram(program);

const posLoc=gl.getAttribLocation(program,"position");
const projLoc=gl.getUniformLocation(program,"projection");
const rotLoc=gl.getUniformLocation(program,"rotation");
const offLoc=gl.getUniformLocation(program,"offset");
const scaleLoc=gl.getUniformLocation(program,"scale");
const colorLoc=gl.getUniformLocation(program,"color");

gl.enableVertexAttribArray(posLoc);
gl.enable(gl.DEPTH_TEST);

/* ---------------- 3D MATH ---------------- */

function perspective(fov,aspect,near,far){
    const f=1/Math.tan(fov/2);
    return new Float32Array([
        f/aspect,0,0,0,
        0,f,0,0,
        0,0,(far+near)/(near-far),-1,
        0,0,(2*far*near)/(near-far),0
    ]);
}

function identity(){
    return new Float32Array([
        1,0,0,
        0,1,0,
        0,0,1
    ]);
}

function rotateY(a){
    const c=Math.cos(a),s=Math.sin(a);
    return new Float32Array([
        c,0,-s,
        0,1,0,
        s,0,c
    ]);
}

function rotateX(a){
    const c=Math.cos(a),s=Math.sin(a);
    return new Float32Array([
        1,0,0,
        0,c,s,
        0,-s,c
    ]);
}

/* ---------------- CUBE ---------------- */

const cube=[
 -1,-1,-1,  1,-1,-1,  1,1,-1,
 -1,-1,-1,  1,1,-1, -1,1,-1,

 -1,-1,1,  1,-1,1,  1,1,1,
 -1,-1,1,  1,1,1, -1,1,1,

 -1,-1,-1, -1,1,-1, -1,1,1,
 -1,-1,-1, -1,1,1, -1,-1,1,

 1,-1,-1, 1,1,-1, 1,1,1,
 1,-1,-1, 1,1,1, 1,-1,1,

 -1,1,-1, 1,1,-1, 1,1,1,
 -1,1,-1, 1,1,1, -1,1,1,

 -1,-1,-1, 1,-1,-1, 1,-1,1,
 -1,-1,-1, 1,-1,1, -1,-1,1
];

const buffer=gl.createBuffer();
gl.bindBuffer(gl.ARRAY_BUFFER,buffer);
gl.bufferData(gl.ARRAY_BUFFER,new Float32Array(cube),gl.STATIC_DRAW);
gl.vertexAttribPointer(posLoc,3,gl.FLOAT,false,0,0);

function drawCube(x,y,z,sx,sy,sz,color,ry=0){
    gl.uniformMatrix3fv(rotLoc,false,rotateY(ry));
    gl.uniform3f(offLoc,x,y,z);
    gl.uniform1f(scaleLoc,1);

    gl.vertexAttribPointer(posLoc,3,gl.FLOAT,false,0,0);

    /* 크기 변형 */
    const old=gl.getUniformLocation(program,"unused");

    gl.uniform4f(colorLoc,color[0],color[1],color[2],1);

    /* 큐브 크기는 offset 주변에서 처리 */
    gl.drawArrays(gl.TRIANGLES,0,cube.length/3);
}

/* ---------------- WORLD ---------------- */

let playerZ=0;
let playerX=0;
let speed=0;
let angle=0;
let boost=100;
let lap=1;

const keys={
    left:false,
    right:false,
    gas:false,
    brake:false,
    boost:false
};

function bind(id,key){
    const b=document.getElementById(id);

    b.addEventListener("pointerdown",e=>{
        e.preventDefault();
        keys[key]=true;
    });

    b.addEventListener("pointerup",e=>{
        e.preventDefault();
        keys[key]=false;
    });

    b.addEventListener("pointerleave",()=>{
        keys[key]=false;
    });
}

bind("left","left");
bind("right","right");
bind("gas","gas");
bind("brake","brake");
bind("boost","boost");

document.addEventListener("keydown",e=>{
    if(e.key==="ArrowLeft"||e.key==="a")keys.left=true;
    if(e.key==="ArrowRight"||e.key==="d")keys.right=true;
    if(e.key==="ArrowUp"||e.key==="w")keys.gas=true;
    if(e.key==="ArrowDown"||e.key==="s")keys.brake=true;
    if(e.code==="Space")keys.boost=true;
});

document.addEventListener("keyup",e=>{
    if(e.key==="ArrowLeft"||e.key==="a")keys.left=false;
    if(e.key==="ArrowRight"||e.key==="d")keys.right=false;
    if(e.key==="ArrowUp"||e.key==="w")keys.gas=false;
    if(e.key==="ArrowDown"||e.key==="s")keys.brake=false;
    if(e.code==="Space")keys.boost=false;
});

/* ---------------- COUNTDOWN ---------------- */

let countdown=3;

const timer=setInterval(()=>{
    countdown--;

    if(countdown>0){
        document.getElementById("count").innerText=countdown;
    }else{
        document.getElementById("count").innerText="GO!";
        setTimeout(()=>{
            document.getElementById("count").style.display="none";
        },600);
        clearInterval(timer);
    }
},1000);

/* ---------------- DRAW ---------------- */

function resize(){
    canvas.width=window.innerWidth*devicePixelRatio;
    canvas.height=window.innerHeight*devicePixelRatio;
    gl.viewport(0,0,canvas.width,canvas.height);
}

window.addEventListener("resize",resize);
resize();

let last=performance.now();

function update(dt){

    if(countdown>0)return;

    if(keys.gas)speed+=35*dt;
    else speed-=12*dt;

    if(keys.brake)speed-=45*dt;

    speed=Math.max(0,Math.min(150,speed));

    if(keys.boost && boost>0 && speed>20){
        speed+=70*dt;
        boost-=25*dt;
    }else{
        boost+=8*dt;
    }

    boost=Math.max(0,Math.min(100,boost));

    if(keys.left){
        angle+=2.4*dt;
        playerX-=45*dt*(speed/100);
    }

    if(keys.right){
        angle-=2.4*dt;
        playerX+=45*dt*(speed/100);
    }

    playerX*=0.995;

    if(Math.abs(playerX)>6){
        speed-=30*dt;
    }

    playerZ+=speed*dt;

    if(playerZ>1000){
        playerZ=0;
        lap++;

        if(lap>2){
            lap=2;
            speed=0;
            document.getElementById("count").innerText="FINISH!";
            document.getElementById("count").style.display="block";
        }
    }

    document.getElementById("speed").innerText=Math.round(speed);
    document.getElementById("boostText").innerText=Math.round(boost);
    document.getElementById("lap").innerText=lap;
}

/* ---------------- ROAD ---------------- */

function road(){

    for(let z=playerZ-100;z<playerZ+700;z+=20){

        let curve=Math.sin(z*0.008)*20;
        let y=0;

        /* 도로 */
        drawCube(
            curve,
            y,
            z-playerZ,
            1,1,1,
            [0.08,0.08,0.09]
        );

        /* 차선 */
        if(Math.floor(z/20)%2===0){
            drawCube(
                curve,
                1.02,
                z-playerZ,
                1,1,1,
                [1,1,1]
            );
        }

        /* 중앙선 */
        drawCube(
            curve,
            1.03,
            z-playerZ,
            1,1,1,
            [1,0.8,0]
        );

        /* 가드레일 */
        drawCube(
            curve-8,
            2,
            z-playerZ,
            1,1,1,
            [0.7,0.7,0.72]
        );

        drawCube(
            curve+8,
            2,
            z-playerZ,
            1,1,1,
            [0.7,0.7,0.72]
        );
    }
}

/* ---------------- KART ---------------- */

function kart(){

    const z=8;

    /* 차체 */
    drawCube(
        playerX,
        3,
        z,
        1,1,1,
        [0.95,0.08,0.03],
        angle
    );

    /* 앞부분 */
    drawCube(
        playerX,
        4,
        z-1,
        1,1,1,
        [1,0.25,0.05],
        angle
    );

    /* 운전자 */
    drawCube(
        playerX,
        5,
        z,
        1,1,1,
        [0.1,0.2,0.8],
        angle
    );

    /* 바퀴 */
    drawCube(playerX-1.2,2.2,z+1,1,1,1,[0.02,0.02,0.02]);
    drawCube(playerX+1.2,2.2,z+1,1,1,1,[0.02,0.02,0.02]);
    drawCube(playerX-1.2,2.2,z-1,1,1,1,[0.02,0.02,0.02]);
    drawCube(playerX+1.2,2.2,z-1,1,1,1,[0.02,0.02,0.02]);
}

/* ---------------- LOOP ---------------- */

function render(){

    const now=performance.now();
    const dt=Math.min((now-last)/1000,0.05);
    last=now;

    update(dt);

    gl.clearColor(0.35,0.68,0.9,1);
    gl.clear(gl.COLOR_BUFFER_BIT|gl.DEPTH_BUFFER_BIT);

    const projection=perspective(
        Math.PI/3,
        canvas.width/canvas.height,
        0.1,
        2000
    );

    gl.uniformMatrix4fv(projLoc,false,projection);

    /*
       간단한 카메라 효과를 위해
       전체 월드를 아래쪽으로 이동
    */

    road();
    kart();

    requestAnimationFrame(render);
}

render();
</script>
</body>
</html>
"""

components.html(
    GAME,
    height=760,
    scrolling=False
)
