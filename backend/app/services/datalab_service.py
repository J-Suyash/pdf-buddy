"""
Datalab OCR Service

This service uses zendriver (stealth browser automation) to interact with
datalab.to's playground for PDF OCR processing. It handles:
1. Browser automation with anti-bot detection
2. PDF upload
3. Turnstile captcha solving
4. Polling for results
5. Parsing the complex JSON response

Note: This requires Chromium to be installed in the environment.
"""

import asyncio
import json
import os
import base64
import re
import logging
from typing import Optional, Callable, Dict, Any, List
from dataclasses import dataclass, field
from html.parser import HTMLParser

import aiohttp

logger = logging.getLogger(__name__)


class HTMLTextExtractor(HTMLParser):
    """Simple HTML parser to extract text content."""

    def __init__(self):
        super().__init__()
        self.text_parts = []

    def handle_data(self, data):
        self.text_parts.append(data.strip())

    def get_text(self) -> str:
        return " ".join(part for part in self.text_parts if part)


def extract_text_from_html(html: str) -> str:
    """Extract plain text from HTML content."""
    if not html:
        return ""
    parser = HTMLTextExtractor()
    try:
        parser.feed(html)
        return parser.get_text()
    except Exception:
        # Fallback: simple regex-based extraction
        clean = re.sub(r"<[^>]+>", " ", html)
        return " ".join(clean.split())


@dataclass
class ParsedBlock:
    """Represents a parsed block/chunk from the datalab response."""

    block_id: str
    block_type: str
    page: int
    html: str
    text: str
    bbox: List[float]
    polygon: List[List[float]]
    section_hierarchy: Dict[str, str]
    images: Dict[str, str]  # image_name -> file_path (after saving)


@dataclass
class ParsedPage:
    """Represents a parsed page from the datalab response."""

    page_num: int
    num_blocks: int
    markdown: str = ""
    html: str = ""
    blocks: List[ParsedBlock] = field(default_factory=list)


@dataclass
class ParsedDatalabResult:
    """Complete parsed result from datalab OCR."""

    status: str
    success: bool
    page_count: int
    markdown: str
    html: str
    runtime_seconds: float
    pages: List[ParsedPage] = field(default_factory=list)
    images: Dict[str, str] = field(default_factory=dict)  # image_name -> file_path


