import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(
    page_title="🧱 벽돌 깨기",
    page_icon="🧱",
    layout="centered"
)

html = r"""
<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8">

<style>
* {
    box-sizing: border-box;
}

body {
    margin: 0;
    background: #111;
    color: white;
    font-family: Arial, sans-serif;
}

.game-container {
    width: 100%;
    max-width: 800px;
    margin: auto;
    text-align: center;
}

h1 {
    margin: 10px 0;
}

.info {
    display: flex;
    justify-content: center;
    gap: 20px;
    flex-wrap: wrap;
    font-size: 18px;
    margin: 10px 0;
}

canvas {
    display: block;
    width: 100%;
    max-width: 800px;
    height: auto;
    background: #050505;
    border: 3px solid white;
    border-radius: 8px;
    touch-action: none;
}

.controls {
    margin-top: 12px;
}

button {
    border: none;
    border-radius: 8px;
    padding: 9px 15px;
    margin: 3px;
    font-size: 15px;
    cursor: pointer;
    color: white;
}

.speed-slow {
    background: #388e3c;
}

.speed-normal {
    background: #1976d2;
}

.speed-fast {
    background: #d32f2f;
}

.start {
    background: #9c27b0;
}

.message {
    min-height: 30px;
    margin: 8px;
    font-size: 18px;
    font-weight: bold;
}

.mobile-controls {
    display: flex;
    justify-content: center;
    gap: 20px;
    margin-top: 8px;
}

.move-button {
    width: 130px;
    height: 50px;
    font-size: 25px;
    background: #333;
    user-select: none;
    -webkit-user-select: none;
    touch-action: none;
}
</style>
</head>

<body>

<div class="game-container">

<h1>🧱 벽돌 깨기</h1>

<div class="info">
    <span>단계: <b id="level">1</b>/30</span>
    <span>점수: <b id="score">0</b></span>
    <span>목숨: <b id="lives">3</b></span>
    <span>공: <b id="ballCount">1</b></span>
    <span>속도: <b id="speedText">보통</b></span>
</div>

<canvas id="game" width="800" height="600"></canvas>

<div class="message" id="message">
    시작 버튼을 눌러주세요!
</div>

<div class="controls">
    <button class="start" onclick="startGame()">게임 시작 / 재시작</button>
    <button class="speed-slow" onclick="changeSpeed(3)">느림</button>
    <button class="speed-normal" onclick="changeSpeed(5)">보통</button>
    <button class="speed-fast" onclick="changeSpeed(7)">빠름</button>
</div>

<div class="mobile-controls">
    <button class="move-button" id="leftButton">◀</button>
    <button class="move-button" id="rightButton">▶</button>
</div>

</div>

<script>

const canvas = document.getElementById("game");
const ctx = canvas.getContext("2d");

const WIDTH = 800;
const HEIGHT = 600;


// ============================
// 게임 변수
// ============================

let level = 1;
let score = 0;
let lives = 3;

let running = false;
let gameOver = false;

let baseSpeed = 5;

let leftPressed = false;
let rightPressed = false;

let balls = [];
let bricks = [];
let items = [];


// ============================
// 패들
// ============================

const paddle = {
    x: 340,
    y: 565,
    width: 120,
    height: 14,
    speed: 9
};


// ============================
// 공 생성
// ============================

function createBall(x, y, speed = baseSpeed) {

    let angle =
        (Math.random() * 1.2 - 0.6);

    let dx = Math.sin(angle) * speed;

    if (Math.abs(dx) < 1) {
        dx = Math.random() < 0.5 ? 1 : -1;
    }

    return {
        x: x,
        y: y,
        radius: 8,
        dx: dx,
        dy: -Math.sqrt(
            Math.max(
                1,
                speed * speed - dx * dx
            )
        )
    };
}


// ============================
// 벽돌 생성
// ============================

function createLevel() {

    bricks = [];

    let rows = Math.min(
        4 + Math.floor((level - 1) / 4),
        9
    );

    let cols = Math.min(
        7 + Math.floor((level - 1) / 5),
        11
    );

    const brickWidth = 62;
    const brickHeight = 22;
    const gap = 8;

    const totalWidth =
        cols * brickWidth +
        (cols - 1) * gap;

    const startX =
        (WIDTH - totalWidth) / 2;

    for (let r = 0; r < rows; r++) {

        for (let c = 0; c < cols; c++) {

            let exists = true;

            // 짝수 단계
            if (
                level % 2 === 0 &&
                (r + c) % 4 === 0
            ) {
                exists = false;
            }

            // 5의 배수 단계
            if (
                level % 5 === 0 &&
                c === Math.floor(cols / 2) &&
                r > 0
            ) {
                exists = false;
            }

            // 10의 배수 단계
            if (
                level % 10 === 0 &&
                r === Math.floor(rows / 2) &&
                c % 2 === 0
            ) {
                exists = false;
            }

            if (exists) {

                let hp = 1;

                // 높은 단계에서는 일부 벽돌 2번 필요
                if (
                    level >= 15 &&
                    (r + c) % 5 === 0
                ) {
                    hp = 2;
                }

                bricks.push({
                    x: startX + c * (brickWidth + gap),
                    y: 55 + r * (brickHeight + gap),
                    width: brickWidth,
                    height: brickHeight,
                    hp: hp,
                    maxHp: hp
                });
            }
        }
    }
}


// ============================
// 게임 초기화
// ============================

function resetBalls() {

    balls = [
        createBall(
            WIDTH / 2,
            paddle.y - 20,
            baseSpeed
        )
    ];

    items = [];

    paddle.x =
        WIDTH / 2 -
        paddle.width / 2;

    updateInfo();
}


// ============================
// 게임 시작
// ============================

function startGame() {

    level = 1;
    score = 0;
    lives = 3;

    gameOver = false;
    running = true;

    createLevel();
    resetBalls();

    setMessage(
        "게임 시작! 30단계를 도전하세요!"
    );

    updateInfo();
}


// ============================
// 속도 변경
// ============================

function changeSpeed(speed) {

    baseSpeed = speed;

    let text = "보통";

    if (speed === 3) {
        text = "느림";
    }

    if (speed === 7) {
        text = "빠름";
    }

    document.getElementById(
        "speedText"
    ).textContent = text;

    // 현재 공의 속도도 변경
    balls.forEach(ball => {

        let current =
            Math.sqrt(
                ball.dx * ball.dx +
                ball.dy * ball.dy
            );

        if (current === 0) return;

        ball.dx =
            ball.dx / current * speed;

        ball.dy =
            ball.dy / current * speed;
    });
}


// ============================
// 정보 표시
// ============================

function updateInfo() {

    document.getElementById(
        "level"
    ).textContent = level;

    document.getElementById(
        "score"
    ).textContent = score;

    document.getElementById(
        "lives"
    ).textContent = lives;

    document.getElementById(
        "ballCount"
    ).textContent = balls.length;
}


function setMessage(text) {

    document.getElementById(
        "message"
    ).textContent = text;
}


// ============================
// 키보드
// ============================

window.addEventListener(
    "keydown",
    function(e) {

        if (e.key === "ArrowLeft") {
            e.preventDefault();
            leftPressed = true;
        }

        if (e.key === "ArrowRight") {
            e.preventDefault();
            rightPressed = true;
        }
    }
);


window.addEventListener(
    "keyup",
    function(e) {

        if (e.key === "ArrowLeft") {
            leftPressed = false;
        }

        if (e.key === "ArrowRight") {
            rightPressed = false;
        }
    }
);


// ============================
// 마우스
// ============================

canvas.addEventListener(
    "mousemove",
    function(e) {

        const rect =
            canvas.getBoundingClientRect();

        const mouseX =
            (e.clientX - rect.left) *
            WIDTH /
            rect.width;

        paddle.x =
            mouseX -
            paddle.width / 2;

        limitPaddle();
    }
);


// ============================
// 터치
// ============================

canvas.addEventListener(
    "touchmove",
    function(e) {

        e.preventDefault();

        const rect =
            canvas.getBoundingClientRect();

        const touchX =
            (e.touches[0].clientX - rect.left) *
            WIDTH /
            rect.width;

        paddle.x =
            touchX -
            paddle.width / 2;

        limitPaddle();

    },
    { passive: false }
);


// ============================
// 모바일 버튼
// ============================

function pressLeft(e) {

    e.preventDefault();
    leftPressed = true;
}

function releaseLeft(e) {

    e.preventDefault();
    leftPressed = false;
}

function pressRight(e) {

    e.preventDefault();
    rightPressed = true;
}

function releaseRight(e) {

    e.preventDefault();
    rightPressed = false;
}


const leftButton =
    document.getElementById(
        "leftButton"
    );

const rightButton =
    document.getElementById(
        "rightButton"
    );


leftButton.addEventListener(
    "pointerdown",
    pressLeft
);

leftButton.addEventListener(
    "pointerup",
    releaseLeft
);

leftButton.addEventListener(
    "pointercancel",
    releaseLeft
);

leftButton.addEventListener(
    "pointerleave",
    releaseLeft
);


rightButton.addEventListener(
    "pointerdown",
    pressRight
);

rightButton.addEventListener(
    "pointerup",
    releaseRight
);

rightButton.addEventListener(
    "pointercancel",
    releaseRight
);

rightButton.addEventListener(
    "pointerleave",
    releaseRight
);


// ============================
// 패들 제한
// ============================

function limitPaddle() {

    if (paddle.x < 0) {
        paddle.x = 0;
    }

    if (
        paddle.x +
        paddle.width >
        WIDTH
    ) {

        paddle.x =
            WIDTH -
            paddle.width;
    }
}


// ============================
// 벽돌 그리기
// ============================

function drawBricks() {

    bricks.forEach(
        function(brick, index) {

            let colors = [
                "#f44336",
                "#ff9800",
                "#ffeb3b",
                "#4caf50",
                "#2196f3",
                "#673ab7",
                "#e91e63",
                "#00bcd4",
                "#795548"
            ];

            ctx.fillStyle =
                colors[index % colors.length];

            ctx.fillRect(
                brick.x,
                brick.y,
                brick.width,
                brick.height
            );

            // HP 2 벽돌 표시
            if (brick.maxHp > 1) {

                ctx.fillStyle = "white";

                ctx.font =
                    "bold 13px Arial";

                ctx.textAlign = "center";

                ctx.fillText(
                    brick.hp,
                    brick.x +
                    brick.width / 2,
                    brick.y + 16
                );
            }
        }
    );
}


// ============================
// 공 그리기
// ============================

function drawBalls() {

    balls.forEach(
        function(ball) {

            ctx.beginPath();

            ctx.arc(
                ball.x,
                ball.y,
                ball.radius,
                0,
                Math.PI * 2
            );

            ctx.fillStyle = "white";

            ctx.fill();

            ctx.closePath();
        }
    );
}


// ============================
// 패들 그리기
// ============================

function drawPaddle() {

    ctx.fillStyle = "#2196f3";

    ctx.fillRect(
        paddle.x,
        paddle.y,
        paddle.width,
        paddle.height
    );
}


// ============================
// 아이템 그리기
// ============================

function drawItems() {

    items.forEach(
        function(item) {

            ctx.beginPath();

            ctx.arc(
                item.x,
                item.y,
                11,
                0,
                Math.PI * 2
            );

            ctx.fillStyle = "#00ff88";

            ctx.fill();

            ctx.closePath();

            ctx.fillStyle = "#111";

            ctx.font =
                "bold 15px Arial";

            ctx.textAlign = "center";

            ctx.fillText(
                "+",
                item.x,
                item.y + 5
            );
        }
    );
}


// ============================
// 공-벽돌 충돌
// ============================

function brickCollision(ball) {

    for (
        let i = bricks.length - 1;
        i >= 0;
        i--
    ) {

        const brick = bricks[i];

        if (
            ball.x + ball.radius >
                brick.x &&
            ball.x - ball.radius <
                brick.x + brick.width &&
            ball.y + ball.radius >
                brick.y &&
            ball.y - ball.radius <
                brick.y + brick.height
        ) {

            ball.dy *= -1;

            brick.hp--;

            if (brick.hp <= 0) {

                // 벽돌 제거
                bricks.splice(i, 1);

                score += 10;

                // ======================
                // 아이템 생성
                // ======================

                items.push({
                    x:
                        brick.x +
                        brick.width / 2,

                    y:
                        brick.y +
                        brick.height / 2,

                    speed: 2.5
                });

            } else {

                score += 5;
            }

            updateInfo();

            return;
        }
    }
}


// ============================
// 공 업데이트
// ============================

function updateBall(ball) {

    ball.x += ball.dx;
    ball.y += ball.dy;


    // 좌우 벽
    if (
        ball.x - ball.radius <= 0
    ) {

        ball.x =
            ball.radius;

        ball.dx =
            Math.abs(ball.dx);
    }


    if (
        ball.x + ball.radius >= WIDTH
    ) {

        ball.x =
            WIDTH -
            ball.radius;

        ball.dx =
            -Math.abs(ball.dx);
    }


    // 천장
    if (
        ball.y - ball.radius <= 0
    ) {

        ball.y =
            ball.radius;

        ball.dy =
            Math.abs(ball.dy);
    }


    // 패들
    if (
        ball.dy > 0 &&
        ball.y + ball.radius >= paddle.y &&
        ball.y - ball.radius <=
            paddle.y + paddle.height &&
        ball.x >= paddle.x &&
        ball.x <=
            paddle.x + paddle.width
    ) {

        let relative =
            (
                ball.x -
                (
                    paddle.x +
                    paddle.width / 2
                )
            ) /
            (paddle.width / 2);

        ball.dx =
            relative * baseSpeed;

        let vertical =
            Math.sqrt(
                Math.max(
                    1,
                    baseSpeed *
                    baseSpeed -
                    ball.dx *
                    ball.dx
                )
            );

        ball.dy = -vertical;

        ball.y =
            paddle.y -
            ball.radius -
            1;
    }


    brickCollision(ball);
}


// ============================
// 아이템 업데이트
// ============================

function updateItems() {

    for (
        let i = items.length - 1;
        i >= 0;
        i--
    ) {

        let item = items[i];

        item.y += item.speed;


        // 패들에 먹힘
        if (
            item.y + 10 >= paddle.y &&
            item.y - 10 <=
                paddle.y +
                paddle.height &&
            item.x >= paddle.x &&
            item.x <=
                paddle.x +
                paddle.width
        ) {

            // 공 하나 추가!
            balls.push(
                createBall(
                    item.x,
                    paddle.y - 20,
                    baseSpeed
                )
            );

            setMessage(
                "🟢 공이 하나 추가되었습니다!"
            );

            items.splice(i, 1);

            updateInfo();

            continue;
        }


        // 화면 밖
        if (item.y > HEIGHT + 20) {

            items.splice(i, 1);
        }
    }
}


// ============================
// 게임 업데이트
// ============================

function update() {

    if (!running) {
        return;
    }


    // 패들 이동
    if (leftPressed) {

        paddle.x -=
            paddle.speed;
    }

    if (rightPressed) {

        paddle.x +=
            paddle.speed;
    }

    limitPaddle();


    // 공 업데이트
    for (
        let i = balls.length - 1;
        i >= 0;
        i--
    ) {

        updateBall(
            balls[i]
        );

        // 바닥 아래
        if (
            balls[i].y >
            HEIGHT + 30
        ) {

            balls.splice(i, 1);
        }
    }


    // 아이템
    updateItems();


    // 공이 전부 사라짐
    if (
        balls.length === 0
    ) {

        lives--;

        updateInfo();

        if (lives <= 0) {

            running = false;
            gameOver = true;

            setMessage(
                "💀 게임 오버! 다시 시작하세요."
            );

        } else {

            setMessage(
                "공을 놓쳤습니다! 남은 목숨: " +
                lives
            );

            resetBalls();
        }
    }


    // 단계 클리어
    if (
        bricks.length === 0
    ) {

        if (level >= 30) {

            running = false;

            setMessage(
                "🏆 축하합니다! 30단계까지 모두 클리어했습니다!"
            );

            return;
        }


        level++;

        createLevel();

        resetBalls();

        setMessage(
            "🎉 " +
            level +
            "단계 시작!"
        );

        updateInfo();
    }
}


// ============================
// 화면 그리기
// ============================

function draw() {

    ctx.clearRect(
        0,
        0,
        WIDTH,
        HEIGHT
    );


    drawBricks();

    drawItems();

    drawPaddle();

    drawBalls();


    update();

    requestAnimationFrame(draw);
}


// ============================
// 초기 화면
// ============================

createLevel();

resetBalls();

running = false;

draw();

</script>

</body>
</html>
"""

components.html(
    html,
    height=850,
    scrolling=False
)
