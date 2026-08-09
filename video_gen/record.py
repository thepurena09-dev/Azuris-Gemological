"""PHASE 7 — Visual recording of the REAL AZURIS UI (Playwright, 9:16 1080x1920).

- Pre-authenticates ONCE (off-camera) and reuses storage_state, so admin pages
  are recorded already-logged-in and NO credentials ever appear on screen.
- A visible fake cursor + click ripple + element highlight are injected so the
  recording shows real navigation/interaction.
- One webm per scene, recorded slightly longer than its voice-over; trimmed to
  exact duration in render.py. Nothing here touches the web app itself.

Usage:  python record.py            # all scenes
        python record.py 1 8 13     # only these scene indices
"""
import asyncio
import json
import os
import sys

from playwright.async_api import async_playwright

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import config as C  # noqa: E402

STORAGE = os.path.join(C.OUT, "storage_state.json")

CURSOR_JS = """
if (!window.__cursorInit) {
  window.__cursorInit = true;
  const c = document.createElement('div');
  c.id = '__vcursor';
  c.style.cssText = 'position:fixed;top:0;left:0;width:26px;height:26px;z-index:2147483647;' +
    'pointer-events:none;transition:transform .5s cubic-bezier(.22,.61,.36,1);' +
    'transform:translate(60px,60px);filter:drop-shadow(0 2px 4px rgba(0,0,0,.4));';
  c.innerHTML = '<svg width="26" height="26" viewBox="0 0 24 24" fill="none">' +
    '<path d="M4 2l6.5 16 2.2-6.3L19 9.5 4 2z" fill="#0D1B2A" stroke="#fff" stroke-width="1.4"/></svg>';
  const add = () => (document.body || document.documentElement).appendChild(c);
  if (document.body) add(); else document.addEventListener('DOMContentLoaded', add);
  window.__moveCursor = (x, y) => { c.style.transform = `translate(${x}px,${y}px)`; };
  window.__ripple = (x, y) => {
    const r = document.createElement('div');
    r.style.cssText = 'position:fixed;left:'+(x-6)+'px;top:'+(y-6)+'px;width:12px;height:12px;'+
      'border:2px solid #C7A247;border-radius:50%;z-index:2147483646;pointer-events:none;'+
      'transition:all .5s ease-out;opacity:1;';
    (document.body||document.documentElement).appendChild(r);
    requestAnimationFrame(()=>{ r.style.transform='scale(4)'; r.style.opacity='0'; });
    setTimeout(()=>r.remove(), 600);
  };
  window.__highlight = (sel) => {
    const el = document.querySelector(sel); if (!el) return;
    const o = el.style.outline, off = el.style.outlineOffset, t = el.style.transition;
    el.style.transition='outline .25s ease'; el.style.outline='3px solid #C7A247';
    el.style.outlineOffset='3px';
    setTimeout(()=>{ el.style.outline=o; el.style.outlineOffset=off; el.style.transition=t; }, 1400);
  };
}
"""

# route + beats. Beat kinds: goto / scrollTo(frac) / anchor(sel) / cursor(sel) / click(sel) / hold
BEATS = {
    1:  [("goto", "/"), ("cursor", "[data-testid=hero-logo]"), ("scrollTo", 0.06), ("hold",)],
    2:  [("goto", "/"), ("scrollTo", 0.18), ("scrollTo", 0.34), ("scrollTo", 0.5),
         ("goto", "/admin/dashboard"), ("hold",)],
    3:  [("goto", "/"), ("click", "[data-testid=nav-verification]"), ("anchor", "#verification"),
         ("hold",), ("hold",)],
    4:  [("scrollTo", 0.55), ("scrollTo", 0.72), ("scrollTo", 0.88),
         ("goto", "/legalitas"), ("hold",)],
    5:  [("goto", "/"), ("anchor", "#keanggotaan"), ("cursor", "[data-testid=home-membership-cta]"),
         ("goto", "/membership"), ("hold",)],
    6:  [("goto", "/login"), ("cursor", "[data-testid=login-submit]"), ("hold",),
         ("goto", "/admin/dashboard"), ("hold",)],
    7:  [("goto", "/admin/dashboard"), ("cursor", "[data-testid=dash-metrics]"), ("scrollTo", 0.3),
         ("cursor", "[data-testid=dash-verify-chart]"), ("scrollTo", 0.55), ("hold",)],
    8:  [("goto", "/admin/certificates"), ("scrollTo", 0.2), ("scrollTo", 0.42),
         ("click", "[data-testid=cert-demo-preview-btn]"), ("hold",), ("hold",)],
    9:  [("goto", "/admin/gemstones"), ("hold",), ("click", "[data-testid=admin-nav-jewelry]"),
         ("hold",), ("click", "[data-testid=admin-nav-customers]"), ("hold",)],
    10: [("goto", "/admin/warranties"), ("hold",), ("click", "[data-testid=admin-nav-ownership]"),
         ("hold",), ("click", "[data-testid=admin-nav-membership]"), ("hold",)],
    11: [("goto", "/admin/visuals"), ("hold",), ("click", "[data-testid=admin-nav-settings]"),
         ("hold",), ("click", "[data-testid=admin-nav-legality]"), ("hold",)],
    12: [("goto", "/"), ("scrollTo", 0.25), ("goto", "/admin/dashboard"),
         ("goto", "/admin/certificates"), ("goto", "/admin/membership"), ("goto", "/")],
    13: [("goto", "/"), ("cursor", "[data-testid=hero-logo]"), ("scrollTo", 0.0), ("hold",)],
}


