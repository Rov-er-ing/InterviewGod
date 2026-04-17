from utils.logger import logger

class Scorer:
    """
    Implements heuristic scoring logic to determine the confidence level 
    of a mass hiring signal.
    """

    def __init__(self, config=None):
        self.config = config or {}
        self.thresholds = self.config.get("scoring", {}).get("thresholds", {
            "high": 80,
            "medium": 50
        })
        
        # Weights from PRD 3.6
        self.weights = {
            "volume": 0.4,
            "source": 0.4,
            "keywords": 0.2
        }

    def score(self, article):
        """
        Calculates a score for an article based on parsed data.
        Returns the article with score and confidence level.
        """
        parsed_data = article.get("parsed_data", {})
        if not parsed_data:
            article["score"] = 0
            article["confidence"] = "Low"
            return article

        # 1. Volume Score (0-100)
        # 5000+ = 100, 1000 = 60, 100 = 20, etc.
        volume = parsed_data.get("max_volume", 0)
        volume_score = self._calculate_volume_score(volume)

        # 2. Source Tier Score (0-100)
        # Tier 1 = 100, Tier 2 = 60, Tier 3 = 20
        tier = parsed_data.get("source_tier", "tier3")
        source_score = self._calculate_source_score(tier)

        # 3. Expansion Keyword Score (0-100)
        # Has keywords = 100, No keywords = 0
        has_keywords = parsed_data.get("has_expansion_keywords", False)
        keyword_score = 100 if has_keywords else 0

        # Weighted Total
        total_score = (
            (volume_score * self.weights["volume"]) +
            (source_score * self.weights["source"]) +
            (keyword_score * self.weights["keywords"])
        )

        article["score"] = round(total_score, 2)
        article["confidence"] = self._get_confidence_level(total_score)
        
        logger.info(f"Scored article {article.get('url')} - Score: {article['score']}, Confidence: {article['confidence']}")
        
        return article

    def _calculate_volume_score(self, volume):
        """Normalizes hiring volume to a 0-100 score."""
        if volume >= 5000:
            return 100
        elif volume >= 1000:
            return 60 + (volume - 1000) * (40 / 4000)
        elif volume >= 100:
            return 20 + (volume - 100) * (40 / 900)
        elif volume > 0:
            return (volume / 100) * 20
        return 0

    def _calculate_source_score(self, tier):
        """Maps source tier to a 0-100 score."""
        scores = {
            "tier1": 100,
            "tier2": 60,
            "tier3": 20
        }
        return scores.get(tier, 20)

    def _get_confidence_level(self, score):
        """Maps numerical score to categorical confidence level."""
        if score >= self.thresholds["high"]:
            return "High"
        elif score >= self.thresholds["medium"]:
            return "Medium"
        return "Low"
