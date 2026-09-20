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
        
        # -> Click the 'More' button in the top navigation to open the More menu.
        # More button
        elem = page.get_by_role("button", name="More")
        await elem.click(timeout=10000)
        
        # -> Click the 'Paste a record' option in the More menu to open the paste-a-record input flow.
        # Paste a record button
        elem = page.get_by_role("banner").get_by_role("button", name="Paste a record")
        await elem.click(timeout=10000)
        
        # -> Fill the 'Tabular Vector Input' textarea with numeric lines for mean perimeter, mean concave points, worst radius, worst perimeter, worst area, and worst concave points, then click the 'Score this table' button.
        # mean perimeter: 122.8 mean concave points: 0.1471... text area
        elem = page.get_by_role("textbox", name="mean perimeter: 122.8 mean")
        await elem.wait_for(state="visible", timeout=10000)
        await elem.fill("mean perimeter: 122.8\nmean concave points: 0.1471\nworst radius: 25.38\nworst perimeter: 184.6\nworst area: 1000.2\nworst concave points: 0.287")
        
        # -> Fill the 'Tabular Vector Input' textarea with numeric lines for mean perimeter, mean concave points, worst radius, worst perimeter, worst area, and worst concave points, then click the 'Score this table' button.
        # Score this table button
        elem = page.get_by_role("button", name="Score this table")
        await elem.click(timeout=10000)
        
        # --> Assertions to verify final state
        
        # --> The page displays the research score results area (research score view is visible).
        await page.locator(".p-3 > div > .w-8").nth(0).scroll_into_view_if_needed()
        # Assert-outcome: passed
        # Assert: Research score results area is visible on the page.
        await expect(page.locator(".p-3 > div > .w-8").nth(0)).to_be_visible(timeout=15000), "Research score results area is visible on the page."
        
        # --> The submitted numeric record is present in the paste-a-record textarea.
        # Assert-outcome: passed
        # Assert: The paste-a-record textarea contains the six submitted numeric lines.
        await expect(page.get_by_role("textbox", name="mean perimeter: 122.8 mean").nth(0)).to_have_value("mean perimeter: 122.8\nmean concave points: 0.1471\nworst radius: 25.38\nworst perimeter: 184.6\nworst area: 1000.2\nworst concave points: 0.287", timeout=15000), "The paste-a-record textarea contains the six submitted numeric lines."
        await asyncio.sleep(5)

    finally:
        if context:
            await context.close()
        if browser:
            await browser.close()
        if pw:
            await pw.stop()

asyncio.run(run_test())
    