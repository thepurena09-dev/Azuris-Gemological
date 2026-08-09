import asyncio
from playwright.async_api import async_playwright
URL="https://hero-gem-editor.preview.emergentagent.com"; E,P="admin@azuris.local","AzurisDev@2026!"
async def ov(pg): return await pg.evaluate("({sw:document.documentElement.scrollWidth,iw:window.innerWidth,over:document.documentElement.scrollWidth>window.innerWidth+2})")
async def main():
    async with async_playwright() as p:
        b=await p.chromium.launch(headless=True,executable_path="/usr/bin/google-chrome",args=["--no-sandbox","--disable-dev-shm-usage"])
        # MOBILE
        m=await b.new_context(viewport={"width":390,"height":844},device_scale_factor=2,ignore_https_errors=True)
        pg=await m.new_page()
        await pg.goto(URL+"/login",wait_until="networkidle")
        await pg.fill("[data-testid=login-email]",E); await pg.fill("[data-testid=login-password]",P)
        await pg.click("[data-testid=login-submit]"); await pg.wait_for_url("**/admin/**",timeout=15000); await pg.wait_for_timeout(1200)
        print("mobile dash overflow:", await ov(pg))
        await pg.click("[data-testid=admin-mobile-nav-toggle]"); await pg.wait_for_timeout(500)
        await pg.screenshot(path="/tmp/mv_drawer.png")
        # navigate via drawer
        await pg.click("[data-testid=admin-nav-certificates-m]"); await pg.wait_for_timeout(1200)
        print("after drawer nav url:", pg.url, "overflow:", await ov(pg))
        await pg.screenshot(path="/tmp/mv_after_nav.png")
        await m.close()
        # DESKTOP intact
        d=await b.new_context(viewport={"width":1280,"height":900},ignore_https_errors=True)
        pg2=await d.new_page()
        await pg2.goto(URL+"/login",wait_until="networkidle")
        await pg2.fill("[data-testid=login-email]",E); await pg2.fill("[data-testid=login-password]",P)
        await pg2.click("[data-testid=login-submit]"); await pg2.wait_for_url("**/admin/**",timeout=15000); await pg2.wait_for_timeout(1000)
        sb=await pg2.is_visible("[data-testid=admin-sidebar]")
        tog=await pg2.is_visible("[data-testid=admin-mobile-nav-toggle]")
        print("desktop sidebar visible:", sb, "| hamburger visible(should be False):", tog, "| overflow:", await ov(pg2))
        await pg2.screenshot(path="/tmp/dv_admin.png")
        await b.close()
asyncio.run(main())
