#!/usr/bin/env python3
"""Performance analysis and visualization utility"""

import argparse
import logging
from pathlib import Path
import json
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import plotly.graph_objects as go
from plotly.subplots import make_subplots

class PerformanceAnalyzer:
    """Analyze and visualize trading performance"""
    
    def __init__(self, data_dir: Path):
        self.data_dir = data_dir
        self.logger = logging.getLogger(__name__)
        
        # Load data
        self.trades = self._load_trades()
        self.metrics = self._load_metrics()
        self.equity_curve = self._load_equity_curve()
        
    def analyze_performance(self) -> Dict:
        """Analyze overall performance metrics"""
        try:
            if not self.trades:
                return self._get_default_metrics()
                
            df = pd.DataFrame(self.trades)
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            df['duration'] = pd.to_timedelta(df['duration'])
            
            # Calculate metrics
            total_trades = len(df)
            winning_trades = len(df[df['profit'] > 0])
            total_profit = df['profit'].sum()
            
            # Calculate returns
            df['return'] = df['profit'] / df['size']
            avg_return = df['return'].mean()
            std_return = df['return'].std()
            
            # Calculate Sharpe ratio (assuming risk-free rate of 1%)
            risk_free_rate = 0.01
            sharpe = (avg_return - risk_free_rate) / std_return if std_return != 0 else 0
            
            # Calculate drawdown
            cumulative_returns = (1 + df['return']).cumprod()
            rolling_max = cumulative_returns.expanding().max()
            drawdowns = (cumulative_returns - rolling_max) / rolling_max
            max_drawdown = drawdowns.min()
            
            return {
                'total_trades': total_trades,
                'winning_trades': winning_trades,
                'win_rate': winning_trades / total_trades if total_trades > 0 else 0,
                'total_profit': total_profit,
                'average_return': avg_return,
                'sharpe_ratio': sharpe,
                'max_drawdown': max_drawdown,
                'profit_factor': self._calculate_profit_factor(df),
                'average_trade_duration': df['duration'].mean(),
                'best_trade': df['profit'].max(),
                'worst_trade': df['profit'].min(),
                'largest_position': df['size'].max(),
                'average_position_size': df['size'].mean()
            }
            
        except Exception as e:
            self.logger.error(f"Error analyzing performance: {e}")
            return self._get_default_metrics()
            
    def generate_reports(self, output_dir: Path):
        """Generate performance reports"""
        try:
            output_dir.mkdir(parents=True, exist_ok=True)
            
            # Generate summary report
            self._generate_summary_report(output_dir)
            
            # Generate detailed analysis
            self._generate_detailed_report(output_dir)
            
            # Generate trade analysis
            self._generate_trade_analysis(output_dir)
            
        except Exception as e:
            self.logger.error(f"Error generating reports: {e}")
            
    def plot_performance(self, output_dir: Path):
        """Create performance visualizations"""
        try:
            output_dir.mkdir(parents=True, exist_ok=True)
            
            # Create equity curve plot
            self._plot_equity_curve(output_dir)
            
            # Create drawdown plot
            self._plot_drawdown(output_dir)
            
            # Create trade distribution plot
            self._plot_trade_distribution(output_dir)
            
            # Create interactive dashboard
            self._create_dashboard(output_dir)
            
        except Exception as e:
            self.logger.error(f"Error creating visualizations: {e}")
            
    def _load_trades(self) -> List[Dict]:
        """Load trade history"""
        try:
            trades_file = self.data_dir / 'trades.json'
            if not trades_file.exists():
                return []
                
            with open(trades_file) as f:
                return json.load(f)
                
        except Exception as e:
            self.logger.error(f"Error loading trades: {e}")
            return []
            
    def _load_metrics(self) -> Dict:
        """Load performance metrics"""
        try:
            metrics_file = self.data_dir / 'metrics.json'
            if not metrics_file.exists():
                return {}
                
            with open(metrics_file) as f:
                return json.load(f)
                
        except Exception as e:
            self.logger.error(f"Error loading metrics: {e}")
            return {}
            
    def _load_equity_curve(self) -> pd.Series:
        """Load equity curve data"""
        try:
            equity_file = self.data_dir / 'equity_curve.csv'
            if not equity_file.exists():
                return pd.Series()
                
            return pd.read_csv(equity_file, index_col=0, squeeze=True)
            
        except Exception as e:
            self.logger.error(f"Error loading equity curve: {e}")
            return pd.Series()
            
    def _calculate_profit_factor(self, df: pd.DataFrame) -> float:
        """Calculate profit factor"""
        winning_trades = df[df['profit'] > 0]['profit'].sum()
        losing_trades = abs(df[df['profit'] < 0]['profit'].sum())
        return winning_trades / losing_trades if losing_trades != 0 else float('inf')
        
    def _generate_summary_report(self, output_dir: Path):
        """Generate performance summary report"""
        metrics = self.analyze_performance()
        
        report = [
            "Trading Performance Summary",
            "=" * 30,
            f"\nAnalysis Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "\nOverall Performance",
            "-" * 20,
            f"Total Trades: {metrics['total_trades']}",
            f"Winning Trades: {metrics['winning_trades']}",
            f"Win Rate: {metrics['win_rate']:.2%}",
            f"Total Profit: {metrics['total_profit']:.4f} SOL",
            f"Sharpe Ratio: {metrics['sharpe_ratio']:.2f}",
            f"Max Drawdown: {metrics['max_drawdown']:.2%}",
            f"Profit Factor: {metrics['profit_factor']:.2f}",
            
            "\nTrade Statistics",
            "-" * 20,
            f"Average Return: {metrics['average_return']:.2%}",
            f"Best Trade: {metrics['best_trade']:.4f} SOL",
            f"Worst Trade: {metrics['worst_trade']:.4f} SOL",
            f"Average Duration: {metrics['average_trade_duration']}",
            
            "\nPosition Sizing",
            "-" * 20,
            f"Largest Position: {metrics['largest_position']:.4f} SOL",
            f"Average Position: {metrics['average_position_size']:.4f} SOL"
        ]
        
        with open(output_dir / 'summary_report.txt', 'w') as f:
            f.write('\n'.join(report))
            
    def _generate_detailed_report(self, output_dir: Path):
        """Generate detailed performance analysis"""
        if not self.trades:
            return
            
        df = pd.DataFrame(self.trades)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        
        # Time-based analysis
        hourly_stats = df.groupby(df['timestamp'].dt.hour)['profit'].agg(['mean', 'count'])
        daily_stats = df.groupby(df['timestamp'].dt.day_name())['profit'].agg(['mean', 'count'])
        
        # Position size analysis
        size_stats = df.groupby(pd.qcut(df['size'], 5))['profit'].agg(['mean', 'count'])
        
        # Duration analysis
        df['duration'] = pd.to_timedelta(df['duration'])
        duration_stats = df.groupby(pd.qcut(df['duration'], 5))['profit'].agg(['mean', 'count'])
        
        report = [
            "Detailed Performance Analysis",
            "=" * 30,
            
            "\nHourly Performance",
            "-" * 20,
            hourly_stats.to_string(),
            
            "\nDaily Performance",
            "-" * 20,
            daily_stats.to_string(),
            
            "\nPosition Size Analysis",
            "-" * 20,
            size_stats.to_string(),
            
            "\nDuration Analysis",
            "-" * 20,
            duration_stats.to_string()
        ]
        
        with open(output_dir / 'detailed_report.txt', 'w') as f:
            f.write('\n'.join(report))
            
    def _generate_trade_analysis(self, output_dir: Path):
        """Generate trade-by-trade analysis"""
        if not self.trades:
            return
            
        df = pd.DataFrame(self.trades)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df['duration'] = pd.to_timedelta(df['duration'])
        df['return'] = df['profit'] / df['size']
        
        # Calculate trade metrics
        df['cumulative_profit'] = df['profit'].cumsum()
        df['drawdown'] = df['cumulative_profit'] - df['cumulative_profit'].expanding().max()
        
        # Export to CSV
        df.to_csv(output_dir / 'trade_analysis.csv')
        
    def _plot_equity_curve(self, output_dir: Path):
        """Plot equity curve"""
        if self.equity_curve.empty:
            return
            
        plt.figure(figsize=(12, 6))
        plt.plot(self.equity_curve.index, self.equity_curve.values)
        plt.title('Equity Curve')
        plt.xlabel('Trade Number')
        plt.ylabel('Equity')
        plt.grid(True)
        plt.savefig(output_dir / 'equity_curve.png')
        plt.close()
        
    def _plot_drawdown(self, output_dir: Path):
        """Plot drawdown chart"""
        if self.equity_curve.empty:
            return
            
        rolling_max = self.equity_curve.expanding().max()
        drawdown = (self.equity_curve - rolling_max) / rolling_max
        
        plt.figure(figsize=(12, 6))
        plt.plot(drawdown.index, drawdown.values * 100)
        plt.title('Drawdown')
        plt.xlabel('Trade Number')
        plt.ylabel('Drawdown %')
        plt.grid(True)
        plt.savefig(output_dir / 'drawdown.png')
        plt.close()
        
    def _plot_trade_distribution(self, output_dir: Path):
        """Plot trade profit distribution"""
        if not self.trades:
            return
            
        df = pd.DataFrame(self.trades)
        
        plt.figure(figsize=(12, 6))
        sns.histplot(data=df, x='profit', bins=50)
        plt.title('Trade Profit Distribution')
        plt.xlabel('Profit')
        plt.ylabel('Count')
        plt.grid(True)
        plt.savefig(output_dir / 'profit_distribution.png')
        plt.close()
        
    def _create_dashboard(self, output_dir: Path):
        """Create interactive performance dashboard"""
        if not self.trades:
            return
            
        df = pd.DataFrame(self.trades)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        
        # Create subplot figure
        fig = make_subplots(
            rows=3, cols=2,
            subplot_titles=(
                'Equity Curve', 'Drawdown',
                'Profit Distribution', 'Position Sizes',
                'Daily Returns', 'Trade Duration'
            )
        )
        
        # Add equity curve
        fig.add_trace(
            go.Scatter(y=self.equity_curve, name='Equity'),
            row=1, col=1
        )
        
        # Add drawdown
        rolling_max = self.equity_curve.expanding().max()
        drawdown = (self.equity_curve - rolling_max) / rolling_max
        fig.add_trace(
            go.Scatter(y=drawdown * 100, name='Drawdown %'),
            row=1, col=2
        )
        
        # Add profit distribution
        fig.add_trace(
            go.Histogram(x=df['profit'], name='Profit Distribution'),
            row=2, col=1
        )
        
        # Add position sizes
        fig.add_trace(
            go.Box(y=df['size'], name='Position Sizes'),
            row=2, col=2
        )
        
        # Add daily returns
        daily_returns = df.groupby(df['timestamp'].dt.date)['profit'].sum()
        fig.add_trace(
            go.Bar(y=daily_returns, name='Daily Returns'),
            row=3, col=1
        )
        
        # Add trade duration
        df['duration'] = pd.to_timedelta(df['duration'])
        fig.add_trace(
            go.Box(y=df['duration'].dt.total_seconds() / 3600, name='Duration (hours)'),
            row=3, col=2
        )
        
        # Update layout
        fig.update_layout(
            height=1200,
            width=1200,
            title_text="Trading Performance Dashboard",
            showlegend=False
        )
        
        # Save dashboard
        fig.write_html(output_dir / 'dashboard.html')
        
    def _get_default_metrics(self) -> Dict:
        """Return default metrics when no data available"""
        return {
            'total_trades': 0,
            'winning_trades': 0,
            'win_rate': 0.0,
            'total_profit': 0.0,
            'average_return': 0.0,
            'sharpe_ratio': 0.0,
            'max_drawdown': 0.0,
            'profit_factor': 0.0,
            'average_trade_duration': timedelta(0),
            'best_trade': 0.0,
            'worst_trade': 0.0,
            'largest_position': 0.0,
            'average_position_size': 0.0
        }

def main():
    """Main function"""
    parser = argparse.ArgumentParser(description='Trading Performance Analyzer')
    
    parser.add_argument('--data-dir', type=str, required=True,
                       help='Directory containing performance data')
    parser.add_argument('--output-dir', type=str, default='analysis',
                       help='Directory to save analysis results')
    
    args = parser.parse_args()
    
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    try:
        analyzer = PerformanceAnalyzer(Path(args.data_dir))
        output_dir = Path(args.output_dir)
        
        # Generate analysis
        analyzer.generate_reports(output_dir)
        analyzer.plot_performance(output_dir)
        
        logging.info(f"Analysis completed. Results saved to {output_dir}")
        
    except Exception as e:
        logging.error(f"Analysis failed: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
