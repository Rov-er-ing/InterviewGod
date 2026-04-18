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
        try:
            if os.path.exists(path):
                with open(path, 'r') as f:
                    return json.load(f)
            return []
        except Exception as e:
            logger.error(f"Failed to load companies from {path}: {e}")
            return []

    def process_company(self, company):
        """Processes a single company to detect hiring signals."""
        name = company.get("name")
        logger.info(f"--- Starting processing for {name} ---")
        
        try:
            # 1. Fetch
            articles = self.fetcher.fetch(name)
            logger.info(f"Found {len(articles)} articles for {name}")
            
            processed_signals = []
            
            for article in articles:
                # 2. Parse
                parsed_article = self.parser.parse(article)
                
                # 3. Score
                scored_article = self.scorer.score(parsed_article)
                
                # Only keep signals with at least the configured threshold
                threshold = self.config.get("score_threshold", 50)
                if scored_article["score"] >= threshold:
                    processed_signals.append(scored_article)
            
            return processed_signals
            
        except Exception as e:
            logger.error(f"Error processing company {name}: {e}")
            return []

    def run(self):
        """Runs the detection pipeline for all target companies."""
        logger.info("Starting Signal Detection Pipeline")
        all_signals = []
        
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            future_to_company = {executor.submit(self.process_company, company): company for company in self.companies}
            
            for future in as_completed(future_to_company):
                company = future_to_company[future]
                try:
                    signals = future.result()
                    all_signals.extend(signals)
                except Exception as e:
                    logger.error(f"Company {company.get('name')} generated an exception: {e}")
        
        # 4. Storage
        self.storage.save_signals(all_signals)
        logger.info(f"Pipeline complete. Total signals detected: {len(all_signals)}")

    def _save_results(self, signals):
        # Deprecated: Handled by self.storage.save_signals
        pass

if __name__ == "__main__":
    from signals.orchestrator import Orchestrator
    orchestrator = Orchestrator()
    orchestrator.run()
