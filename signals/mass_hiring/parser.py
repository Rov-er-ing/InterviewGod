import re
from utils.logger import logger
from .keywords import TIER1_KEYWORDS, TIER2_KEYWORDS, TIER3_KEYWORDS, NEGATIVE_KEYWORDS

class Parser:
    """
    Parses article text to extract mass hiring signals using regex patterns.
    """

    def __init__(self, config=None):
        self.config = config or {}
        # Patterns for hiring volumes (e.g., "5k+ hires", "10,000 engineers")
        self.volume_patterns = [
            # 10,000+ engineers, 5k roles, 500 jobs
            r'(\d{1,3}(?:,\d{3})*(?:\.\d+)?)\s*(?:k|thousand|m|million)?\+?\s*(?:open\s+)?(?:engineers|roles|jobs|people|hires|employees|vacancies|positions)',
            # hiring 5,000, expansion of 200
            r'(?:hiring|expansion of|recruiting)\s*(\d{1,3}(?:,\d{3})*(?:\.\d+)?)\s*(?:k|thousand|m|million)?',
            # 5k+ 
            r'(\d+(?:\.\d+)?)\s*k\+?\s*(?:open\s+)?(?:engineers|roles|jobs|people|hires)'
        ]

        # Tiered keywords from .keywords
        self.tier1_keywords = TIER1_KEYWORDS
        self.tier2_keywords = TIER2_KEYWORDS
        self.tier3_keywords = TIER3_KEYWORDS
        self.negative_keywords = NEGATIVE_KEYWORDS

        # Trusted domains from config or defaults
        trusted = self.config.get("trusted_domains", [])
        if not trusted:
            trusted = ['reuters.com', 'bloomberg.com', 'techcrunch.com', 'wsj.com', 'ft.com']
            
        self.source_tier_patterns = {
            "tier1": [re.escape(domain) for domain in trusted],
            "tier2": [r'indiatimes\.com', r'moneycontrol\.com', r'business-standard\.com']
        }

    def parse(self, article):
        """
        Parses an article dictionary and extracts signals.
        Returns a dictionary with extracted features.
        """
        text = article.get("raw_text", "")
        
        # 1. Extract Volumes
        volumes = self._extract_volumes(text)
        
        # 2. Check for Tiered Keywords
        tier1_matches = self._check_keywords(text, self.tier1_keywords)
        tier2_matches = self._check_keywords(text, self.tier2_keywords)
        tier3_matches = self._check_keywords(text, self.tier3_keywords)
        negative_matches = self._check_keywords(text, self.negative_keywords)
        
        # 3. Detect Source Tier (if url available)
        source_tier = self._detect_tier(article.get("url", ""))

        # Update article with parsed data
        article["parsed_data"] = {
            "max_volume": max(volumes) if volumes else 0,
            "all_volumes": volumes,
            "tier1_matches": tier1_matches,
            "tier2_matches": tier2_matches,
            "tier3_matches": tier3_matches,
            "negative_matches": negative_matches,
            "source_tier": source_tier
        }
        
        return article

    def _extract_volumes(self, text):
        """Extracts and normalizes numbers from the text."""
        volumes = []
        for pattern in self.volume_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                raw_num = match.group(1).replace(',', '')
                try:
                    num = float(raw_num)
                    # Handle "k" or "m" suffix
                    match_text = match.group(0).lower()
                    # Fix: Use re.search(r'\dk', match_text) instead of 'k' in match_text
                    if re.search(r'\dk', match_text) or 'thousand' in match_text:
                        num *= 1000
                    elif 'm' in match_text or 'million' in match_text:
                        num *= 1000000
                    
                    volumes.append(int(num))
                except ValueError:
                    continue
        return sorted(list(set(volumes)), reverse=True)

    def _check_keywords(self, text, keyword_list):
        """Checks for keywords in text and returns matches."""
        found = []
        for kw in keyword_list:
            # Use word boundaries for better matching
            pattern = r'\b' + re.escape(kw) + r'\b'
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                found.append(kw)
        return found

    def _detect_tier(self, url):
        """Detects the tier of the source domain."""
        if not url:
            return "tier3"
            
        for tier, patterns in self.source_tier_patterns.items():
            for pattern in patterns:
                if re.search(pattern, url, re.IGNORECASE):
                    return tier
        return "tier3"
