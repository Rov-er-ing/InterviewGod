import pytest
from signals.mass_hiring.scorer import Scorer
from datetime import datetime, timezone, timedelta

def test_confidence_mapping():
    scorer = Scorer()
    assert scorer._get_confidence_level(85) == "High"
    assert scorer._get_confidence_level(60) == "Medium"
    assert scorer._get_confidence_level(30) == "Low"
    assert scorer._get_confidence_level(10) == "Noise"

def test_full_scoring_additive():
    config = {"trusted_domains": ["techcrunch.com"]}
    scorer = Scorer(config)
    
    # Yesterday's date for recency bonus
    yesterday = (datetime.now(timezone.utc) - timedelta(hours=12)).isoformat()
    
    article = {
        "url": "https://techcrunch.com/article",
        "published_at": yesterday,
        "parsed_data": {
            "tier1_matches": ["mass hiring"], # 25
            "tier2_matches": ["hiring", "expansion"], # 20
            "max_volume": 5000, # 15
        }
    }
    # 25 + 20 + 15 + 10 (trusted) + 10 (recency) = 80
    result = scorer.score(article)
    assert result["score"] == 80
    assert result["confidence"] == "High"
    assert "mass hiring" in result["reason"]

def test_negative_penalty():
    scorer = Scorer()
    article = {
        "parsed_data": {
            "tier1_matches": ["mass hiring"], # 25
            "negative_matches": ["layoffs"] # -15
        }
    }
    # 25 - 15 = 10
    result = scorer.score(article)
    assert result["score"] == 10
    assert result["confidence"] == "Noise"
    assert "negative signal" in result["reason"]

def test_cap_logic():
    scorer = Scorer()
    article = {
        "parsed_data": {
            "tier1_matches": ["mass hiring", "hiring spree", "bulk recruitment"], # 25*3 = 75, cap at 50
        }
    }
    # 50
    result = scorer.score(article)
    assert result["score"] == 50
    assert result["confidence"] == "Medium"
