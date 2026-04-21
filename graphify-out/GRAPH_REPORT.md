# Graph Report - C:\Users\Shiti\OneDrive\ドキュメント\task2 , pyhton  (2026-04-19)

## Corpus Check
- 16 files · ~5,104 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 81 nodes · 134 edges · 13 communities detected
- Extraction: 62% EXTRACTED · 38% INFERRED · 0% AMBIGUOUS · INFERRED: 51 edges (avg confidence: 0.68)
- Token cost: 0 input · 0 output

## Community Hubs (Navigation)
- [[_COMMUNITY_Community 0|Community 0]]
- [[_COMMUNITY_Community 1|Community 1]]
- [[_COMMUNITY_Community 2|Community 2]]
- [[_COMMUNITY_Community 3|Community 3]]
- [[_COMMUNITY_Community 4|Community 4]]
- [[_COMMUNITY_Community 5|Community 5]]
- [[_COMMUNITY_Community 6|Community 6]]
- [[_COMMUNITY_Community 7|Community 7]]
- [[_COMMUNITY_Community 8|Community 8]]
- [[_COMMUNITY_Community 9|Community 9]]
- [[_COMMUNITY_Community 10|Community 10]]
- [[_COMMUNITY_Community 11|Community 11]]
- [[_COMMUNITY_Community 12|Community 12]]

## God Nodes (most connected - your core abstractions)
1. `Orchestrator` - 17 edges
2. `Parser` - 17 edges
3. `Fetcher` - 14 edges
4. `Scorer` - 14 edges
5. `Storage` - 13 edges
6. `Processes a single company to detect hiring signals.` - 6 edges
7. `Runs the detection pipeline for all target companies.` - 6 edges
8. `Main entry point for the Signal Detection System.     Coordinates fetching, pars` - 5 edges
9. `main()` - 4 edges
10. `test_extract_volumes()` - 3 edges

## Surprising Connections (you probably didn't know these)
- `Orchestrator` --uses--> `Fetcher`  [INFERRED]
  C:\Users\Shiti\OneDrive\ドキュメント\task2 , pyhton\signals\orchestrator.py → C:\Users\Shiti\OneDrive\ドキュメント\task2 , pyhton\signals\mass_hiring\fetcher.py
- `Orchestrator` --uses--> `Parser`  [INFERRED]
  C:\Users\Shiti\OneDrive\ドキュメント\task2 , pyhton\signals\orchestrator.py → C:\Users\Shiti\OneDrive\ドキュメント\task2 , pyhton\signals\mass_hiring\parser.py
- `Orchestrator` --uses--> `Scorer`  [INFERRED]
  C:\Users\Shiti\OneDrive\ドキュメント\task2 , pyhton\signals\orchestrator.py → C:\Users\Shiti\OneDrive\ドキュメント\task2 , pyhton\signals\mass_hiring\scorer.py
- `Orchestrator` --uses--> `Storage`  [INFERRED]
  C:\Users\Shiti\OneDrive\ドキュメント\task2 , pyhton\signals\orchestrator.py → C:\Users\Shiti\OneDrive\ドキュメント\task2 , pyhton\utils\storage.py
- `Main entry point for the Signal Detection System.     Coordinates fetching, pars` --uses--> `Parser`  [INFERRED]
  C:\Users\Shiti\OneDrive\ドキュメント\task2 , pyhton\signals\orchestrator.py → C:\Users\Shiti\OneDrive\ドキュメント\task2 , pyhton\signals\mass_hiring\parser.py

## Communities

### Community 0 - "Community 0"
Cohesion: 0.21
Nodes (11): Parser, Detects the tier of the source domain., Parses an article dictionary and extracts signals.         Returns a dictionary, Parses article text to extract mass hiring signals using regex patterns., Extracts and normalizes numbers from the text., Checks for keywords in text and returns matches., test_detect_tier(), test_extract_million_volumes() (+3 more)

