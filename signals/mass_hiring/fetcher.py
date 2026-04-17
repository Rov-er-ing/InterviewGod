import time
import random
import feedparser
import requests
from bs4 import BeautifulSoup
from urllib.parse import quote_plus
from utils.logger import logger
from datetime import datetime
import json

class Fetcher:
    """
    Handles fetching articles from RSS feeds (Google News, Bing News) 
    and falling back to full-page scraping if necessary.
    """
    
    USER_AGENTS = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (iPhone; CPU iPhone OS 17_1_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Mobile/15E148 Safari/604.1"
    ]

    def __init__(self, config=None):
        self.config = config or {}
        self.timeout = self.config.get("fetch_timeout_seconds", 15)
        self.max_articles = self.config.get("max_articles_per_company", 10)
        self.session = requests.Session()

    def get_headers(self):
        return {
            "User-Agent": random.choice(self.USER_AGENTS),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
        }

    def fetch_rss(self, company_name):
        """Fetches articles from various RSS sources for a company."""
        all_articles = []
        queries = [
            f"{company_name} hiring",
            f"{company_name} expansion jobs"
        ]
        
        sources = [
            "https://news.google.com/rss/search?q={query}",
            "https://www.bing.com/news/search?q={query}&format=RSS"
        ]

        for query in queries:
            encoded_query = quote_plus(query)
            for source_template in sources:
                url = source_template.format(query=encoded_query)
                logger.info(f"Fetching RSS from: {url}")
                
                try:
                    articles = self._parse_feed(url, company_name)
                    all_articles.extend(articles)
                    if len(all_articles) >= self.max_articles:
                        break
                except Exception as e:
                    logger.warning(f"Failed to fetch RSS from {url}: {e}")
                
                # Small delay between sources to avoid rate limiting
                time.sleep(random.uniform(1.0, 2.0))
            
            if len(all_articles) >= self.max_articles:
                break
                
        return all_articles[:self.max_articles]

    def _parse_feed(self, url, company_name):
        """Parses an RSS feed and extracts article metadata."""
        # Using requests first for better header control, then passing to feedparser
        response = self._request_with_retry(url)
        if not response:
            return []
            
        feed = feedparser.parse(response.content)
        articles = []
        
        for entry in feed.entries:
            article = {
                "company_name": company_name,
                "title": entry.get("title", ""),
                "url": entry.get("link", ""),
                "published_at": entry.get("published", datetime.now().isoformat()),
                "summary": entry.get("summary", ""),
                "raw_text": f"{entry.get('title', '')} {entry.get('summary', '')}"
            }
            
            # If summary is too short, mark for potential full-page fetch
            if len(article["summary"]) < 200:
                article["needs_full_fetch"] = True
            else:
                article["needs_full_fetch"] = False
                
            articles.append(article)
            
        return articles

    def fetch_full_content(self, url):
        """Attempts to scrape the full text of an article."""
        logger.info(f"Attempting full-page fetch for: {url}")
        response = self._request_with_retry(url)
        if not response:
            return ""
            
        try:
            soup = BeautifulSoup(response.content, "lxml")
            # Remove script and style elements
            for script in soup(["script", "style"]):
                script.decompose()
            
            # Get text
            text = soup.get_text(separator=' ')
            # Clean up whitespace
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            text = '\n'.join(chunk for chunk in chunks if chunk)
            
            return text
        except Exception as e:
            logger.warning(f"Failed to parse full page {url}: {e}")
            return ""

    def _request_with_retry(self, url, max_retries=3):
        """Helper to perform requests with exponential backoff."""
        for i in range(max_retries):
            try:
                response = self.session.get(url, headers=self.get_headers(), timeout=self.timeout)
                response.raise_for_status()
                return response
            except requests.exceptions.RequestException as e:
                wait_time = (2 ** i) + random.uniform(0, 1)
                logger.warning(f"Request failed ({e}), retrying in {wait_time:.2f}s... ({i+1}/{max_retries})")
                time.sleep(wait_time)
                
        return None

    def fetch(self, company_name):
        """Main entry point: fetch RSS, then supplement with full-page text if needed."""
        articles = self.fetch_rss(company_name)
        
        for article in articles:
            if article.get("needs_full_fetch"):
                full_text = self.fetch_full_content(article["url"])
                if full_text:
                    article["raw_text"] = f"{article['title']} {full_text}"
                    logger.info(f"Supplemented article text for {article['url']} (length: {len(full_text)})")
            
            # Clean up internal flags before returning
            article.pop("needs_full_fetch", None)
            
        return articles
