# E-commerce Product URL Crawler

This crawler extracts product URLs from e-commerce websites by using a combination of static HTML scraping (BeautifulSoup) and dynamic scraping (Playwright for JavaScript-heavy pages). The goal is to identify and collect links pointing to product pages.
## Steps for URL Extraction:

1. URL Validation: Ensures the URL follows the proper format (HTTP/HTTPS) using a regex pattern.
2. Filtering Product URLs: 
   1. The crawler looks for URLs containing specific keywords like /products/ or /product/.
   2. Converts relative URLs to absolute URLs using the base domain.
3. JavaScript-Rendered Content (Playwright): For pages that load content dynamically (via JavaScript), Playwright is used to fetch and     
   scroll the page to ensure all product links are loaded.
4. Static Content (Requests): For static HTML pages, requests fetches the content directly.
5. Handling Pagination: For infinite scroll or multiple pages, the crawler simulates scrolling and loading additional content using 
   Playwright’s scroll_page function. 
6. Storing Results: URLs are stored in a Python set (to avoid duplicates), then converted into a list for JSON serialization:
7. Edge Cases Handled:
   1. Converts relative URLs to absolute.
   2. Filters out irrelevant links (e.g., app download links).
   3. Handles JavaScript-heavy pages via Playwright.
## Run Instructions

```bash
sudo apt update
sudo apt install python3 python3-pip

python -m venv venv
source venv/bin/activate   # macOS/Linux
pip install -r requirements.txt
python -m playwright install
python crawler.py
```