### Community 1 - "Community 1"
Cohesion: 0.19
Nodes (8): Fetcher, Handles fetching articles from RSS feeds (Google News, Bing News)      and falli, Helper to perform requests with exponential backoff., Main entry point: fetch RSS, then supplement with full-page text if needed., Fetches articles from various RSS sources for a company., Parses an RSS feed and extracts article metadata., Attempts to scrape the full text of an article., Main entry point for the Signal Detection System.     Coordinates fetching, pars

### Community 2 - "Community 2"
Cohesion: 0.29
Nodes (8): Maps numerical score to categorical confidence level., Calculates a score for an article based on the PRD additive formula.         Ret, Implements heuristic scoring logic to determine the confidence level      of a m, Scorer, test_cap_logic(), test_confidence_mapping(), test_full_scoring_additive(), test_negative_penalty()

### Community 3 - "Community 3"
Cohesion: 0.21
Nodes (5): Initializes the SQLite database schema., Saves a list of signal dictionaries to both SQLite and JSON., Handles persistence of detected signals using SQLite and JSON., Retrieves all stored signals from the database., Storage

### Community 4 - "Community 4"
Cohesion: 0.31
Nodes (4): main(), Orchestrator, Processes a single company to detect hiring signals., Runs the detection pipeline for all target companies.

### Community 5 - "Community 5"
Cohesion: 0.4
Nodes (0): 

### Community 6 - "Community 6"
Cohesion: 0.67
Nodes (2): Sets up a structured logger that outputs to both console and file., setup_logger()

### Community 7 - "Community 7"
Cohesion: 1.0
Nodes (0): 

### Community 8 - "Community 8"
Cohesion: 1.0
Nodes (0): 

### Community 9 - "Community 9"
Cohesion: 1.0
Nodes (0): 

### Community 10 - "Community 10"
Cohesion: 1.0
Nodes (0): 

### Community 11 - "Community 11"
Cohesion: 1.0
Nodes (0): 

### Community 12 - "Community 12"
Cohesion: 1.0
Nodes (0): 

## Knowledge Gaps
- **19 isolated node(s):** `Handles fetching articles from RSS feeds (Google News, Bing News)      and falli`, `Fetches articles from various RSS sources for a company.`, `Parses an RSS feed and extracts article metadata.`, `Attempts to scrape the full text of an article.`, `Helper to perform requests with exponential backoff.` (+14 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **Thin community `Community 7`** (1 nodes): `api.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 8`** (1 nodes): `__init__.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 9`** (1 nodes): `__init__.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 10`** (1 nodes): `http.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 11`** (1 nodes): `text.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 12`** (1 nodes): `__init__.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Parser` connect `Community 0` to `Community 1`, `Community 4`, `Community 5`?**
  _High betweenness centrality (0.241) - this node is a cross-community bridge._
- **Why does `Storage` connect `Community 3` to `Community 1`, `Community 4`?**
  _High betweenness centrality (0.210) - this node is a cross-community bridge._
- **Why does `Fetcher` connect `Community 1` to `Community 4`, `Community 5`?**
  _High betweenness centrality (0.199) - this node is a cross-community bridge._
- **Are the 9 inferred relationships involving `Orchestrator` (e.g. with `Main entry point for the Signal Detection System.     Coordinates fetching, pars` and `Fetcher`) actually correct?**
  _`Orchestrator` has 9 INFERRED edges - model-reasoned connections that need verification._
- **Are the 10 inferred relationships involving `Parser` (e.g. with `Orchestrator` and `Main entry point for the Signal Detection System.     Coordinates fetching, pars`) actually correct?**
  _`Parser` has 10 INFERRED edges - model-reasoned connections that need verification._
- **Are the 5 inferred relationships involving `Fetcher` (e.g. with `Orchestrator` and `Main entry point for the Signal Detection System.     Coordinates fetching, pars`) actually correct?**
  _`Fetcher` has 5 INFERRED edges - model-reasoned connections that need verification._
- **Are the 9 inferred relationships involving `Scorer` (e.g. with `Orchestrator` and `Main entry point for the Signal Detection System.     Coordinates fetching, pars`) actually correct?**
  _`Scorer` has 9 INFERRED edges - model-reasoned connections that need verification._