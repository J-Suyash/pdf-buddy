import asyncio
import json
import aiohttp

import zendriver as zd
from zendriver import cdp


async def main():
    # Start browser with anti-bot detection features
    browser = await zd.start(
        browser_args=[
            "--disable-blink-features=AutomationControlled",
            "--disable-dev-shm-usage",
            "--disable-extensions",
            "--disable-plugins",
            "--disable-gpu",
            "--remote-debugging-port=9222"
        ]
    )
    
    page = await browser.get("https://www.datalab.to/playground/documents/new")

    # Enable network monitoring
    await page.send(cdp.network.enable())

    # Wait for the page to fully load with a timeout
    # try:
    #     await page.wait_for_ready_state("networkidle", timeout=10000)  # 10 second timeout
    # except asyncio.TimeoutError:
    #     print("Network idle timeout, proceeding with page load")
    #     # Try alternative wait condition
    #     await page.wait_for_ready_state("complete", timeout=5000)

    # Wait a bit more to ensure all dynamic content is loaded
    await asyncio.sleep(3)

    # Handler for network requests and responses
    requests = {}

    async def request_handler(event: cdp.network.RequestWillBeSent):
        requests[event.request_id] = event.request.method

    async def response_handler(event: cdp.network.ResponseReceived):
        method = requests.get(event.request_id)
        if event.response.url == "https://www.datalab.to/api/v1/playground/marker" and method == "POST" and event.response.status == 200:
            try:
                body_result = await page.send(cdp.network.get_response_body(request_id=event.request_id))
                print(f"Body result: {body_result}")
                body = body_result[0]
                print(f"Body: {body}")
                data = json.loads(body)
                polling_url = data['request_check_url']
                print(f"Got polling URL: {polling_url}")
                await browser.stop()
                # Poll for result
                async with aiohttp.ClientSession() as session:
                    while True:
                        async with session.get(polling_url) as res:
                            text = await res.text()
                            print(f"Polling: {text[:100]}...")
                            if '"status":"complete"' in text:
                                with open("result.json", "w") as f:
                                    f.write(text)
                                print("Saved result to result.json")
                                return
                        await asyncio.sleep(5)
            except Exception as e:
                print(f"Error in handler: {e}")

    page.add_handler(cdp.network.RequestWillBeSent, request_handler)
    page.add_handler(cdp.network.ResponseReceived, response_handler)

    try:
        # Find the file input element
        file_input = await page.select('input[type="file"]')

        if file_input:
            print("Found file input element")
            # Send the file path to the input
            file_path = "/home/sxtr/Documents/SEM 5/Discrete Maths/Discrete_Mathematics_-_2025_JULY-B.pdf"
            await file_input.send_file(file_path)
            print(f"Successfully uploaded file: {file_path}")

            # Wait a moment to see the result
            # await asyncio.sleep(2)

            # Click the button that shows the widget
            try:
                # Try to find a button, e.g., with text "Process" or "Submit"
                button = await page.find("Submit", best_match=True) or await page.find("Process", best_match=True) or await page.find("Upload", best_match=True)
                if button:
                    await button.click()
                    print("Clicked the button to show widget")
                    await asyncio.sleep(2)  # Wait for widget to appear
                else:
                    print("No button found to click")
            except Exception as e:
                print(f"Error clicking button: {e}")

            # Now, solve the Turnstile captcha
            try:
                turnstile_div = await page.select('div.w-full.svelte-1vitwd6')
                if turnstile_div:
                    print("Found Turnstile widget, attempting to solve")
                    for attempt in range(10):
                        try:
                            turnstile_check = await page.evaluate('document.querySelector("[name=cf-turnstile-response]").value || ""')
                            print(f"Attempt {attempt + 1}: Turnstile check: '{turnstile_check}'")
                            if turnstile_check == "":
                                print(f"No response yet, clicking Turnstile")
                                await turnstile_div.click()
                                # await asyncio.sleep(1)  # Wait for iframe to load
                                # Click the checkbox inside the iframe by mouse click at center
                                pos = await page.evaluate('''(function() {
                                const div = document.querySelector('div.w-full.svelte-1vitwd6');
                                if (div) {
                                    const rect = div.getBoundingClientRect();
                                    return {x: rect.left + rect.width / 4 - 20, y: rect.top + rect.height / 2};
                                }
                                return null;
                                })()''')
                                print(f"Position: {pos}")
                                if pos:
                                    await page.mouse_click(pos['x'], pos['y'])
                                    print(f"Clicked at {pos['x']}, {pos['y']}")
                                await asyncio.sleep(0.5)
                            else:
                                print(f"Turnstile solved on attempt {attempt + 1}: {turnstile_check[:20]}...")
                                break
                        except Exception as e:
                            print(f"Error on attempt {attempt + 1}: {e}")
                            await asyncio.sleep(0.5)
                    else:
                        print("Failed to solve Turnstile after 10 attempts")

                    # After solving, click the "Parse Document" button
                    parse_button = await page.find("Parse Document", best_match=True)
                    if parse_button:
                        await parse_button.click()
                        print("Clicked Parse Document button")
                    else:
                        print("No Parse Document button found")
                else:
                    print("No Turnstile widget found")
            except Exception as e:
                print(f"Error solving Turnstile: {e}")


        else:
            print("Could not find the file input element")
            # Fallback to clicking the drop zone if input not found
            file_drop_zone = await page.select('div[role="button"].file-drop-zone.playground-drop-zone')
            if file_drop_zone:
                print("Found file drop zone element, clicking to open picker")
                await file_drop_zone.click()
                print("Successfully clicked the file drop zone")
                await asyncio.sleep(2)
                # Note: In a real scenario, you might need to handle the file picker dialog,
                # but since it's programmatic, direct input is preferred.
    
    except Exception as e:
        print(f"Error occurred: {e}")
        # Take a screenshot for debugging
        await page.save_screenshot("error_screenshot.png")
        await browser.stop()

    # Polling is handled in the handler


if __name__ == "__main__":
    asyncio.run(main())
