import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(
    page_title="3D Highway Kart",
    page_icon="🏎️",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown("""
<style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .block-container {
        padding: 0 !important;
        max-width: 100% !important;
    }
    iframe {
        width: 100% !important;
        border: none !important;
    }
</style>
""", unsafe_allow_html=True)

GAME = r"""
<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">

<meta name="viewport"
      content="width=device-width,
      initial-scale=1,
      maximum-scale=1,
      user-scalable=no,
      viewport-fit=cover">

<style>

* {
    box-sizing: border-box;
}

html, body {
    margin: 0;
    padding: 0;
    width: 100%;
    height: 100%;
    overflow: hidden;
    background: #8fd3ff;
    touch-action: none;
    user-select: none;
    -webkit-user-select: none;
    -webkit-touch-callout: none;
}

canvas {
    display: block;
    width: 100%;
    height: 100%;
    touch-action: none;
}

#hud {
    position: fixed;
    top: 12px;
    left: 12px;
    z-index: 10;

    color: white;
    font-family: Arial, sans-serif;
    font-weight: bold;

    text-shadow:
        0 2px 4px black,
        0 0 8px black;

    pointer-events: none;
}

#title {
    font-size: 20px;
}

#status {
    margin-top: 6px;
    font-size: 15px;
}

#countdown {
    position: fixed;
    z-index: 20;

    left: 50%;
    top: 45%;

    transform: translate(-50%, -50%);

    color: white;
    font-family: Arial, sans-serif;
    font-size: 75px;
    font-weight: bold;

    text-shadow:
        0 4px 10px black,
        0 0 20px black;

    pointer-events: none;
}

#finish {
    display: none;

    position: fixed;
    inset: 0;

    z-index: 50;

    background: rgba(0,0,0,0.65);

    color: white;

    font-family: Arial, sans-serif;

    align-items: center;
    justify-content: center;

    flex-direction: column;
}

#finish h1 {
    font-size: 58px;
    margin: 0 0 15px;
}

#finish button {
    padding: 14px 28px;

    border: none;
    border-radius: 15px;

    background: white;
    color: black;

    font-size: 20px;
    font-weight: bold;
}

/* 모바일 조작 */

#mobile {
    position: fixed;

    left: 0;
    right: 0;

    bottom: max(10px, env(safe-area-inset-bottom));

    z-index: 30;

    display: none;

    justify-content: space-between;

    padding: 0 12px;

    pointer-events: none;
}

.group {
    display: flex;
    gap: 8px;

    pointer-events: auto;
}

.btn {
    width: 62px;
    height: 62px;

    border-radius: 18px;

    border: 2px solid rgba(255,255,255,.75);

    background: rgba(15,20,30,.62);

    color: white;

    display: flex;

    align-items: center;
    justify-content: center;

    font-family: Arial, sans-serif;
    font-size: 17px;
    font-weight: bold;

    touch-action: none;

    -webkit-tap-highlight-color: transparent;

    box-shadow:
        0 4px 12px rgba(0,0,0,.35);
}

.btn.gas {
    font-size: 30px;
}

.btn.active,
.btn:active {
    background: rgba(255,255,255,.35);
    transform: scale(.93);
}

@media(max-width: 700px) {

    #mobile {
        display: flex;
    }

    #title {
        font-size: 17px;
    }

    #status {
        font-size: 13px;
    }

    .btn {
        width: 58px;
        height: 58px;
    }
}

</style>
</head>

<body>

<div id="hud">

    <div id="title">
        🏎️ 3D HIGHWAY KART
    </div>

    <div id="status">
        LAP 1/2 · SPEED 0 · BOOST 100
    </div>

</div>

<div id="countdown">
    3
</div>

<div id="finish">

    <h1>
        FINISH!
    </h1>

    <div id="finalTime"
         style="font-size:22px;margin-bottom:20px">
    </div>

    <button onclick="location.reload()">
        다시 하기
    </button>

</div>


<!-- 모바일 버튼 -->

<div id="mobile">

    <div class="group">

        <div class="btn"
             id="left">
            ◀
        </div>

        <div class="btn"
             id="right">
            ▶
        </div>

    </div>


    <div class="group">

        <div class="btn"
             id="drift">
            DRIFT
        </div>

        <div class="btn"
             id="boost">
            BOOST
        </div>

        <div class="btn gas"
             id="gas">
            ▲
        </div>

    </div>

</div>


<script src="https://cdn.jsdelivr.net/npm/three@0.160.0/build/three.min.js"></script>


<script>

"use strict";


/* =====================================================
   THREE.JS
===================================================== */

const scene =
    new THREE.Scene();

scene.background =
    new THREE.Color(0x9bdcff);

scene.fog =
    new THREE.Fog(
        0x9bdcff,
        180,
        900
    );


const camera =
    new THREE.PerspectiveCamera(
        65,
        innerWidth / innerHeight,
        0.1,
        1500
    );


const renderer =
    new THREE.WebGLRenderer({
        antialias: true,
        powerPreference: "high-performance"
    });

renderer.setPixelRatio(
    Math.min(devicePixelRatio || 1, 1.8)
);

renderer.setSize(
    innerWidth,
    innerHeight
);

renderer.outputColorSpace =
    THREE.SRGBColorSpace;

document.body.appendChild(
    renderer.domElement
);


/* =====================================================
   LIGHT
===================================================== */

scene.add(
    new THREE.HemisphereLight(
        0xffffff,
        0x52704d,
        2
    )
);

const sunlight =
    new THREE.DirectionalLight(
        0xffffff,
        2.2
    );

sunlight.position.set(
    150,
    250,
    100
);

scene.add(sunlight);


/* =====================================================
   지면
===================================================== */

const ground =
    new THREE.Mesh(
        new THREE.PlaneGeometry(
            2000,
            2000
        ),
        new THREE.MeshLambertMaterial({
            color: 0x609553
        })
    );

ground.rotation.x =
    -Math.PI / 2;

ground.position.y =
    -0.1;

scene.add(ground);


/* =====================================================
   고가도로 느낌의 오리지널 트랙
===================================================== */

const points = [

    new THREE.Vector3(0, 0, 0),

    new THREE.Vector3(0, 0, -140),

    new THREE.Vector3(55, 0, -225),

    new THREE.Vector3(175, 0, -225),

    new THREE.Vector3(285, 0, -150),

    new THREE.Vector3(285, 0, 0),

    new THREE.Vector3(225, 0, 90),

    new THREE.Vector3(100, 0, 130),

    new THREE.Vector3(-40, 0, 130),

    new THREE.Vector3(-155, 0, 75),

    new THREE.Vector3(-215, 0, -20),

    new THREE.Vector3(-200, 0, -115),

    new THREE.Vector3(-130, 0, -185),

    new THREE.Vector3(-45, 0, -210)

];


const track =
    new THREE.CatmullRomCurve3(
        points,
        true,
        "catmullrom",
        0.38
    );


const TRACK_WIDTH = 13;
const SAMPLES = 600;


/* =====================================================
   도로
===================================================== */

const roadPositions = [];
const roadIndices = [];

for (
    let i = 0;
    i < SAMPLES;
    i++
) {

    const t =
        i / SAMPLES;

    const p =
        track.getPointAt(t);

    const tangent =
        track
        .getTangentAt(t)
        .normalize();

    const side =
        new THREE.Vector3(
            -tangent.z,
            0,
            tangent.x
        ).normalize();


    const left =
        p.clone()
        .addScaledVector(
            side,
            TRACK_WIDTH
        );


    const right =
        p.clone()
        .addScaledVector(
            side,
            -TRACK_WIDTH
        );


    roadPositions.push(
        left.x,
        0,
        left.z,

        right.x,
        0,
        right.z
    );


    const next =
        (i + 1) % SAMPLES;


    roadIndices.push(
        i * 2,
        i * 2 + 1,
        next * 2,

        i * 2 + 1,
        next * 2 + 1,
        next * 2
    );
}


const roadGeometry =
    new THREE.BufferGeometry();

roadGeometry.setAttribute(
    "position",
    new THREE.Float32BufferAttribute(
        roadPositions,
        3
    )
);

roadGeometry.setIndex(
    roadIndices
);

roadGeometry.computeVertexNormals();


const road =
    new THREE.Mesh(
        roadGeometry,
        new THREE.MeshLambertMaterial({
            color: 0x303238,
            side: THREE.DoubleSide
        })
    );

scene.add(road);


/* =====================================================
   중앙 차선
===================================================== */

const lanePositions = [];

for (
    let i = 0;
    i < 260;
    i++
) {

    const t =
        i / 260;

    const p =
        track.getPointAt(t);

    const tangent =
        track.getTangentAt(t)
        .normalize();


    const a =
        p.clone()
        .addScaledVector(
            tangent,
            2
        );

    const b =
        p.clone()
        .addScaledVector(
            tangent,
            5
        );

    a.y = 0.08;
    b.y = 0.08;


    lanePositions.push(
        a.x,a.y,a.z,
        b.x,b.y,b.z
    );
}


const laneGeometry =
    new THREE.BufferGeometry();

laneGeometry.setAttribute(
    "position",
    new THREE.Float32BufferAttribute(
        lanePositions,
        3
    )
);


scene.add(
    new THREE.LineSegments(
        laneGeometry,
        new THREE.LineBasicMaterial({
            color: 0xffffff
        })
    )
);


/* =====================================================
   연석
===================================================== */

for (
    let i = 0;
    i < 180;
    i++
) {

    const t =
        i / 180;

    const p =
        track.getPointAt(t);

    const tangent =
        track.getTangentAt(t)
        .normalize();

    const side =
        new THREE.Vector3(
            -tangent.z,
            0,
            tangent.x
        ).normalize();


    for (
        const sign of [-1,1]
    ) {

        const curb =
            new THREE.Mesh(
                new THREE.BoxGeometry(
                    3,
                    .22,
                    .8
                ),
                new THREE.MeshLambertMaterial({
                    color:
                        i % 2 === 0
                        ? 0xffffff
                        : 0xe02d2d
                })
            );


        curb.position.copy(
            p
        );

        curb.position.addScaledVector(
            side,
            sign * (TRACK_WIDTH + .8)
        );

        curb.position.y =
            .15;

        curb.rotation.y =
            Math.atan2(
                tangent.x,
                tangent.z
            );

        scene.add(curb);
    }
}


/* =====================================================
   가드레일
===================================================== */

for (
    let i = 0;
    i < 100;
    i++
) {

    const t =
        i / 100;

    const p =
        track.getPointAt(t);

    const tangent =
        track.getTangentAt(t)
        .normalize();

    const side =
        new THREE.Vector3(
            -tangent.z,
            0,
            tangent.x
        ).normalize();


    for (
        const sign of [-1,1]
    ) {

        const rail =
            new THREE.Mesh(
                new THREE.BoxGeometry(
                    5,
                    .35,
                    .15
                ),
                new THREE.MeshLambertMaterial({
                    color: 0x777b80
                })
            );


        rail.position.copy(
            p
        );

        rail.position.addScaledVector(
            side,
            sign * (TRACK_WIDTH + 2)
        );

        rail.position.y =
            .9;

        rail.rotation.y =
            Math.atan2(
                tangent.x,
                tangent.z
            );

        scene.add(rail);
    }
}


/* =====================================================
   나무
===================================================== */

function createTree(
    position,
    scale
) {

    const tree =
        new THREE.Group();


    const trunk =
        new THREE.Mesh(
            new THREE.CylinderGeometry(
                .2,
                .32,
                2.2,
                8
            ),
            new THREE.MeshLambertMaterial({
                color: 0x704a2a
            })
        );

    trunk.position.y =
        1.1;

    tree.add(trunk);


    const leaves =
        new THREE.Mesh(
            new THREE.ConeGeometry(
                1.7,
                4,
                8
            ),
            new THREE.MeshLambertMaterial({
                color: 0x2f803a
            })
        );

    leaves.position.y =
        3.5;

    tree.add(leaves);


    tree.position.copy(
        position
    );

    tree.scale.setScalar(
        scale
    );

    scene.add(tree);
}


for (
    let i = 0;
    i < 90;
    i++
) {

    const t =
        i / 90;

    const p =
        track.getPointAt(t);

    const tangent =
        track.getTangentAt(t)
        .normalize();

    const side =
        new THREE.Vector3(
            -tangent.z,
            0,
            tangent.x
        ).normalize();


    const sign =
        i % 2 === 0
        ? 1
        : -1;


    const position =
        p.clone()
        .addScaledVector(
            side,
            sign * (23 + (i % 4) * 3)
        );


    createTree(
        position,
        .7 + (i % 4) * .12
    );
}


/* =====================================================
   가로등
===================================================== */

for (
    let i = 0;
    i < 70;
    i++
) {

    const t =
        i / 70;

    const p =
        track.getPointAt(t);

    const tangent =
        track.getTangentAt(t)
        .normalize();

    const side =
        new THREE.Vector3(
            -tangent.z,
            0,
            tangent.x
        ).normalize();


    const sign =
        i % 2 === 0
        ? 1
        : -1;


    const pole =
        new THREE.Mesh(
            new THREE.CylinderGeometry(
                .12,
                .2,
                6,
                8
            ),
            new THREE.MeshLambertMaterial({
                color: 0x777777
            })
        );


    pole.position.copy(
        p
    );

    pole.position.addScaledVector(
        side,
        sign * 16
    );

    pole.position.y =
        3;

    scene.add(pole);


    const lamp =
        new THREE.Mesh(
            new THREE.BoxGeometry(
                .8,
                .25,
                .8
            ),
            new THREE.MeshBasicMaterial({
                color: 0xffffbb
            })
        );

    lamp.position.copy(
        pole.position
    );

    lamp.position.y =
        6;

    scene.add(lamp);
}


/* =====================================================
   고가도로 구조물
===================================================== */

function bridge(t) {

    const p =
        track.getPointAt(t);

    for (
        const x of [-5,5]
    ) {

        const pillar =
            new THREE.Mesh(
                new THREE.BoxGeometry(
                    1.3,
                    7,
                    1.3
                ),
                new THREE.MeshLambertMaterial({
                    color: 0x70757a
                })
            );

        pillar.position.set(
            p.x + x,
            3.5,
            p.z
        );

        scene.add(pillar);
    }


    const beam =
        new THREE.Mesh(
            new THREE.BoxGeometry(
                13,
                .9,
                1.5
            ),
            new THREE.MeshLambertMaterial({
                color: 0x85898e
            })
        );

    beam.position.set(
        p.x,
        7,
        p.z
    );

    scene.add(beam);
}


for (
    let i = 0;
    i < 10;
    i++
) {

    bridge(
        .1 + i * .055
    );
}


/* =====================================================
   카트 제작
===================================================== */

function makeKart(color) {

    const kart =
        new THREE.Group();


    const body =
        new THREE.Mesh(
            new THREE.BoxGeometry(
                2.3,
                .7,
                3.5
            ),
            new THREE.MeshLambertMaterial({
                color: color
            })
        );

    body.position.y =
        .7;

    kart.add(body);


    const front =
        new THREE.Mesh(
            new THREE.BoxGeometry(
                1.5,
                .45,
                1.3
            ),
            new THREE.MeshLambertMaterial({
                color: 0xe8e8e8
            })
        );

    front.position.set(
        0,
        .85,
        -1.25
    );

    kart.add(front);


    const seat =
        new THREE.Mesh(
            new THREE.BoxGeometry(
                1.2,
                .7,
                1.1
            ),
            new THREE.MeshLambertMaterial({
                color: 0x151515
            })
        );

    seat.position.set(
        0,
        1.1,
        .45
    );

    kart.add(seat);


    const spoiler =
        new THREE.Mesh(
            new THREE.BoxGeometry(
                2.3,
                .18,
                .45
            ),
            new THREE.MeshLambertMaterial({
                color: 0x222222
            })
        );

    spoiler.position.set(
        0,
        1.12,
        1.55
    );

    kart.add(spoiler);


    for (
        const x of [-1,1]
    ) {

        for (
            const z of [-1.15,1.15]
        ) {

            const wheel =
                new THREE.Mesh(
                    new THREE.CylinderGeometry(
                        .39,
                        .39,
                        .3,
                        12
                    ),
                    new THREE.MeshLambertMaterial({
                        color: 0x101010
                    })
                );

            wheel.rotation.z =
                Math.PI / 2;

            wheel.position.set(
                x * 1.18,
                .43,
                z
            );

            kart.add(wheel);
        }
    }


    return kart;
}


/* =====================================================
   플레이어
===================================================== */

const player =
    makeKart(
        0x2678ff
    );

scene.add(player);


/* =====================================================
   CPU
===================================================== */

const cpuColors = [
    0xff3333,
    0xffc400,
    0x45d35c,
    0x9955ff,
    0xff7a22
];

const cpu = [];


cpuColors.forEach(
    (color, index) => {

        const kart =
            makeKart(color);

        scene.add(kart);


        cpu.push({
            mesh: kart,
            t: .03 + index * .018,
            speed:
                .0098 +
                index * .00035,
            lane:
                (index % 3) - 1
        });
    }
);


/* =====================================================
   입력
===================================================== */

const keys = {

    up: false,
    down: false,

    left: false,
    right: false,

    drift: false,
    boost: false
};


addEventListener(
    "keydown",
    event => {

        if (
            event.code === "ArrowUp"
        )
            keys.up = true;

        if (
            event.code === "ArrowDown"
        )
            keys.down = true;

        if (
            event.code === "ArrowLeft"
        )
            keys.left = true;

        if (
            event.code === "ArrowRight"
        )
            keys.right = true;

        if (
            event.code === "ShiftLeft" ||
            event.code === "ShiftRight"
        )
            keys.drift = true;

        if (
            event.code === "Space"
        )
            keys.boost = true;
    }
);


addEventListener(
    "keyup",
    event => {

        if (
            event.code === "ArrowUp"
        )
            keys.up = false;

        if (
            event.code === "ArrowDown"
        )
            keys.down = false;

        if (
            event.code === "ArrowLeft"
        )
            keys.left = false;

        if (
            event.code === "ArrowRight"
        )
            keys.right = false;

        if (
            event.code === "ShiftLeft" ||
            event.code === "ShiftRight"
        )
            keys.drift = false;

        if (
            event.code === "Space"
        )
            keys.boost = false;
    }
);


/* =====================================================
   모바일 버튼
===================================================== */

function bindButton(
    id,
    key
) {

    const element =
        document.getElementById(id);

    if (!element)
        return;


    function down(event) {

        event.preventDefault();

        keys[key] = true;

        element.classList.add(
            "active"
        );

        try {
            element.setPointerCapture(
                event.pointerId
            );
        } catch (_) {}
    }


    function up(event) {

        event.preventDefault();

        keys[key] = false;

        element.classList.remove(
            "active"
        );
    }


    element.addEventListener(
        "pointerdown",
        down,
        {passive:false}
    );

    element.addEventListener(
        "pointerup",
        up,
        {passive:false}
    );

    element.addEventListener(
        "pointercancel",
        up,
        {passive:false}
    );
}


bindButton(
    "left",
    "left"
);

bindButton(
    "right",
    "right"
);

bindButton(
    "gas",
    "up"
);

bindButton(
    "drift",
    "drift"
);

bindButton(
    "boost",
    "boost"
);


document.addEventListener(
    "touchmove",
    event => {
        event.preventDefault();
    },
    {passive:false}
);


/* =====================================================
   레이스 변수
===================================================== */

let progress = 0;

let speed = 0;

let boostGauge = 100;

let driftPower = 0;

let drifting = false;

let lap = 1;

let started = false;

let finished = false;

let raceTime = 0;


/* =====================================================
   카운트다운
===================================================== */

const countdown =
    document.getElementById(
        "countdown"
    );

let count = 3;


const timer =
    setInterval(
        () => {

            count--;

            if (
                count > 0
            ) {

                countdown.textContent =
                    count;

            } else if (
                count === 0
            ) {

                countdown.textContent =
                    "GO!";

            } else {

                countdown.style.display =
                    "none";

                started = true;

                clearInterval(timer);
            }

        },
        1000
    );


/* =====================================================
   플레이어 업데이트
===================================================== */

function updatePlayer(dt) {

    if (
        !started ||
        finished
    )
        return;


    raceTime += dt;


    /* 가속 */

    if (keys.up) {

        speed +=
            30 * dt;

    } else {

        speed -=
            7 * dt;
    }


    /* 브레이크 */

    if (keys.down) {

        speed -=
            35 * dt;
    }


    speed =
        Math.max(
            0,
            speed
        );


    /* 드리프트 */

    const steering =
        (keys.left ? -1 : 0) +
        (keys.right ? 1 : 0);


    if (
        keys.drift &&
        steering !== 0 &&
        speed > 7
    ) {

        drifting = true;

        driftPower +=
            dt *
            (6 + speed * .18);

    } else {

        if (
            drifting &&
            driftPower > 2
        ) {

            boostGauge =
                Math.min(
                    100,
                    boostGauge +
                    driftPower * 5
                );
        }

        drifting = false;

        driftPower = 0;
    }


    /* 부스트 */

    if (
        keys.boost &&
        boostGauge > 0
    ) {

        speed +=
            18 * dt;

        boostGauge -=
            28 * dt;
    }


    const maxSpeed =
        (
            keys.boost &&
            boostGauge > 0
        )
        ? 50
        : 35;


    speed =
        Math.min(
            speed,
            maxSpeed
        );


    /* 트랙 이동 */

    progress +=
        speed *
        dt /
        track.getLength();


    if (
        progress >= 1
    ) {

        progress -= 1;
    }


    const position =
        track.getPointAt(
            progress
        );


    const tangent =
        track
        .getTangentAt(
            progress
        )
        .normalize();


    const side =
        new THREE.Vector3(
            -tangent.z,
            0,
            tangent.x
        ).normalize();


    /* 드리프트 횡이동 */

    if (
        drifting
    ) {

        position.addScaledVector(
            side,
            steering *
            4.8 *
            dt *
            speed /
            10
        );

    } else {

        position.addScaledVector(
            side,
            steering *
            2.0 *
            dt *
            speed /
            10
        );
    }


    player.position.copy(
        position
    );

    player.position.y =
        .1;


    let rotation =
        Math.atan2(
            tangent.x,
            tangent.z
        );


    if (
        drifting
    ) {

        rotation +=
            steering *
            .25;
    }


    player.rotation.y =
        rotation;


    /* 랩 계산 */

    if (
        progress > .5
    ) {

        lap = 2;
    }


    /*
       출발선을 두 번 통과하면 종료
    */

    if (
        raceTime > 5 &&
        progress < .02 &&
        lap >= 2
    ) {

        finished = true;

        document.getElementById(
            "finish"
        ).style.display =
            "flex";

        document.getElementById(
            "finalTime"
        ).textContent =
            "기록 : " +
            raceTime.toFixed(2) +
            "초";
    }
}


/* =====================================================
   CPU 업데이트
===================================================== */

function updateCPU(dt) {

    cpu.forEach(
        car => {

            car.t +=
                car.speed *
                dt;


            if (
                car.t >= 1
            )
                car.t -= 1;


            const p =
                track.getPointAt(
                    car.t
                );


            const tangent =
                track
                .getTangentAt(
                    car.t
                )
                .normalize();


            const side =
                new THREE.Vector3(
                    -tangent.z,
                    0,
                    tangent.x
                ).normalize();


            p.addScaledVector(
                side,
                car.lane * 3
            );


            car.mesh.position.copy(
                p
            );

            car.mesh.position.y =
                .1;


            car.mesh.rotation.y =
                Math.atan2(
                    tangent.x,
                    tangent.z
                );
        }
    );
}


/* =====================================================
   카메라
===================================================== */

function updateCamera() {

    const tangent =
        track
        .getTangentAt(
            progress
        )
        .normalize();


    const cameraPosition =
        player.position
        .clone()
        .addScaledVector(
            tangent,
            -11
        );


    cameraPosition.y +=
        5.5;


    camera.position.lerp(
        cameraPosition,
        .12
    );


    const lookPosition =
        player.position
        .clone()
        .addScaledVector(
            tangent,
            5
        );


    lookPosition.y +=
        1.2;


    camera.lookAt(
        lookPosition
    );
}


/* =====================================================
   게임 루프
===================================================== */

let last =
    performance.now();


function animate(now) {

    requestAnimationFrame(
        animate
    );


    const dt =
        Math.min(
            (now - last) / 1000,
            .04
        );


    last = now;


    updatePlayer(dt);

    updateCPU(dt);

    updateCamera();


    document.getElementById(
        "status"
    ).textContent =
        "LAP " +
        Math.min(lap,2) +
        "/2 · SPEED " +
        Math.round(speed) +
        " · BOOST " +
        Math.round(boostGauge) +
        (drifting
            ? " · DRIFT!"
            : "");


    renderer.render(
        scene,
        camera
    );
}


camera.position.set(
    0,
    8,
    15
);


requestAnimationFrame(
    animate
);


/* =====================================================
   화면 크기
===================================================== */

addEventListener(
    "resize",
    () => {

        camera.aspect =
            innerWidth /
            innerHeight;

        camera.updateProjectionMatrix();

        renderer.setSize(
            innerWidth,
            innerHeight
        );
    }
);

})();
</script>

</body>
</html>
"""


components.html(
    GAME,
    height=760,
    scrolling=False
)
