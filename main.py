import argparse
import sys
from signals.orchestrator import Orchestrator
from utils.logger import logger

def main():
    parser = argparse.ArgumentParser(description="Signal Detection System — Mass Hiring / Scale-Up Signal Detector")
    parser.add_argument("--config", default="config.yaml", help="Path to config YAML")
    parser.add_argument("--companies", help="Path to companies JSON")
    parser.add_argument("--threshold", type=int, help="Minimum score to emit a signal")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose logging")
    
    args = parser.parse_args()
    
    try:
        orchestrator = Orchestrator(config_path=args.config)
        
        # Override config if CLI args provided
        if args.companies:
            orchestrator.config["companies_file"] = args.companies
            orchestrator.companies = orchestrator._load_companies()
            
        if args.threshold is not None:
            orchestrator.config["score_threshold"] = args.threshold
            
        orchestrator.run()
        
    except Exception as e:
        logger.error(f"Pipeline failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
