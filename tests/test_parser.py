import pytest
from signals.mass_hiring.parser import Parser

def test_extract_volumes():
    parser = Parser()
    text = "Google is hiring 5,000 engineers in India. Another report says they have 2k open roles."
    volumes = parser._extract_volumes(text)
    assert 5000 in volumes
    assert 2000 in volumes
    assert len(volumes) == 2

def test_extract_million_volumes():
    parser = Parser()
    text = "The government plans to create 1 million jobs this year."
    volumes = parser._extract_volumes(text)
    assert 1000000 in volumes

def test_tiered_keywords():
    parser = Parser()
    text = "Amazon announces a hiring spree for its new office in Hyderabad. However, they might freeze hiring later."
    result = parser.parse({"raw_text": text})
    data = result["parsed_data"]
    
    assert "hiring spree" in data["tier1_matches"]
    assert "new office" in data["tier2_matches"]
    assert "freeze hiring" in data["negative_matches"]

def test_detect_tier():
    config = {"trusted_domains": ["reuters.com", "bloomberg.com"]}
    parser = Parser(config)
    assert parser._detect_tier("https://www.reuters.com/business/tech") == "tier1"
    assert parser._detect_tier("https://www.moneycontrol.com/news") == "tier2"
    assert parser._detect_tier("https://random-blog.com/post") == "tier3"

def test_parse_article():
    parser = Parser()
    article = {
        "raw_text": "Microsoft is planning a mass hiring of 10k people for its expansion.",
        "url": "https://techcrunch.com/article"
    }
    result = parser.parse(article)
    data = result["parsed_data"]
    assert data["max_volume"] == 10000
    assert len(data["tier1_matches"]) > 0
    assert data["source_tier"] == "tier1"
