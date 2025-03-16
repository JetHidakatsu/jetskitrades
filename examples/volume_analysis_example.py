"""Example usage of volume analysis system"""

import asyncio
import os
from datetime import datetime

from solana.rpc.async_api import AsyncClient

from ..env.volume_analyzer import VolumeAnalyzer
from ..env.token_safety_analyzer import TokenSafetyAnalyzer

async def analyze_token_volume(
    endpoint: str,
    token_mint: str,
    pool_address: str,
    creator_address: str
):
    """Analyze token volume and safety"""
    
    # Initialize client
    client = AsyncClient(endpoint)
    
    try:
        # Create analyzers
        volume_analyzer = VolumeAnalyzer(
            client,
            cache_duration=3600,
            volume_window=24,
            large_tx_threshold=10000,
            spike_threshold=200.0
        )
        
        safety_analyzer = TokenSafetyAnalyzer(client)
        
        # Analyze volume directly
        print("\nDirect Volume Analysis:")
        print("----------------------")
        
        volume_result = await volume_analyzer.analyze_volume(
            token_mint,
            pool_address
        )
        
        print(f"24h Volume: {volume_result['volume_24h']:.2f} USDC")
        print(f"Volume Change: {volume_result['volume_change_24h']:.1f}%")
        print(f"Volume Spikes: {volume_result['volume_spikes']}")
        print(f"Buy/Sell Ratio: {volume_result['buy_sell_ratio']:.2f}")
        print(f"Large TX Ratio: {volume_result['large_tx_ratio']:.2f}")
        print(f"Volume Risk Score: {volume_result['risk_score']:.2f}")
        
        if volume_result['volume_spikes'] > 0:
            print("\nVolume Spike Times:")
            for spike_time in volume_result['spike_times']:
                print(f"- {spike_time}")
        
        # Analyze token safety (includes volume)
        print("\nToken Safety Analysis:")
        print("---------------------")
        
        safety_result = await safety_analyzer.analyze_token(
            token_mint,
            pool_address,
            creator_address
        )
        
        print(f"\nComponent Scores:")
        for component, score in safety_result['component_scores'].items():
            print(f"- {component}: {score:.2f}")
            
        print(f"\nOverall Safety Score: {safety_result['overall_safety_score']:.2f}")
        
        if safety_result['risk_factors']:
            print("\nRisk Factors:")
            for factor in safety_result['risk_factors']:
                print(f"- {factor}")
        
        print(f"\nIs Safe: {safety_result['is_safe']}")
        
        # Example of handling volume-specific risks
        volume_metrics = safety_result['volume_metrics']
        if volume_metrics['volume_change_24h'] > 200:
            print("\nWarning: Unusual volume increase detected!")
            print(f"Volume increased by {volume_metrics['volume_change_24h']:.1f}%")
            
        if volume_metrics['buy_sell_ratio'] < 0.5:
            print("\nWarning: Heavy selling pressure detected!")
            print(f"Buy/Sell ratio: {volume_metrics['buy_sell_ratio']:.2f}")

    except Exception as e:
        print(f"Error during analysis: {e}")
    
    finally:
        await client.close()

def main():
    """Run the example"""
    # Example token data (replace with real addresses)
    endpoint = "https://api.mainnet-beta.solana.com"
    token_mint = "YOUR_TOKEN_MINT"
    pool_address = "YOUR_POOL_ADDRESS"
    creator_address = "YOUR_CREATOR_ADDRESS"
    
    print("Starting Volume Analysis Example...")
    print("==================================")
    
    asyncio.run(analyze_token_volume(
        endpoint,
        token_mint,
        pool_address,
        creator_address
    ))

if __name__ == "__main__":
    main()
