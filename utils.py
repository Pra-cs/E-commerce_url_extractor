import re
import xml.etree.ElementTree as ET
from urllib.parse import urljoin, urlparse

PRODUCT_PATTERNS = {
    "virgio.com": [r"/p/"],
    "tatacliq.com": [r"/product/"],
    "nykaafashion.com": [r"/p/", r"/products/"],
    "westside.com": [r"/products/"]
}

# Parse the sitemap to get product URLs
def parse_sitemap(sitemap_content):
    product_urls = []
    try:
        root = ET.fromstring(sitemap_content)
        for url in root.findall(".//url/loc"):
            loc = url.text
            if loc and any(is_valid_product_url(loc, domain) for domain in PRODUCT_PATTERNS):
                product_urls.append(loc)
    except ET.ParseError:
        return []
    return product_urls

# Check if a URL matches known product patterns for the domain
def is_valid_product_url(url, domain):
    domain_key = domain.replace("www.", "").split('/')[0]
    patterns = PRODUCT_PATTERNS.get(domain_key, [])
    for pattern in patterns:
        if re.search(pattern, url):
            return True
    return False

# Normalize the URL by resolving relative paths
def normalize_url(href, base):
    if href.startswith("javascript") or href.startswith("#"):
        return None
    return urljoin(base, href)
