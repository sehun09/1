import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(
    page_title="Kart Racing",
    page_icon="🏎️",
    layout="centered"
)

st.title("🏎️ Kart Racing")

game_html = """
<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">

<style>
    body {
        margin: 0;
        background: #111;
        font-family: Arial, sans-serif;
        overflow: hidden;
    }

    #game {
        width: 100%;
        max-width: 700px;
        height: 650px;
        margin: auto;
        position: relative;
        overflow: hidden;
        background: #333;
        border: 4px solid white;
        box-sizing: border-box;
    }

    #road {
        position: absolute;
        left: 15%;
        width: 70%;
        height: 100%;
        background: #555;
        overflow: hidden;
    }

    .lane {
        position: absolute;
        width: 8px;
        height: 70px;
        background: white;
        left: 33.33%;
        opacity: 0.8;
    }

    .lane2 {
        position: absolute;
        width: 8px;
        height: 70px;
        background: white;
        left: 66.66%;
        opacity: 0.8;
    }

    .side {
        position: absolute;
        width: 15%;
        height: 100%;
        background: #3d9b40;
    }

    #leftSide {
        left: 0;
    }

    #rightSide {
        right: 0;
    }

    #player {
        position: absolute;
        width: 55px;
        height: 85px;
        background: #e53935;
        border-radius: 14px;
        bottom: 50px;
        left: calc(50% - 27px);
        z-index: 10;
        box-shadow: 0 5px 10px #000;
    }

    #player::before {
        content: "";
        position: absolute;
        width: 35px;
        height: 25px;
        background: #222;
        top: 10px;
        left: 10px;
        border-radius: 7px;
    }

    #player::after {
        content: "";
        position: absolute;
        width: 35px;
        height: 15px;
        background: yellow;
        bottom: 10px;
        left: 10px;
        border-radius: 4px;
    }

    .obstacle {
        position: absolute;
        width: 50px;
        height: 65px;
        background: #222;
        border-radius: 10px;
        z-index: 5;
    }

    .obstacle::before {
        content: "";
        position: absolute;
        top: 12px;
        left: 8px;
        width: 34px;
        height: 12px;
        background: orange;
    }

    .coin {
        position: absolute;
        width: 28px;
        height: 28px;
        border-radius: 50%;
        background: gold;
        border: 4px solid #ffcc00;
        box-sizing: border-box;
        z-index: 4;
    }

    #hud {
        position: absolute;
        top: 10px;
        left: 10px;
        right: 10px;
        z-index: 20;
        color: white;
        font-size: 18px;
        font-weight: bold;
        display: flex;
        justify-content: space-between;
        text-shadow: 2px 2px 3px black;
    }

    #message {
        position: absolute;
        width: 100%;
        top: 45%;
        text-align: center;
        color: white;
        font-size: 35px;
        font-weight: bold;
        z-index: 30;
        text-shadow: 3px 3px 5px black;
        display: none;
    }

    #start {
        position: absolute;
        z-index: 40;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        padding: 15px 35px;
        font-size: 22px;
        font-weight: bold;
        border: none;
        border-radius: 12px;
        cursor: pointer;
        background: #00c853;
        color: white;
    }

    #controls {
        position: absolute;
        bottom: 10px;
        left: 10px;
        right: 10px;
        z-index: 50;
        display: flex;
        justify-content: space-between;
        pointer-events: none;
    }

    .controlGroup {
        display: flex;
        gap: 10px;
    }

    .control {
        width: 65px;
        height: 65px;
        border-radius: 50%;
        border: 2px solid white;
        background: rgba(0,0,0,0.5);
        color: white;
        font-size: 30px;
        pointer-events: auto;
        user-select: none;
    }

    @media (max-width: 600px) {
        #game {
            height: 600px;
        }

        .control {
            width: 60px;
            height: 60px;
        }
    }
</style>
</head>

<body>

<div id="game">

    <div id="leftSide" class="side"></div>
    <div id="rightSide" class="side"></div>

    <div id="road">

        <div id="player"></div>

    </div>

    <div id="hud">
        <div>🏁 거리: <span id="distance">0</span>m</div>
        <div>🪙 <span id="coins">0</span></div>
        <div>❤️ <span id="hp">3</span></div>
    </div>

    <div id="message"></div>

    <button id="start">게임 시작</button>

    <div id="controls">

        <div class="controlGroup">
            <button class="control" id="left">◀</button>
            <button class="control" id="right">▶</button>
        </div>

        <div class="controlGroup">
            <button class="control" id="boost">💨</button>
        </div>

    </div>

</div>

<script>

const game = document.getElementById("game");
const road = document.getElementById("road");
const player = document.getElementById("player");

const distanceText = document.getElementById("distance");
const coinsText = document.getElementById("coins");
const hpText = document.getElementById("hp");

const startButton = document.getElementById("start");
const message = document.getElementById("message");

let running = false;

let playerX = 0;

let speed = 6;
let normalSpeed = 6;
let boostSpeed = 12;

let distance = 0;
let coins = 0;
let hp = 3;

let keys = {
    left: false,
    right: false,
    boost: false
};

let obstacles = [];
let coinObjects = [];

let spawnTimer = 0;
let coinTimer = 0;

const lanes = [20, 40, 60, 80];

function startGame() {

    running = true;

    distance = 0;
    coins = 0;
    hp = 3;

    speed = normalSpeed;

    playerX = 50;

    distanceText.innerText = 0;
    coinsText.innerText = 0;
    hpText.innerText = 3;

    message.style.display = "none";
    startButton.style.display = "none";

    obstacles.forEach(o => o.remove());
    coinObjects.forEach(c => c.remove());

    obstacles = [];
    coinObjects = [];

    requestAnimationFrame(gameLoop);
}

function endGame() {

    running = false;

    message.innerHTML =
        "GAME OVER<br><span style='font-size:20px'>거리: "
        + Math.floor(distance)
        + "m<br>코인: "
        + coins
        + "</span>";

    message.style.display = "block";

    startButton.innerText = "다시 시작";
    startButton.style.display = "block";
}

function createObstacle() {

    const obstacle = document.createElement("div");

    obstacle.className = "obstacle";

    const lane =
        lanes[Math.floor(Math.random() * lanes.length)];

    obstacle.style.left = lane + "%";
    obstacle.style.top = "-80px";

    road.appendChild(obstacle);

    obstacles.push(obstacle);
}

function createCoin() {

    const coin = document.createElement("div");

    coin.className = "coin";

    const lane =
        lanes[Math.floor(Math.random() * lanes.length)];

    coin.style.left = lane + "%";
    coin.style.top = "-40px";

    road.appendChild(coin);

    coinObjects.push(coin);
}

function collision(a, b) {

    const r1 = a.getBoundingClientRect();
    const r2 = b.getBoundingClientRect();

    return !(
        r1.right < r2.left ||
        r1.left > r2.right ||
        r1.bottom < r2.top ||
        r1.top > r2.bottom
    );
}

function updatePlayer() {

    if (keys.left) {
        playerX -= 0.8;
    }

    if (keys.right) {
        playerX += 0.8;
    }

    playerX = Math.max(18, Math.min(82, playerX));

    player.style.left =
        "calc(" + playerX + "% - 27px)";
}

function updateObjects() {

    for (let i = obstacles.length - 1; i >= 0; i--) {

        const obstacle = obstacles[i];

        let top =
            parseFloat(obstacle.style.top);

        top += speed;

        obstacle.style.top = top + "px";

        if (collision(player, obstacle)) {

            obstacle.remove();
            obstacles.splice(i, 1);

            hp--;

            hpText.innerText = hp;

            if (hp <= 0) {
                endGame();
                return;
            }

            continue;
        }

        if (top > 700) {

            obstacle.remove();
            obstacles.splice(i, 1);
        }
    }

    for (let i = coinObjects.length - 1; i >= 0; i--) {

        const coin = coinObjects[i];

        let top =
            parseFloat(coin.style.top);

        top += speed;

        coin.style.top = top + "px";

        if (collision(player, coin)) {

            coin.remove();
            coinObjects.splice(i, 1);

            coins++;

            coinsText.innerText = coins;

            continue;
        }

        if (top > 700) {

            coin.remove();
            coinObjects.splice(i, 1);
        }
    }
}

function gameLoop() {

    if (!running) return;

    if (keys.boost) {
        speed = boostSpeed;
    } else {
        speed = normalSpeed;
    }

    updatePlayer();
    updateObjects();

    distance += speed * 0.03;

    distanceText.innerText =
        Math.floor(distance);

    spawnTimer++;

    coinTimer++;

    if (spawnTimer > Math.max(25, 70 - distance / 100)) {

        createObstacle();

        spawnTimer = 0;
    }

    if (coinTimer > 35) {

        createCoin();

        coinTimer = 0;
    }

    requestAnimationFrame(gameLoop);
}


// 키보드 조작

document.addEventListener("keydown", function(e) {

    if (e.key === "ArrowLeft") {
        keys.left = true;
    }

    if (e.key === "ArrowRight") {
        keys.right = true;
    }

    if (e.code === "Space") {
        keys.boost = true;
    }

});

document.addEventListener("keyup", function(e) {

    if (e.key === "ArrowLeft") {
        keys.left = false;
    }

    if (e.key === "ArrowRight") {
        keys.right = false;
    }

    if (e.code === "Space") {
        keys.boost = false;
    }

});


// 터치 버튼

function holdButton(button, key) {

    button.addEventListener("mousedown", () => {
        keys[key] = true;
    });

    button.addEventListener("mouseup", () => {
        keys[key] = false;
    });

    button.addEventListener("mouseleave", () => {
        keys[key] = false;
    });

    button.addEventListener("touchstart", (e) => {
        e.preventDefault();
        keys[key] = true;
    });

    button.addEventListener("touchend", (e) => {
        e.preventDefault();
        keys[key] = false;
    });
}

holdButton(
    document.getElementById("left"),
    "left"
);

holdButton(
    document.getElementById("right"),
    "right"
);

holdButton(
    document.getElementById("boost"),
    "boost"
);

startButton.addEventListener(
    "click",
    startGame
);

</script>

</body>
</html>
"""

components.html(
    game_html,
    height=680,
    scrolling=False
)
