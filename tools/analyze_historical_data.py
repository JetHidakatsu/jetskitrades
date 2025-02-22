#!/usr/bin/env python3
"""Tool to analyze and visualize historical trading data"""

import json
import argparse
from datetime import datetime
from pathlib import Path
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Dict, List, Any

class HistoricalDataAnalyzer:
    """Analyzer for historical trading data"""
    
    def __init__(self, data_path: Path):
        self.data_path = data_path
        self.data = self._load_data()
        self.events_df = self._create_events_dataframe()
        self.pools_df = self._create_pools_dataframe()
        
    def _load_data(self) -> Dict[str, Any]:
        """Load historical data from file"""
        with open(self.data_path) as f:
            return json.load(f)
            
    def _create_events_dataframe(self) -> pd.DataFrame:
        """Convert events to DataFrame"""
        events = pd.DataFrame(self.data["events"])
        events["timestamp"] = pd.to_datetime(events["timestamp"])
        return events
        
    def _create_pools_dataframe(self) -> pd.DataFrame:
        """Create DataFrame of pool data"""
        pool_data = []
        for event in self.data["events"]:
            if event["type"] == "pool_creation":
                pool_data.append({
                    "pool_id": event["pool_id"],
                    "creation_time": pd.to_datetime(event["timestamp"]),
                    **event["pool_data"]
                })
        return pd.DataFrame(pool_data)
        
    def analyze(self, output_dir: Path):
        """Run complete analysis"""
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Generate all analyses
        self.analyze_price_movements(output_dir)
        self.analyze_liquidity_changes(output_dir)
        self.analyze_pool_creation_patterns(output_dir)
        self.analyze_trading_metrics(output_dir)
        self.generate_summary_report(output_dir)
        
    def analyze_price_movements(self, output_dir: Path):
        """Analyze price movements"""
        price_updates = self.events_df[self.events_df["type"] == "price_update"]
        
        # Price movement over time
        plt.figure(figsize=(12, 6))
        for pool_id in price_updates["pool_id"].unique():
            pool_data = price_updates[price_updates["pool_id"] == pool_id]
            plt.plot(pool_data["timestamp"], pool_data["price"], label=pool_id)
        plt.title("Price Movement Over Time")
        plt.xlabel("Time")
        plt.ylabel("Price")
        plt.legend()
        plt.savefig(output_dir / "price_movements.png")
        plt.close()
        
        # Price change distribution
        price_changes = []
        for pool_id in price_updates["pool_id"].unique():
            pool_data = price_updates[price_updates["pool_id"] == pool_id]
            changes = pool_data["price"].pct_change().dropna()
            price_changes.extend(changes)
            
        plt.figure(figsize=(10, 6))
        sns.histplot(price_changes, bins=50)
        plt.title("Distribution of Price Changes")
        plt.xlabel("Percentage Change")
        plt.ylabel("Count")
        plt.savefig(output_dir / "price_change_distribution.png")
        plt.close()
        
    def analyze_liquidity_changes(self, output_dir: Path):
        """Analyze liquidity changes"""
        price_updates = self.events_df[self.events_df["type"] == "price_update"]
        
        # Liquidity changes over time
        plt.figure(figsize=(12, 6))
        for pool_id in price_updates["pool_id"].unique():
            pool_data = price_updates[price_updates["pool_id"] == pool_id]
            plt.plot(pool_data["timestamp"], 
                    pool_data["liquidity_change"].cumsum(),
                    label=pool_id)
        plt.title("Cumulative Liquidity Changes")
        plt.xlabel("Time")
        plt.ylabel("Net Liquidity Change")
        plt.legend()
        plt.savefig(output_dir / "liquidity_changes.png")
        plt.close()
        
        # Initial liquidity distribution
        plt.figure(figsize=(10, 6))
        sns.histplot(self.pools_df["initial_liquidity"], bins=20)
        plt.title("Distribution of Initial Liquidity")
        plt.xlabel("Initial Liquidity")
        plt.ylabel("Count")
        plt.savefig(output_dir / "initial_liquidity_distribution.png")
        plt.close()
        
    def analyze_pool_creation_patterns(self, output_dir: Path):
        """Analyze pool creation patterns"""
        pool_creations = self.events_df[self.events_df["type"] == "pool_creation"]
        
        # Pool creations over time
        plt.figure(figsize=(12, 6))
        creation_times = pd.to_datetime(pool_creations["timestamp"])
        plt.hist(creation_times, bins=20)
        plt.title("Pool Creation Timeline")
        plt.xlabel("Time")
        plt.ylabel("Number of Pools Created")
        plt.savefig(output_dir / "pool_creation_timeline.png")
        plt.close()
        
        # Creator analysis
        plt.figure(figsize=(10, 6))
        creator_counts = self.pools_df["creator_address"].value_counts()
        creator_counts.plot(kind="bar")
        plt.title("Pool Creations by Creator")
        plt.xlabel("Creator Address")
        plt.ylabel("Number of Pools")
        plt.tight_layout()
        plt.savefig(output_dir / "creator_analysis.png")
        plt.close()
        
    def analyze_trading_metrics(self, output_dir: Path):
        """Analyze trading metrics"""
        price_updates = self.events_df[self.events_df["type"] == "price_update"]
        
        # Volume analysis
        plt.figure(figsize=(12, 6))
        for pool_id in price_updates["pool_id"].unique():
            pool_data = price_updates[price_updates["pool_id"] == pool_id]
            plt.plot(pool_data["timestamp"], 
                    pool_data["volume"].cumsum(),
                    label=pool_id)
        plt.title("Cumulative Trading Volume")
        plt.xlabel("Time")
        plt.ylabel("Volume")
        plt.legend()
        plt.savefig(output_dir / "trading_volume.png")
        plt.close()
        
        # Price impact analysis
        plt.figure(figsize=(10, 6))
        sns.boxplot(data=self.pools_df, y="price_impact")
        plt.title("Price Impact Distribution")
        plt.ylabel("Price Impact")
        plt.savefig(output_dir / "price_impact_distribution.png")
        plt.close()
        
    def generate_summary_report(self, output_dir: Path):
        """Generate summary report"""
        report = {
            "dataset_summary": {
                "timeframe": self.data["metadata"]["timeframe"],
                "total_pools": len(self.pools_df),
                "total_events": len(self.events_df),
                "unique_creators": len(self.pools_df["creator_address"].unique())
            },
            "price_metrics": {
                "avg_price_change": self.events_df[
                    self.events_df["type"] == "price_update"
                ]["price"].pct_change().mean(),
                "price_volatility": self.events_df[
                    self.events_df["type"] == "price_update"
                ]["price"].std()
            },
            "liquidity_metrics": {
                "avg_initial_liquidity": self.pools_df["initial_liquidity"].mean(),
                "total_liquidity_change": self.events_df[
                    self.events_df["type"] == "price_update"
                ]["liquidity_change"].sum()
            },
            "trading_metrics": {
                "total_volume": self.events_df[
                    self.events_df["type"] == "price_update"
                ]["volume"].sum(),
                "avg_price_impact": self.pools_df["price_impact"].mean()
            }
        }
        
        # Save report
        with open(output_dir / "analysis_summary.json", 'w') as f:
            json.dump(report, f, indent=2)
            
        # Generate markdown report
        markdown = f"""# Historical Data Analysis Summary

## Dataset Overview
- Timeframe: {report['dataset_summary']['timeframe']}
- Total Pools: {report['dataset_summary']['total_pools']}
- Total Events: {report['dataset_summary']['total_events']}
- Unique Creators: {report['dataset_summary']['unique_creators']}

## Price Analysis
- Average Price Change: {report['price_metrics']['avg_price_change']:.2%}
- Price Volatility: {report['price_metrics']['price_volatility']:.4f}

## Liquidity Analysis
- Average Initial Liquidity: {report['liquidity_metrics']['avg_initial_liquidity']:,.0f}
- Total Liquidity Change: {report['liquidity_metrics']['total_liquidity_change']:,.0f}

## Trading Metrics
- Total Volume: {report['trading_metrics']['total_volume']:,.0f}
- Average Price Impact: {report['trading_metrics']['avg_price_impact']:.2%}

## Generated Visualizations
- Price Movements (`price_movements.png`)
- Price Change Distribution (`price_change_distribution.png`)
- Liquidity Changes (`liquidity_changes.png`)
- Initial Liquidity Distribution (`initial_liquidity_distribution.png`)
- Pool Creation Timeline (`pool_creation_timeline.png`)
- Creator Analysis (`creator_analysis.png`)
- Trading Volume (`trading_volume.png`)
- Price Impact Distribution (`price_impact_distribution.png`)
"""
        
        with open(output_dir / "analysis_summary.md", 'w') as f:
            f.write(markdown)

def main():
    parser = argparse.ArgumentParser(description='Analyze historical trading data')
    
    parser.add_argument('--input', type=str, required=True,
                       help='Input data file path')
    parser.add_argument('--output-dir', type=str, default='analysis_output',
                       help='Output directory for analysis')
    
    args = parser.parse_args()
    
    analyzer = HistoricalDataAnalyzer(Path(args.input))
    analyzer.analyze(Path(args.output_dir))
    
    print(f"Analysis complete. Results saved to: {args.output_dir}")

if __name__ == '__main__':
    main()