class DatalabService:
    """
    Service for processing PDFs using Datalab's OCR API via browser automation.
    """

    DATALAB_URL = "https://www.datalab.to/playground/documents/new"
    DATALAB_API_URL = "https://www.datalab.to/api/v1/playground/marker"

    def __init__(self, storage_dir: str = "./storage/datalab"):
        self.storage_dir = storage_dir
        os.makedirs(storage_dir, exist_ok=True)

    async def process_pdf(
        self,
        file_path: str,
        job_id: str,
        progress_callback: Optional[Callable[[int, str], None]] = None,
    ) -> Dict[str, Any]:
        """
        Process a PDF using Datalab's OCR.

        Args:
            file_path: Path to the PDF file
            job_id: Job ID for tracking
            progress_callback: Optional callback for progress updates (progress%, message)

        Returns:
            Raw datalab response dict
        """
        # Import zendriver here to avoid import errors when module loads
        import zendriver as zd
        from zendriver import cdp

        def update_progress(progress: int, message: str):
            logger.info(f"[Job {job_id}] {progress}%: {message}")
            if progress_callback:
                progress_callback(progress, message)

        update_progress(5, "Starting browser")

        browser = None
        polling_url = None
        result_data = None

        try:
            # Start browser with anti-bot detection features
            browser = await zd.start(
                browser_args=[
                    "--disable-blink-features=AutomationControlled",
                    "--disable-dev-shm-usage",
                    "--disable-extensions",
                    "--disable-plugins",
                    "--disable-gpu",
                    "--no-sandbox",  # Required for Docker
                    "--disable-setuid-sandbox",  # Required for Docker
                ]
            )

            update_progress(10, "Navigating to Datalab")
            page = await browser.get(self.DATALAB_URL)

            # Enable network monitoring
            await page.send(cdp.network.enable())

            # Wait for page to load
            await asyncio.sleep(3)

            update_progress(15, "Page loaded, preparing upload")

            # Set up network handler to capture the API response
            requests = {}
            captured_polling_url = {"url": None}

            async def request_handler(event: cdp.network.RequestWillBeSent):
                requests[event.request_id] = event.request.method

            async def response_handler(event: cdp.network.ResponseReceived):
                method = requests.get(event.request_id)
                if (
                    event.response.url == self.DATALAB_API_URL
                    and method == "POST"
                    and event.response.status == 200
                ):
                    try:
                        body_result = await page.send(
                            cdp.network.get_response_body(request_id=event.request_id)
                        )
                        body = body_result[0]
                        data = json.loads(body)
                        captured_polling_url["url"] = data.get("request_check_url")
                        logger.info(
                            f"Captured polling URL: {captured_polling_url['url']}"
                        )
                    except Exception as e:
                        logger.error(f"Error capturing response: {e}")

            page.add_handler(cdp.network.RequestWillBeSent, request_handler)
            page.add_handler(cdp.network.ResponseReceived, response_handler)

            # Find and use file input
            update_progress(20, "Uploading PDF")
            file_input = await page.select('input[type="file"]')

            if not file_input:
                # Fallback to drop zone if input not found
                file_drop_zone = await page.select('div[role="button"].file-drop-zone.playground-drop-zone')
                if file_drop_zone:
                    await file_drop_zone.click()
                    await asyncio.sleep(1)
                else:
                    raise RuntimeError("Could not find file input element")

            await file_input.send_file(file_path)
            logger.info(f"Uploaded file: {file_path}")
            await asyncio.sleep(2)

            # Click initial process button if present (optional step to show widget)
            update_progress(25, "Initial processing check")
            try:
                # Direct match from datalab.py: Submit, Process, or Upload
                button = (
                    await page.find("Submit", best_match=True, timeout=2) or 
                    await page.find("Process", best_match=True, timeout=2) or 
                    await page.find("Upload", best_match=True, timeout=2)
                )
                if button:
                    await button.click()
                    logger.info("Clicked initial button (Submit/Process/Upload)")
                    await asyncio.sleep(2)
            except Exception as e:
                logger.debug(f"Optional initial button not found or already proceeded: {e}")

            # Solve Turnstile captcha
            update_progress(30, "Solving captcha")
            try:
                turnstile_div = await page.select('div.w-full.svelte-1vitwd6')
                if turnstile_div:
                    logger.info("Found Turnstile widget, attempting to solve")
                    for attempt in range(10):
                        try:
                            turnstile_check = await page.evaluate('document.querySelector("[name=cf-turnstile-response]").value || ""')
                            if turnstile_check:
                                logger.info(f"Turnstile solved on attempt {attempt + 1}")
                                break
                            
                            logger.info(f"Attempt {attempt + 1}: Clicking Turnstile")
                            # Click the div itself first
                            await turnstile_div.click()
                            
                            # Calculate position for center-left click as per datalab.py
                            pos = await page.evaluate('''(function() {
                                const div = document.querySelector('div.w-full.svelte-1vitwd6');
                                if (div) {
                                    const rect = div.getBoundingClientRect();
                                    return {x: rect.left + rect.width / 4 - 20, y: rect.top + rect.height / 2};
                                }
                                return null;
                            })()''')
                            
                            if pos and isinstance(pos, dict):
                                await page.mouse_click(pos['x'], pos['y'])
                                logger.debug(f"Clicked at coordinates: {pos}")
                            
                            await asyncio.sleep(1) # Wait for state change
                        except Exception as e:
                            logger.warning(f"Captcha attempt {attempt + 1} error: {e}")
                            await asyncio.sleep(0.5)
                    else:
                        logger.warning("Failed to solve Turnstile after 10 attempts, trying to proceed anyway")
                else:
                    logger.info("No Turnstile widget found, skipping captcha solve")
            except Exception as e:
                logger.error(f"Error during Turnstile solve: {e}")

            # Click Parse Document button (this is usually the final trigger)
            update_progress(35, "Finalizing parse request")
            try:
                parse_button = await page.find("Parse Document", best_match=True, timeout=10)
                if parse_button:
                    await parse_button.click()
                    logger.info("Clicked Parse Document button")
                else:
                    logger.warning("Parse Document button not found, checking if polling started anyway")
            except Exception as e:
                logger.error(f"Could not find Parse Document button: {e}")
                # We don't raise here yet, because the network handler might have already captured the URL

            # Wait for polling URL to be captured
            await asyncio.sleep(3)

            for _ in range(10):
                if captured_polling_url["url"]:
                    break
                await asyncio.sleep(1)

            polling_url = captured_polling_url["url"]

            if not polling_url:
                raise RuntimeError("Failed to capture polling URL")

            # Close browser, we have the polling URL
            await browser.stop()
            browser = None

            # Poll for results
            update_progress(50, "Polling for results")
            async with aiohttp.ClientSession() as session:
                max_attempts = 120  # 10 minutes max
                for attempt in range(max_attempts):
                    async with session.get(polling_url) as res:
                        text = await res.text()

                        if '"status":"complete"' in text:
                            result_data = json.loads(text)
                            update_progress(70, "Results received")
                            break
                        elif '"status":"failed"' in text or '"success":false' in text:
                            result_data = json.loads(text)
                            raise RuntimeError(
                                f"Datalab processing failed: {result_data.get('error', 'Unknown error')}"
                            )

                        # Update progress during polling
                        poll_progress = 50 + (attempt * 15 // max_attempts)
                        update_progress(
                            poll_progress, f"Polling... attempt {attempt + 1}"
                        )

                    await asyncio.sleep(5)
                else:
                    raise RuntimeError("Polling timeout - processing took too long")

            return result_data

        except Exception as e:
            logger.error(f"Datalab processing error: {e}")
            raise
        finally:
            if browser:
                try:
                    await browser.stop()
                except Exception:
                    pass

    def parse_response(
        self, response: Dict[str, Any], job_id: str
    ) -> ParsedDatalabResult:
        """
        Parse the complex datalab JSON response into structured objects.
        Also saves images to disk and updates image references.

        Args:
            response: Raw datalab response dict
            job_id: Job ID for creating storage subdirectory

        Returns:
            ParsedDatalabResult with all structured data
        """
        # Create job-specific storage directory
        job_storage_dir = os.path.join(self.storage_dir, job_id)
        images_dir = os.path.join(job_storage_dir, "images")
        os.makedirs(images_dir, exist_ok=True)

        # Extract top-level data
        status = response.get("status", "unknown")
        success = response.get("success", False)
        page_count = response.get("page_count", 0)
        markdown = response.get("markdown", "")
        html = response.get("html", "")
        runtime = response.get("runtime", 0.0)

        # Save images to disk
        saved_images = {}
        raw_images = response.get("images", {})
        for image_name, image_base64 in raw_images.items():
            if image_base64:
                image_path = os.path.join(images_dir, image_name)
                try:
                    image_data = base64.b64decode(image_base64)
                    with open(image_path, "wb") as f:
                        f.write(image_data)
                    saved_images[image_name] = image_path
                    logger.debug(f"Saved image: {image_path}")
                except Exception as e:
                    logger.warning(f"Failed to save image {image_name}: {e}")

        # Parse chunks/blocks
        chunks_data = response.get("chunks", {})
        blocks = chunks_data.get("blocks", [])
        page_info = chunks_data.get("page_info", [])
        metadata = response.get("metadata", {})
        page_stats = metadata.get("page_stats", [])

        # Create page stats lookup
        stats_by_page = {stat["page_id"]: stat["num_blocks"] for stat in page_stats}

        # Group blocks by page
        blocks_by_page: Dict[int, List[ParsedBlock]] = {}
        for block in blocks:
            page_num = block.get("page", 0)
            if page_num not in blocks_by_page:
                blocks_by_page[page_num] = []

            # Extract text from HTML
            block_html = block.get("html", "")
            block_text = extract_text_from_html(block_html)

            # Process block images - update paths to saved files
            block_images = block.get("images", {})
            processed_images = {}
            for img_name, img_data in block_images.items():
                if img_name in saved_images:
                    processed_images[img_name] = saved_images[img_name]
                elif img_data:
                    # Save inline block image
                    img_path = os.path.join(
                        images_dir,
                        f"block_{block.get('id', '').replace('/', '_')}_{img_name}",
                    )
                    try:
                        img_bytes = base64.b64decode(img_data)
                        with open(img_path, "wb") as f:
                            f.write(img_bytes)
                        processed_images[img_name] = img_path
                    except Exception as e:
                        logger.warning(f"Failed to save block image: {e}")

            parsed_block = ParsedBlock(
                block_id=block.get("id", ""),
                block_type=block.get("block_type", ""),
                page=page_num,
                html=block_html,
                text=block_text,
                bbox=block.get("bbox", []),
                polygon=block.get("polygon", []),
                section_hierarchy=block.get("section_hierarchy", {}),
                images=processed_images,
            )
            blocks_by_page[page_num].append(parsed_block)

        # Create ParsedPage objects
        pages = []
        for page_num in range(page_count):
            page_blocks = blocks_by_page.get(page_num, [])
            num_blocks = stats_by_page.get(page_num, len(page_blocks))

            # Compile page-level markdown and HTML from blocks
            page_markdown = "\n\n".join(b.text for b in page_blocks if b.text)
            page_html = "\n".join(b.html for b in page_blocks if b.html)

            parsed_page = ParsedPage(
                page_num=page_num,
                num_blocks=num_blocks,
                markdown=page_markdown,
                html=page_html,
                blocks=page_blocks,
            )
            pages.append(parsed_page)

        return ParsedDatalabResult(
            status=status,
            success=success,
            page_count=page_count,
            markdown=markdown,
            html=html,
            runtime_seconds=runtime,
            pages=pages,
            images=saved_images,
        )


# Singleton instance - uses config for storage directory
from app.config import settings

datalab_service = DatalabService(storage_dir=settings.datalab_storage_dir)
