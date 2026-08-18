import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(
    page_title="벽돌 깨기",
    page_icon="🧱",
    layout="centered"
)

st.title("🧱 벽돌 깨기")

game = """
<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">

<style>
    body {
        margin: 0;
        padding: 0;
        background: #111;
        display: flex;
        justify-content: center;
        align-items: center;
        font-family: Arial, sans-serif;
    }

    #gameWrapper {
        width: 100%;
        max-width: 600px;
        text-align: center;
    }

    canvas {
        width: 100%;
        max-width: 600px;
        background: #050505;
        border: 3px solid white;
        border-radius: 8px;
        display: block;
        margin: auto;
    }

    #info {
        color: white;
        font-size: 20px;
        margin: 10px;
    }

    button {
        font-size: 18px;
        padding: 10px 25px;
        border: none;
        border-radius: 8px;
        cursor: pointer;
        background: #2196f3;
        color: white;
    }

    button:hover {
        background: #1976d2;
    }
</style>
</head>

<body>

<div id="gameWrapper">

    <canvas id="gameCanvas" width="600" height="500"></canvas>

    <div id="info">
        점수: <span id="score">0</span>
        &nbsp;&nbsp;
        목숨: <span id="lives">3</span>
    </div>

    <button onclick="restartGame()">게임 다시 시작</button>

</div>

<script>

const canvas = document.getElementById("gameCanvas");
const ctx = canvas.getContext("2d");

let score = 0;
let lives = 3;
let gameRunning = true;

const ball = {
    x: canvas.width / 2,
    y: canvas.height - 50,
    radius: 8,
    dx: 4,
    dy: -4
};

const paddle = {
    width: 100,
    height: 12,
    x: canvas.width / 2 - 50,
    speed: 8
};

const brick = {
    rowCount: 5,
    columnCount: 8,
    width: 65,
    height: 20,
    padding: 8,
    offsetTop: 50,
    offsetLeft: 15
};

let bricks = [];

function createBricks() {
    bricks = [];

    for (let r = 0; r < brick.rowCount; r++) {
        bricks[r] = [];

        for (let c = 0; c < brick.columnCount; c++) {
            bricks[r][c] = {
                x: 0,
                y: 0,
                alive: true
            };
        }
    }
}

createBricks();

let leftPressed = false;
let rightPressed = false;

document.addEventListener("keydown", keyDownHandler);
document.addEventListener("keyup", keyUpHandler);

function keyDownHandler(e) {

    if (e.key === "ArrowLeft") {
        leftPressed = true;
    }

    if (e.key === "ArrowRight") {
        rightPressed = true;
    }
}

function keyUpHandler(e) {

    if (e.key === "ArrowLeft") {
        leftPressed = false;
    }

    if (e.key === "ArrowRight") {
        rightPressed = false;
    }
}

// 마우스 조작
canvas.addEventListener("mousemove", function(e) {

    const rect = canvas.getBoundingClientRect();

    const mouseX =
        (e.clientX - rect.left) *
        (canvas.width / rect.width);

    paddle.x = mouseX - paddle.width / 2;

    if (paddle.x < 0)
        paddle.x = 0;

    if (paddle.x + paddle.width > canvas.width)
        paddle.x = canvas.width - paddle.width;
});

// 터치 조작
canvas.addEventListener("touchmove", function(e) {

    e.preventDefault();

    const rect = canvas.getBoundingClientRect();

    const touchX =
        (e.touches[0].clientX - rect.left) *
        (canvas.width / rect.width);

    paddle.x = touchX - paddle.width / 2;

    if (paddle.x < 0)
        paddle.x = 0;

    if (paddle.x + paddle.width > canvas.width)
        paddle.x = canvas.width - paddle.width;

}, { passive: false });


function drawBall() {

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


function drawPaddle() {

    ctx.fillStyle = "#2196f3";

    ctx.fillRect(
        paddle.x,
        canvas.height - paddle.height - 10,
        paddle.width,
        paddle.height
    );
}


function drawBricks() {

    for (let r = 0; r < brick.rowCount; r++) {

        for (let c = 0; c < brick.columnCount; c++) {

            if (!bricks[r][c].alive)
                continue;

            const brickX =
                c * (brick.width + brick.padding)
                + brick.offsetLeft;

            const brickY =
                r * (brick.height + brick.padding)
                + brick.offsetTop;

            bricks[r][c].x = brickX;
            bricks[r][c].y = brickY;

            const colors = [
                "#f44336",
                "#ff9800",
                "#ffeb3b",
                "#4caf50",
                "#2196f3"
            ];

            ctx.fillStyle = colors[r];

            ctx.fillRect(
                brickX,
                brickY,
                brick.width,
                brick.height
            );
        }
    }
}


function collisionDetection() {

    for (let r = 0; r < brick.rowCount; r++) {

        for (let c = 0; c < brick.columnCount; c++) {

            const b = bricks[r][c];

            if (!b.alive)
                continue;

            if (
                ball.x > b.x &&
                ball.x < b.x + brick.width &&
                ball.y > b.y &&
                ball.y < b.y + brick.height
            ) {

                ball.dy = -ball.dy;

                b.alive = false;

                score++;

                document.getElementById("score").textContent = score;

                if (score ===
                    brick.rowCount * brick.columnCount) {

                    gameRunning = false;

                    setTimeout(() => {
                        alert("🎉 모든 벽돌을 깼습니다!");
                    }, 100);
                }
            }
        }
    }
}


function update() {

    if (!gameRunning)
        return;

    // 벽 충돌
    if (
        ball.x + ball.dx > canvas.width - ball.radius ||
        ball.x + ball.dx < ball.radius
    ) {
        ball.dx = -ball.dx;
    }

    // 천장 충돌
    if (ball.y + ball.dy < ball.radius) {
        ball.dy = -ball.dy;
    }

    // 바닥 / 패들
    else if (
        ball.y + ball.dy >
        canvas.height - ball.radius - paddle.height - 10
    ) {

        if (
            ball.x > paddle.x &&
            ball.x < paddle.x + paddle.width
        ) {

            // 패들의 어느 위치에 맞았는지에 따라 방향 변경
            const hitPoint =
                ball.x -
                (paddle.x + paddle.width / 2);

            ball.dx = hitPoint * 0.12;

            ball.dy = -Math.abs(ball.dy);

        } else if (
            ball.y + ball.dy >
            canvas.height - ball.radius
        ) {

            lives--;

            document.getElementById("lives").textContent = lives;

            if (lives <= 0) {

                gameRunning = false;

                setTimeout(() => {
                    alert("💀 게임 오버!");
                }, 100);

            } else {

                resetBall();
            }
        }
    }

    // 패들 이동
    if (leftPressed) {
        paddle.x -= paddle.speed;
    }

    if (rightPressed) {
        paddle.x += paddle.speed;
    }

    if (paddle.x < 0)
        paddle.x = 0;

    if (paddle.x + paddle.width > canvas.width)
        paddle.x = canvas.width - paddle.width;

    ball.x += ball.dx;
    ball.y += ball.dy;

    collisionDetection();
}


function resetBall() {

    ball.x = canvas.width / 2;
    ball.y = canvas.height - 50;

    ball.dx = 4;
    ball.dy = -4;

    paddle.x = canvas.width / 2 - paddle.width / 2;
}


function draw() {

    ctx.clearRect(
        0,
        0,
        canvas.width,
        canvas.height
    );

    drawBricks();
    drawBall();
    drawPaddle();

    update();

    requestAnimationFrame(draw);
}


function restartGame() {

    score = 0;
    lives = 3;

    document.getElementById("score").textContent = score;
    document.getElementById("lives").textContent = lives;

    gameRunning = true;

    createBricks();
    resetBall();
}


draw();

</script>

</body>
</html>
"""

components.html(game, height=650, scrolling=False)
