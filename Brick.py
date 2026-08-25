import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="30단계 벽돌깨기", layout="centered")

components.html("""
<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<style>
body{margin:0;background:#111;font-family:Arial;color:white}
.wrap{max-width:820px;margin:auto;text-align:center}
canvas{background:#000;border:3px solid white;width:100%}
button{
padding:8px 18px;margin:4px;border:none;
border-radius:8px;font-size:16px;cursor:pointer;
}
#slow{background:#4caf50;color:white}
#normal{background:#2196f3;color:white}
#fast{background:#f44336;color:white}
.info{font-size:20px;margin:10px}
</style>
</head>
<body>
<div class="wrap">
<h2>🧱 30단계 벽돌깨기</h2>

<canvas id="c" width="800" height="600"></canvas>

<div class="info">
LEVEL <span id="lv">1</span> |
점수 <span id="score">0</span> |
목숨 <span id="life">3</span> |
공 <span id="balls">1</span>
</div>

<div>
<button id="slow" onclick="setSpeed(3)">느림</button>
<button id="normal" onclick="setSpeed(5)">보통</button>
<button id="fast" onclick="setSpeed(7)">빠름</button>
</div>
</div>

<script>
const cvs=document.getElementById("c");
const ctx=cvs.getContext("2d");

let level=1,score=0,lives=3;
let baseSpeed=5;
let paddle={x:340,y:570,w:120,h:12};
let left=false,right=false;

let balls=[];
let bricks=[];
let items=[];

function newBall(x,y){
return{
x,y,r:8,
dx:(Math.random()*2-1)*baseSpeed,
dy:-baseSpeed
};
}

function setSpeed(v){
baseSpeed=v;
balls.forEach(b=>{
let sx=Math.sign(b.dx)||1;
let sy=Math.sign(b.dy)||-1;
b.dx=sx*baseSpeed;
b.dy=sy*baseSpeed;
});
}

function makeLevel(lv){

bricks=[];

let rows=3+Math.floor((lv-1)/3);
if(rows>8)rows=8;

let cols=6+((lv-1)%5);
if(cols>10)cols=10;

let bw=68,bh=22,p=8;
let startX=(800-(cols*bw+(cols-1)*p))/2;

for(let r=0;r<rows;r++){
for(let c=0;c<cols;c++){

let alive=true;

// 레벨별 패턴
if(lv%2==0 && (r+c)%3==0)alive=false;
if(lv%5==0 && c==Math.floor(cols/2))alive=false;
if(lv%7==0 && r==0)alive=false;

if(alive){
bricks.push({
x:startX+c*(bw+p),
y:50+r*(bh+p),
w:bw,h:bh,
hp:1
});
}
}
}
}

function resetStage(){
balls=[newBall(400,520)];
items=[];
paddle.x=340;
document.getElementById("balls").innerText=balls.length;
}

makeLevel(level);
resetStage();

document.addEventListener("keydown",e=>{
if(e.key=="ArrowLeft")left=true;
if(e.key=="ArrowRight")right=true;
});
document.addEventListener("keyup",e=>{
if(e.key=="ArrowLeft")left=false;
if(e.key=="ArrowRight")right=false;
});

cvs.addEventListener("mousemove",e=>{
const rect=cvs.getBoundingClientRect();
let mx=(e.clientX-rect.left)*(800/rect.width);
paddle.x=mx-paddle.w/2;
});

function drawBrick(b,i){
const colors=["#f44336","#ff9800","#ffeb3b","#4caf50","#00bcd4","#3f51b5"];
ctx.fillStyle=colors[i%colors.length];
ctx.fillRect(b.x,b.y,b.w,b.h);
}

function drawItem(it){
ctx.beginPath();
ctx.fillStyle="#00ff88";
ctx.arc(it.x,it.y,10,0,Math.PI*2);
ctx.fill();
ctx.fillStyle="#000";
ctx.font="12px Arial";
ctx.fillText("+",it.x-3,it.y+4);
}

function collision(ball){

if(ball.x<ball.r||ball.x>800-ball.r)ball.dx*=-1;
if(ball.y<ball.r)ball.dy*=-1;

// 패들
if(ball.y+ball.r>paddle.y &&
ball.x>paddle.x &&
ball.x<paddle.x+paddle.w &&
ball.dy>0){

let hit=(ball.x-(paddle.x+paddle.w/2))/50;
ball.dx=hit*baseSpeed;
ball.dy=-Math.abs(baseSpeed);
}

// 벽돌
for(let i=0;i<bricks.length;i++){
let b=bricks[i];
if(ball.x>b.x&&ball.x<b.x+b.w&&
ball.y>b.y&&ball.y<b.y+b.h){

ball.dy*=-1;
bricks.splice(i,1);
score++;
document.getElementById("score").innerText=score;

// 아이템 생성
items.push({
x:b.x+b.w/2,
y:b.y+b.h/2,
dy:2
});
break;
}
}
}

function update(){

if(left)paddle.x-=8;
if(right)paddle.x+=8;

if(paddle.x<0)paddle.x=0;
if(paddle.x>800-paddle.w)paddle.x=800-paddle.w;

// 아이템
for(let i=items.length-1;i>=0;i--){
let it=items[i];
it.y+=it.dy;

if(it.y>paddle.y &&
it.x>paddle.x &&
it.x<paddle.x+paddle.w){

balls.push(newBall(it.x,it.y));
document.getElementById("balls").innerText=balls.length;
items.splice(i,1);
}
else if(it.y>600){
items.splice(i,1);
}
}

// 공
for(let i=balls.length-1;i>=0;i--){
let b=balls[i];

b.x+=b.dx;
b.y+=b.dy;

collision(b);

if(b.y>620){
balls.splice(i,1);
}
}

if(balls.length==0){
lives--;
document.getElementById("life").innerText=lives;

if(lives<=0){
alert("게임 오버");
level=1;score=0;lives=3;
document.getElementById("score").innerText=0;
document.getElementById("life").innerText=3;
document.getElementById("lv").innerText=1;
makeLevel(level);
}
resetStage();
}

// 클리어
if(bricks.length==0){

if(level==30){
alert("🏆 30단계 클리어!");
level=1;
score=0;
lives=3;
document.getElementById("score").innerText=0;
document.getElementById("life").innerText=3;
}else{
level++;
}

document.getElementById("lv").innerText=level;
makeLevel(level);
resetStage();
}
}

function draw(){

ctx.clearRect(0,0,800,600);

// 벽돌
bricks.forEach((b,i)=>drawBrick(b,i));

// 패들
ctx.fillStyle="#2196f3";
ctx.fillRect(paddle.x,paddle.y,paddle.w,paddle.h);

// 공
ctx.fillStyle="white";
balls.forEach(b=>{
ctx.beginPath();
ctx.arc(b.x,b.y,b.r,0,Math.PI*2);
ctx.fill();
});

// 아이템
items.forEach(drawItem);

update();
requestAnimationFrame(draw);
}

draw();

</script>
</body>
</html>
""",height=760)
