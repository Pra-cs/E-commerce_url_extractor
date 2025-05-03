import asyncio
import re
import json
from bs4 import BeautifulSoup
from playwright.async_api import async_playwright
import requests

# Function to check if a URL is valid
def is_valid_url(url):
    return bool(re.match(r'https?://[^\s/$.?#].[^\s]*', url))

# Function to refine the URLs, filtering for product pages
def refine_product_urls(links, base_url):
    refined_urls = set()
    for link in links:
        if 'product' in link or 'p/' in link or '/products/' in link:
            # Make the link absolute if it is relative
            if link.startswith('/'):
                link = base_url + link
            refined_urls.add(link)
    return refined_urls

# Function to fetch HTML content using Playwright with dynamic page interaction
async def fetch_with_js(url):
    if is_valid_url(url):  # Only proceed if the URL is valid
        try:
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=True)  # Launch browser in headless mode
                page = await browser.new_page()
                await page.goto(url, timeout=60000)  # Increased timeout for slower pages
                await scroll_page(page)  # Add scrolling to ensure more products load
                content = await page.content()  # Get the full content of the page
                await browser.close()
                return content, page  # Return both content and page
        except Exception as e:
            print(f"Error fetching {url}: {e}")
            return None, None
    else:
        print(f"Invalid URL: {url}")
        return None, None

# Function to scroll the page to load more content (useful for JS-rendered content)
async def scroll_page(page):
    try:
        # Scroll the page a few times to load more content
        for _ in range(5):  # Adjust the range for more scrolls
            await page.evaluate('window.scrollTo(0, document.body.scrollHeight)')
            await page.wait_for_timeout(2000)  # Wait for 2 seconds after scrolling
    except Exception as e:
        print(f"Error scrolling page: {e}")

# Function to fetch HTML content using requests (for non-JS pages)
def fetch_html_with_requests(url):
    try:
        response = requests.get(url)
        return response.text if response.status_code == 200 else None
    except requests.exceptions.RequestException as e:
        print(f"Error fetching {url} with requests: {e}")
        return None

# Function to handle crawling of a single domain
async def crawl_domain(url):
    print(f"Starting crawl for {url}")
    product_urls = set()  # Use set to store unique URLs

    # Handle specific websites like nykaafashion and westside
    if 'nykaafashion.com' in url or 'westside.com' in url:
        print(f"Performing additional scrolls for {url} due to JavaScript content.")
    
    # Fetch the content using Playwright (use this for JS-rendered content)
    html, page = await fetch_with_js(url)
    if not html:
        html = fetch_html_with_requests(url)  # Fallback to requests for non-JS pages

    if html:
        soup = BeautifulSoup(html, 'html.parser')

        # Look for all links and filter by refined product URL patterns
        links = [link['href'] for link in soup.find_all('a', href=True)]
        refined_urls = refine_product_urls(links, url)

        product_urls.update(refined_urls)

        # Handle category pages and pagination if needed (for TataCliq)
        if url == "https://www.tatacliq.com/":
            print("Crawling TataCliq category pages...")
            category_links = [link['href'] for link in soup.find_all('a', href=True) if '/shop/' in link['href']]
            for category in category_links:
                category_html, _ = await fetch_with_js(category)
                if category_html:
                    category_soup = BeautifulSoup(category_html, 'html.parser')
                    category_links = [link['href'] for link in category_soup.find_all('a', href=True)]
                    refined_category_urls = refine_product_urls(category_links, category)
                    product_urls.update(refined_category_urls)

        # Handle pagination or infinite scroll
        if page:  # Ensure the page is defined (only for Playwright)
            await scroll_page(page)  # Scroll the page to load more products

    return product_urls

# Function to convert results to serializable format (convert sets to lists)
def convert_to_serializable(crawl_results):
    for key, value in crawl_results.items():
        if isinstance(value, set):
            crawl_results[key] = list(value)  # Convert set to list
    return crawl_results

# Main function to orchestrate crawling
async def main():
    domains = [
        "https://www.virgio.com/",
        "https://www.tatacliq.com/",
        "https://nykaafashion.com/",
        "https://www.westside.com/"
    ]

    # Initiate the crawling process for each domain
    tasks = [crawl_domain(domain) for domain in domains]
    results = await asyncio.gather(*tasks)

    # Display the results
    crawl_results = dict(zip(domains, results))
    print("Crawl complete. Results:", crawl_results)

    # Save results to file
    with open('crawl_results.json', 'w') as f:
        serializable_results = convert_to_serializable(crawl_results)  # Convert sets to lists
        json.dump(serializable_results, f, indent=4)

# Run the main function
if __name__ == "__main__":
    asyncio.run(main())
