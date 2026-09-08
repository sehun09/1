from pathlib import Path
import zipfile, re, shutil

src = Path("/mnt/data/kart_highway_3d.zip")
work = Path("/mnt/data/kart_highway_mobile")
if work.exists():
    shutil.rmtree(work)
work.mkdir()

with zipfile.ZipFile(src, "r") as z:
    z.extractall(work)

app = work / "app.py"
text = app.read_text(encoding="utf-8")

# Make the embedded game area responsive and mobile-friendly.
text = text.replace(
    'components.html(html, height=800, scrolling=False)',
    'components.html(html, height=760, scrolling=False)'
)

# Add stronger mobile CSS and touch behavior before the existing </style>.
mobile_css = r"""
        html, body {
            width: 100%;
            height: 100%;
            margin: 0;
            overflow: hidden !important;
            overscroll-behavior: none;
            touch-action: none;
            -webkit-user-select: none;
            user-select: none;
            -webkit-touch-callout: none;
        }
        canvas {
            display: block;
            width: 100% !important;
            height: 100% !important;
            touch-action: none;
        }
        #mobileControls {
            position: fixed;
            left: 0;
            right: 0;
            bottom: max(12px, env(safe-area-inset-bottom));
            z-index: 20;
            display: flex;
            justify-content: space-between;
            align-items: flex-end;
            padding: 0 14px;
            box-sizing: border-box;
            pointer-events: none;
        }
        .mobileCluster {
            display: flex;
            gap: 10px;
            pointer-events: auto;
        }
        .mBtn {
            width: 68px;
            height: 68px;
            border-radius: 20px;
            border: 2px solid rgba(255,255,255,.65);
            background: rgba(20,20,30,.58);
            color: white;
            font-size: 27px;
            font-weight: 800;
            display: flex;
            align-items: center;
            justify-content: center;
            box-shadow: 0 4px 16px rgba(0,0,0,.28);
            -webkit-tap-highlight-color: transparent;
            touch-action: none;
        }
        .mBtn.small {
            width: 62px;
            height: 62px;
            font-size: 20px;
        }
        .mBtn.active, .mBtn:active {
            transform: scale(.94);
            background: rgba(255,255,255,.28);
        }
        @media (max-width: 700px) {
            #mobileControls { display: flex; }
            .mBtn { width: 64px; height: 64px; }
            .mBtn.small { width: 58px; height: 58px; }
        }
        @media (min-width: 701px) {
            #mobileControls { display: none; }
        }
"""
text = text.replace("</style>", mobile_css + "\n</style>", 1)

# Add mobile control HTML if it isn't already present.
if 'id="mobileControls"' not in text:
    marker = "</body>"
    controls = r"""
<div id="mobileControls">
  <div class="mobileCluster">
    <div class="mBtn" id="mLeft">◀</div>
    <div class="mBtn" id="mRight">▶</div>
  </div>
  <div class="mobileCluster">
    <div class="mBtn small" id="mDrift">DRIFT</div>
    <div class="mBtn small" id="mBoost">BOOST</div>
    <div class="mBtn" id="mGas">▲</div>
  </div>
</div>
"""
    text = text.replace(marker, controls + "\n" + marker, 1)

# Add robust pointer/touch handlers near the end of the JS.
mobile_js = r"""
// Mobile touch controls: works with one or multiple fingers and does not require a keyboard.
(function () {
  const map = {
    mLeft: 'left',
    mRight: 'right',
    mGas: 'up',
    mDrift: 'drift',
    mBoost: 'boost'
  };

  function press(el, key) {
    const down = (e) => {
      e.preventDefault();
      try { el.setPointerCapture(e.pointerId); } catch (_) {}
      keys[key] = true;
      el.classList.add('active');
    };
    const up = (e) => {
      e.preventDefault();
      keys[key] = false;
      el.classList.remove('active');
    };

    el.addEventListener('pointerdown', down, {passive:false});
    el.addEventListener('pointerup', up, {passive:false});
    el.addEventListener('pointercancel', up, {passive:false});
    el.addEventListener('pointerleave', (e) => {
      if (e.buttons) return;
      up(e);
    }, {passive:false});
  }

  Object.entries(map).forEach(([id, key]) => {
    const el = document.getElementById(id);
    if (el) press(el, key);
  });

  // Prevent the browser from interpreting swipes/taps as page gestures.
  document.addEventListener('touchmove', e => e.preventDefault(), {passive:false});
  document.addEventListener('gesturestart', e => e.preventDefault(), {passive:false});
  document.addEventListener('dblclick', e => e.preventDefault(), {passive:false});

  // Keep the game sized correctly after phone rotation.
  window.addEventListener('orientationchange', () => {
    setTimeout(() => window.dispatchEvent(new Event('resize')), 250);
  });
})();
"""
# Insert before the final script close if possible; otherwise append.
last_script = text.rfind("</script>")
if last_script != -1:
    text = text[:last_script] + mobile_js + "\n" + text[last_script:]
else:
    text += mobile_js

# Make the page height a little more phone-friendly if the original has a viewport meta tag.
if 'name="viewport"' not in text:
    text = text.replace("<head>", '<head><meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1, user-scalable=no">', 1)

app.write_text(text, encoding="utf-8")

# Repack.
out = Path("/mnt/data/kart_highway_3d_mobile.zip")
if out.exists():
    out.unlink()
with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
    for p in work.rglob("*"):
        if p.is_file():
            z.write(p, p.relative_to(work))

print(f"완료: {out}")
