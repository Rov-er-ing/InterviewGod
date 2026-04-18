from utils.logger import logger
from datetime import datetime
from dateutil import parser as date_parser

class Scorer:
    """
    Implements heuristic scoring logic to determine the confidence level 
    of a mass hiring signal using the PRD §3.6 additive formula.
    """

    def __init__(self, config=None):
        self.config = config or {}
        self.score_threshold = self.config.get("score_threshold", 50)
        self.trusted_domains = self.config.get("trusted_domains", [])

    def score(self, article):
        """
        Calculates a score for an article based on the PRD additive formula.
        Returns the article with score, confidence level, and reason.
        """
        parsed_data = article.get("parsed_data", {})
        if not parsed_data:
            article["score"] = 0
            article["confidence"] = "Low"
            article["reason"] = "No parsed data available."
            return article

        base_score = 0
        reasons = []

        # 1. Keyword tier contributions (additive)
        t1_count = len(parsed_data.get("tier1_matches", []))
        t2_count = len(parsed_data.get("tier2_matches", []))
        t3_count = len(parsed_data.get("tier3_matches", []))

        t1_score = min(t1_count * 25, 50)
        t2_score = min(t2_count * 10, 30)
        t3_score = min(t3_count * 5, 10)

        base_score += t1_score
        base_score += t2_score
        base_score += t3_score

        if t1_count > 0:
            reasons.append(f"{t1_count} Tier-1 keywords matched ({', '.join(parsed_data['tier1_matches'])})")
        if t2_count > 0:
            reasons.append(f"{t2_count} Tier-2 keywords matched")

        # 2. Numeric signal bonus
        max_volume = parsed_data.get("max_volume", 0)
        volume_bonus = 0
        if max_volume >= 10000:
            volume_bonus = 20
        elif max_volume >= 1000:
            volume_bonus = 15
        elif max_volume >= 500:
            volume_bonus = 10
        elif max_volume >= 100:
            volume_bonus = 5
        
        base_score += volume_bonus
        if volume_bonus > 0:
            reasons.append(f"numeric signal of {max_volume} hires found")

        # 3. Source credibility bonus
        url = article.get("url", "").lower()
        source_bonus = 0
        for domain in self.trusted_domains:
            if domain.lower() in url:
                source_bonus = 10
                break
        
        base_score += source_bonus
        if source_bonus > 0:
            reasons.append("trusted source detected")

        # 4. Recency bonus
        published_at = article.get("published_at")
        recency_bonus = 0
        if published_at:
            try:
                pub_date = date_parser.parse(published_at)
                if pub_date.tzinfo is None:
                    now = datetime.now()
                else:
                    from datetime import timezone
                    now = datetime.now(timezone.utc)
                
                diff = now - pub_date
                hours = diff.total_seconds() / 3600
                
                if hours <= 24:
                    recency_bonus = 10
                elif hours <= 168: # 7 days
                    recency_bonus = 5
            except Exception as e:
                logger.warning(f"Failed to parse date {published_at}: {e}")
        
        base_score += recency_bonus
        if recency_bonus == 10:
            reasons.append("published within 24h")
        elif recency_bonus == 5:
            reasons.append("published within 7d")

        # 5. Negative signal penalty
        neg_count = len(parsed_data.get("negative_matches", []))
        penalty = neg_count * 15
        base_score -= penalty
        if neg_count > 0:
            reasons.append(f"negative signal detected ({', '.join(parsed_data['negative_matches'])})")

        # Final clamping
        final_score = max(0, min(base_score, 100))
        article["score"] = round(final_score, 2)
        article["confidence"] = self._get_confidence_level(final_score)
        
        # Reason generation
        article["reason"] = f"Hiring signal detected: {'; '.join(reasons)}." if reasons else "Hiring signal detected with low confidence."

        logger.info(f"Scored article {article.get('url')} - Score: {article['score']}, Confidence: {article['confidence']}")
        
        return article

    def _get_confidence_level(self, score):
        """Maps numerical score to categorical confidence level."""
        if score >= 80:
            return "High"
        elif score >= 50:
            return "Medium"
        elif score >= 20:
            return "Low"
        return "Noise"
