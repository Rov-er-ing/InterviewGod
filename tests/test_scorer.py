import pytest
from signals.mass_hiring.scorer import Scorer

def test_volume_scoring():
    scorer = Scorer()
    assert scorer._calculate_volume_score(5000) == 100
    assert scorer._calculate_volume_score(1000) == 60
    assert scorer._calculate_volume_score(100) == 20
    assert scorer._calculate_volume_score(0) == 0

def test_source_scoring():
    scorer = Scorer()
    assert scorer._calculate_source_score("tier1") == 100
    assert scorer._calculate_source_score("tier2") == 60
    assert scorer._calculate_source_score("tier3") == 20

def test_confidence_mapping():
    scorer = Scorer()
    assert scorer._get_confidence_level(85) == "High"
    assert scorer._get_confidence_level(60) == "Medium"
    assert scorer._get_confidence_level(30) == "Low"

def test_full_scoring():
    scorer = Scorer()
    article = {
        "parsed_data": {
            "max_volume": 5000,      # score 100 * 0.4 = 40
            "source_tier": "tier1",  # score 100 * 0.4 = 40
            "has_expansion_keywords": True # score 100 * 0.2 = 20
        }
    }
    # Total = 100
    result = scorer.score(article)
    assert result["score"] == 100
    assert result["confidence"] == "High"

def test_partial_scoring():
    scorer = Scorer()
    article = {
        "parsed_data": {
            "max_volume": 100,       # score 20 * 0.4 = 8
            "source_tier": "tier3",  # score 20 * 0.4 = 8
            "has_expansion_keywords": False # score 0 * 0.2 = 0
        }
    }
    # Total = 16
    result = scorer.score(article)
    assert result["score"] == 16
    assert result["confidence"] == "Low"
