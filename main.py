#!/usr/bin/env python3
from trail import StopTrail
import argparse
import json
import requests

def main(options):

    if options.type not in ['buy', 'sell', 'sell_percent', 'buy_percent']:
        print("Error: Please use valid trail type (Ex: 'buy', 'buy_percent', 'sell', 'sell_percent')")
        return

    task = StopTrail(options.symbol, options.type, options.size, options.interval)
    task.run()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--symbol', type=str, help='Market Symbol (Ex: NEO/BTC - NEO/USDT)', required=True)
    parser.add_argument('--size', type=float, help='How many satoshis (or USD) the stop loss should be placed above or below current price', required=True)
    parser.add_argument('--type', type=str, help="Specify whether the trailing stop loss should be in buying or selling mode. (Ex: 'buy', 'buy_percent', 'sell', 'sell_percent')", required=True)
    parser.add_argument('--interval', type=float, help="How often the bot should check for price changes", default=5)

    options = parser.parse_args()
    main(options)
