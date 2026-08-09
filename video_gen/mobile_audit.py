import asyncio, sys
from playwright.async_api import async_playwright

URL = "https://cert-processor.preview.emergentagent.com"
EMAIL, PW = "admin@azuris.local", "AzurisDev@2026!"

async def overflow(page):
    return await page.evaluate("({sw:document.documentElement.scrollWidth, iw:window.innerWidth, over:document.documentElement.scrollWidth>window.innerWidth+2})")

async def shot(page, name):
    await page.screenshot(path=f"/tmp/{name}.png")
    print(name, await overflow(page))

async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(headless=True, executable_path="/usr/bin/google-chrome", args=["--no-sandbox","--disable-dev-shm-usage"])
        ctx = await b.new_context(viewport={"width":390,"height":844}, device_scale_factor=2, ignore_https_errors=True)
        page = await ctx.new_page()
        # public home
        await page.goto(URL+"/", wait_until="networkidle"); await page.wait_for_timeout(1200)
        await shot(page, "ma_home")
        # mobile menu
        try:
            await page.click('[data-testid="header-mobile-toggle"]'); await page.wait_for_timeout(500)
            await shot(page, "ma_home_menu")
        except Exception as e: print("menu err", e)
        # login
        await page.goto(URL+"/login", wait_until="networkidle"); await page.wait_for_timeout(1000)
        await shot(page, "ma_login")
        # authenticate then admin
        await page.fill("[data-testid=login-email]", EMAIL)
        await page.fill("[data-testid=login-password]", PW)
        await page.click("[data-testid=login-submit]")
        await page.wait_for_url("**/admin/**", timeout=15000); await page.wait_for_timeout(1500)
        await shot(page, "ma_admin_dashboard")
        for route,name in [("/admin/certificates","ma_admin_cert"),("/admin/customers","ma_admin_customers"),("/admin/ownership","ma_admin_ownership")]:
            await page.goto(URL+route, wait_until="networkidle"); await page.wait_for_timeout(1200)
            await shot(page, name)
        await b.close()

asyncio.run(main())