async def _cursor_to(page, sel):
    try:
        el = await page.query_selector(sel)
        if not el:
            return
        await el.scroll_into_view_if_needed(timeout=2500)
        box = await el.bounding_box()
        if not box:
            return
        x, y = box["x"] + box["width"] / 2, box["y"] + box["height"] / 2
        await page.evaluate("([x,y])=>window.__moveCursor&&window.__moveCursor(x,y)", [x, y])
        await page.mouse.move(x, y)
        await page.evaluate("s=>window.__highlight&&window.__highlight(s)", sel)
        await asyncio.sleep(0.55)
    except Exception as e:
        print("   cursor warn:", sel, e)


async def _click(page, sel):
    try:
        el = await page.query_selector(sel)
        if not el:
            print("   click miss:", sel)
            return
        await el.scroll_into_view_if_needed(timeout=2500)
        box = await el.bounding_box()
        if box:
            x, y = box["x"] + box["width"] / 2, box["y"] + box["height"] / 2
            await page.evaluate("([x,y])=>window.__moveCursor&&window.__moveCursor(x,y)", [x, y])
            await page.mouse.move(x, y)
            await asyncio.sleep(0.45)
            await page.evaluate("([x,y])=>window.__ripple&&window.__ripple(x,y)", [x, y])
        await el.click(timeout=3000)
        await page.wait_for_timeout(500)
    except Exception as e:
        print("   click warn:", sel, e)


async def _scroll_to(page, frac):
    try:
        await page.evaluate(
            "f=>window.scrollTo({top:(document.body.scrollHeight-innerHeight)*f,behavior:'smooth'})", frac
        )
        await asyncio.sleep(0.6)
    except Exception:
        pass


async def _anchor(page, sel):
    try:
        await page.evaluate(
            "s=>{const e=document.querySelector(s); if(e)e.scrollIntoView({behavior:'smooth',block:'center'});}", sel
        )
        await asyncio.sleep(0.6)
    except Exception:
        pass


async def run_beats(page, beats, seconds):
    import time
    per = max(0.7, seconds / len(beats))
    for kind, *arg in beats:
        t0 = time.time()
        if kind == "goto":
            try:
                await page.goto(C.APP_URL + arg[0], wait_until="domcontentloaded", timeout=15000)
                await page.wait_for_timeout(700)
            except Exception as e:
                print("   goto warn:", arg[0], e)
        elif kind == "scrollTo":
            await _scroll_to(page, arg[0])
        elif kind == "anchor":
            await _anchor(page, arg[0])
        elif kind == "cursor":
            await _cursor_to(page, arg[0])
        elif kind == "click":
            await _click(page, arg[0])
        # hold / fill remaining slice
        elapsed = time.time() - t0
        if elapsed < per:
            await asyncio.sleep(per - elapsed)


async def authenticate(browser):
    if os.path.exists(STORAGE):
        return
    ctx = await browser.new_context(viewport={"width": C.W, "height": C.H}, ignore_https_errors=True)
    page = await ctx.new_page()
    await page.goto(C.APP_URL + "/login", wait_until="domcontentloaded", timeout=20000)
    await page.fill("[data-testid=login-email]", C.ADMIN_EMAIL)
    await page.fill("[data-testid=login-password]", C.ADMIN_PASSWORD)
    await page.click("[data-testid=login-submit]")
    await page.wait_for_url("**/admin/**", timeout=15000)
    await page.wait_for_timeout(1500)
    await ctx.storage_state(path=STORAGE)
    await ctx.close()
    print("authenticated (off-camera), storage saved")


async def record_scene(browser, scene):
    idx = scene["index"]
    dur = scene["audio_duration"] + 0.6  # small tail, trimmed later
    ctx = await browser.new_context(
        viewport={"width": C.W, "height": C.H},
        storage_state=STORAGE,
        ignore_https_errors=True,
        record_video_dir=C.VIDEO_DIR,
        record_video_size={"width": C.W, "height": C.H},
        device_scale_factor=1,
    )
    await ctx.add_init_script(CURSOR_JS)
    page = await ctx.new_page()
    print(f"scene-{idx:02d}: recording ~{dur:.1f}s ...")
    await run_beats(page, BEATS[idx], dur)
    vid = page.video
    await ctx.close()
    src = await vid.path()
    dst = os.path.join(C.VIDEO_DIR, f"scene-{idx:02d}.webm")
    if os.path.exists(dst):
        os.remove(dst)
    os.rename(src, dst)
    print(f"   -> {dst}")


async def main():
    only = [int(a) for a in sys.argv[1:]] if len(sys.argv) > 1 else None
    with open(os.path.join(C.OUT, "manifest.json")) as f:
        scenes = json.load(f)["scenes"]
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True, args=["--no-sandbox", "--disable-dev-shm-usage"])
        await authenticate(browser)
        for s in scenes:
            if only and s["index"] not in only:
                continue
            await record_scene(browser, s)
        await browser.close()
    print("recording done")


if __name__ == "__main__":
    asyncio.run(main())
