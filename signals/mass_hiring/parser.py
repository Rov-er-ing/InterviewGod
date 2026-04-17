import re
from utils.logger import logger

class Parser:
    """
    Parses article text to extract mass hiring signals using regex patterns.
    """

    def __init__(self):
        # Patterns for hiring volumes (e.g., "5k+ hires", "10,000 engineers")
        self.volume_patterns = [
            # 10,000+ engineers, 5k roles, 500 jobs
            r'(\d{1,3}(?:,\d{3})*(?:\.\d+)?)\s*(?:k|thousand|m|million)?\+?\s*(?:open\s+)?(?:engineers|roles|jobs|people|hires|employees|vacancies|positions)',
            # hiring 5,000, expansion of 200
            r'(?:hiring|expansion of|recruiting)\s*(\d{1,3}(?:,\d{3})*(?:\.\d+)?)\s*(?:k|thousand|m|million)?',
            # 5k+ 
            r'(\d+(?:\.\d+)?)\s*k\+?\s*(?:open\s+)?(?:engineers|roles|jobs|people|hires)'
        ]

        # Patterns for expansion signals
        self.expansion_keywords = [
            r'mass hiring',
            r'ramp up',
            r'scaling up',
            r'major expansion',
            r'aggressive hiring',
            r'global expansion',
            r'hiring spree',
            r'new (?:office|hub|center|campus)'
        ]

        # Trusted domains (already handled in scorer, but useful for parser to know context)
        self.source_tier_patterns = {
            "tier1": [r'reuters\.com', r'bloomberg\.com', r'techcrunch\.com', r'wsj\.com', r'ft\.com'],
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
        
        # 2. Check for Expansion Keywords
        expansion_signals = self._check_expansion(text)
        
        # 3. Detect Source Tier (if url available)
        source_tier = self._detect_tier(article.get("url", ""))

        # Update article with parsed data
        article["parsed_data"] = {
            "max_volume": max(volumes) if volumes else 0,
            "all_volumes": volumes,
            "has_expansion_keywords": len(expansion_signals) > 0,
            "expansion_keywords_found": expansion_signals,
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
                    if 'k' in match_text or 'thousand' in match_text:
                        num *= 1000
                    elif 'm' in match_text or 'million' in match_text:
                        num *= 1000000
                    
                    volumes.append(int(num))
                except ValueError:
                    continue
        return sorted(list(set(volumes)), reverse=True)

    def _check_expansion(self, text):
        """Checks for expansion-related keywords."""
        found = []
        for kw in self.expansion_keywords:
            match = re.search(kw, text, re.IGNORECASE)
            if match:
                found.append(match.group(0))
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
