import yaml
import json
import os
from concurrent.futures import ThreadPoolExecutor, as_completed
from .mass_hiring.fetcher import Fetcher
from .mass_hiring.parser import Parser
from .mass_hiring.scorer import Scorer
from utils.storage import Storage
from utils.logger import logger

class Orchestrator:
    """
    Main entry point for the Signal Detection System.
    Coordinates fetching, parsing, scoring, and storage.
    """

    def __init__(self, config_path="config.yaml"):
        self.config_path = config_path
        self.config = self._load_config(config_path)
        self.fetcher = Fetcher(self.config)
        self.parser = Parser(self.config)
        self.scorer = Scorer(self.config)
        self.storage = Storage()
        self.companies = self._load_companies()
        self.max_workers = self.config.get("concurrency_workers", 4)

    def _load_config(self, path):
        try:
            with open(path, 'r') as f:
                return yaml.safe_load(f)
        except Exception as e:
            logger.error(f"Failed to load config from {path}: {e}")
            return {}

    def _load_companies(self):
        path = self.config.get("companies_file", "data/companies.json")
        # Resolve relative path based on the config file's location if it's not absolute
        if not os.path.isabs(path):
            config_dir = os.path.dirname(os.path.abspath(self.config_path))
            path = os.path.join(config_dir, path)
            
        try:
            if os.path.exists(path):
                with open(path, 'r') as f:
                    return json.load(f)
            return []
        except Exception as e:
            logger.error(f"Failed to load companies from {path}: {e}")
            return []

    def process_company(self, company, show_noise=False):
        """Pipeline for a single company. Returns (signals, total_articles_fetched)"""
        name = company.get("name")
        logger.info(f"Processing signals for: {name}")
        
        try:
            # 1. Fetch
            articles = self.fetcher.fetch(name)
            total_fetched = len(articles)
            
            # 2. Parse & 3. Score
            signals = []
            for article in articles:
                parsed_article = self.parser.parse(article)
                score_data = self.scorer.score(parsed_article)
                
                threshold = self.config.get("score_threshold", 50)
                if score_data["score"] >= threshold or show_noise:
                    scored_article = {**parsed_article, **score_data}
                    signals.append(scored_article)
            
            return signals, total_fetched
        except Exception as e:
            logger.error(f"Error processing company {name}: {e}")
            return [], 0

    def run(self, show_noise=False):
        """Runs the detection pipeline. Returns (all_signals, total_fetched)"""
        logger.info("Starting Signal Detection Pipeline")
        all_signals = []
        total_fetched = 0
        
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            future_to_company = {executor.submit(self.process_company, company, show_noise): company for company in self.companies}
            
            for future in as_completed(future_to_company):
                company = future_to_company[future]
                try:
                    signals, fetched_count = future.result()
                    all_signals.extend(signals)
                    total_fetched += fetched_count
                except Exception as e:
                    logger.error(f"Company {company.get('name')} generated an exception: {e}")
        
        # 4. Storage
        self.storage.save_signals(all_signals)
        logger.info(f"Pipeline complete. Detected {len(all_signals)} signals from {total_fetched} articles.")
        return all_signals, total_fetched

if __name__ == "__main__":
    orchestrator = Orchestrator()
    orchestrator.run()
