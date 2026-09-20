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
        
        # -> Click the 'Data' tab in the header to open the Data view.
        # Data button
        elem = page.get_by_role("button", name="Data", exact=True)
        await elem.click(timeout=10000)
        
        # --> Assertions to verify final state
        
        # --> The Data view shows the public catalog filter button "All 23 tables", indicating the public catalog is displayed.
        await page.get_by_role("button", name="All 23 tables").nth(0).scroll_into_view_if_needed()
        # Assert-outcome: passed
        # Assert: The public catalog filter button "All 23 tables" is visible.
        await expect(page.get_by_role("button", name="All 23 tables").nth(0)).to_be_visible(timeout=15000), "The public catalog filter button \"All 23 tables\" is visible."
        
        # --> Dataset entries and saved-model labels are visible on the Data view (for example the "ddd" dataset card and the "QSVC" model label).
        await page.get_by_text("ddd", exact=True).nth(0).scroll_into_view_if_needed()
        # Assert-outcome: passed
        # Assert: A dataset card titled "ddd" is visible.
        await expect(page.get_by_text("ddd", exact=True).nth(0)).to_be_visible(timeout=15000), "A dataset card titled \"ddd\" is visible."
        await page.get_by_text("QSVC", exact=True).first.nth(0).scroll_into_view_if_needed()
        # Assert-outcome: passed
        # Assert: A saved-model label "QSVC" is visible on a dataset card.
        await expect(page.get_by_text("QSVC", exact=True).first.nth(0)).to_be_visible(timeout=15000), "A saved-model label \"QSVC\" is visible on a dataset card."
        await asyncio.sleep(5)

    finally:
        if context:
            await context.close()
        if browser:
            await browser.close()
        if pw:
            await pw.stop()

asyncio.run(run_test())
    