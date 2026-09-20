import asyncio
import re
from playwright import async_api
from playwright.async_api import expect

async def run_test():
    pw = None
    browser = None
    context = None

    try:
        # Start a Playwright session in asynchronous mode
        pw = await async_api.async_playwright().start()

        # Launch a Chromium browser in headless mode with custom arguments
        browser = await pw.chromium.launch(
            headless=True,
            args=[
                "--window-size=1280,720",
                "--disable-dev-shm-usage",
                "--ipc=host",
                "--single-process"
            ],
        )

        # Create a new browser context (like an incognito window)
        context = await browser.new_context()
        # Wider default timeout to match the agent's DOM-stability budget;
        # auto-waiting Playwright APIs (expect, locator.wait_for) inherit this.
        context.set_default_timeout(15000)

        # Open a new page in the browser context
        page = await context.new_page()

        # Interact with the page elements to simulate user flow
        # -> navigate
        await page.goto("http://localhost:8000/")
        try:
            await page.wait_for_load_state("domcontentloaded", timeout=5000)
        except Exception:
            pass
        
        # -> Click the 'Cost' tab in the top navigation to open the cost dashboard.
        # Cost button
        elem = page.get_by_role("button", name="Cost", exact=True)
        await elem.click(timeout=10000)
        
        # --> Assertions to verify final state
        
        # --> The page shows the QSVC vs RBF F1 comparison.
        # Assert-outcome: passed
        # Assert: Page contains the label 'QSVC'.
        await expect(page.locator("#root").nth(0)).to_contain_text("QSVC", timeout=15000), "Page contains the label 'QSVC'."
        # Assert-outcome: passed
        # Assert: Page contains the label 'RBF'.
        await expect(page.locator("#root").nth(0)).to_contain_text("RBF", timeout=15000), "Page contains the label 'RBF'."
        
        # --> The page shows the QSVC fit-time explanatory message about QSVC taking much longer to fit.
        # Assert-outcome: passed
        # Assert: Page displays the QSVC fit-time explanatory message.
        await expect(page.locator("#root").nth(0)).to_contain_text("QSVC matches RBF on F1 within this split but takes ~477\u00d7 longer to fit", timeout=15000), "Page displays the QSVC fit-time explanatory message."
        await asyncio.sleep(5)

    finally:
        if context:
            await context.close()
        if browser:
            await browser.close()
        if pw:
            await pw.stop()

asyncio.run(run_test())
    