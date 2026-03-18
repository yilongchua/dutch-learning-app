import httpx
from typing import Optional
import trafilatura
from playwright.async_api import async_playwright

class PageExtractionService:
    """
    Service to extract clean article content from URLs.
    Supports both static fetching (httpx) and dynamic rendering (Playwright).
    """
    def __init__(self, timeout: int = 15):
        self.timeout = timeout
        # self.user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        self.user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36"
        self.min_text_length = 400
    
    async def fetch_html(self, url: str) -> Optional[str]:
        """Fetch raw HTML using httpx."""
        try:
            async with httpx.AsyncClient(timeout=self.timeout, follow_redirects=True, headers={"User-Agent": self.user_agent}) as client:
                r = await client.get(url)
                if r.status_code == 200:
                    return r.text
        except Exception as e:
            print(f"[PageExtraction] httpx error for {url}: {e}")
        return None

    async def playwright_render(self, url: str) -> Optional[str]:
        """
        Fallback for JS-heavy websites. 
        Focuses on the body and removes known navigation/header/footer noise.
        """
        try:
            async with async_playwright() as p:
                device = p.devices['Desktop Chrome']
                browser = await p.chromium.launch(headless=True)
                context = await browser.new_context(**device)
                page = await context.new_page()
                
                # Navigate and wait for network to be idle
                await page.goto(url, timeout=30000, wait_until="networkidle")
                
                clean_html = await page.evaluate("""() => {
                    const noiseSelectors = [
                        'nav', 'header', 'footer', 'aside', 
                        '#header', '#footer', '#nav', '.header', '.footer', '.nav',
                        '.sidebar', '.menu', '.ads', 'ins.adsbygoogle', 
                        'script', 'style', 'iframe', 'form', 'noscript'
                    ];
                    
                    // Remove noise from the entire document
                    noiseSelectors.forEach(selector => {
                        document.querySelectorAll(selector).forEach(el => el.remove());
                    });

                    // Return content. Prefer body innerHTML if it exists, 
                    // otherwise fallback to documentElement (html) content.
                    return document.body ? document.body.innerHTML : document.documentElement.innerHTML;
                }""")
                
                await browser.close()
                return f"<html><body>{clean_html}</body></html>"
        except Exception as e:
            print(f"[PageExtraction] Playwright fallback failed for {url}: {e}")
            return None

    def extract_text(self, html: str) -> Optional[str]:
        """Uses trafilatura to extract high-quality main text, ignoring noise."""
        if not html:
            return None
        return trafilatura.extract(html, include_comments=False, include_tables=False, favor_precision=True)

    async def extract_url(self, url: str) -> Optional[str]:
        """Smart extraction: try static first, then full browser rendering."""
        html = await self.fetch_html(url)
        text = self.extract_text(html) if html else None
        
        if not text or len(text) < self.min_text_length:
            html = await self.playwright_render(url)
            if html:
                text = self.extract_text(html)
        
        return text
