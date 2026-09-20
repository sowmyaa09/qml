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
        
        # --> Assertions to verify final state
        
        # --> The header shows the research-only advisory about non-medical use.
        # Assert-outcome: passed
        # Assert: The header contains the research-only advisory text.
        await expect(page.locator("#root").nth(0)).to_contain_text("Research risk classification \u2014 not a medical device, not for clinical use.", timeout=15000), "The header contains the research-only advisory text."
        
        # --> The page footer/chrome displays the non-diagnostic research-environment banner.
        # Assert-outcome: passed
        # Assert: The footer/chrome contains the non-diagnostic research environment banner text.
        await expect(page.locator("#root").nth(0)).to_contain_text("[RESEARCH ENVIRONMENT: NON-DIAGNOSTIC] Exploratory hybrid variational quantum algorithms evaluated on anonymized biomedical tables.", timeout=15000), "The footer/chrome contains the non-diagnostic research environment banner text."
        await asyncio.sleep(5)

    finally:
        if context:
            await context.close()
        if browser:
            await browser.close()
        if pw:
            await pw.stop()

asyncio.run(run_test())
    