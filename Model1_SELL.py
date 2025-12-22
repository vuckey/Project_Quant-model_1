from alpaca.trading.client import TradingClient

trading_client = TradingClient(
    api_key="Here enter your own alpaca trading API key",
    secret_key="Here enter your own alpaca trading API secret key"
)

clock = trading_client.get_clock()

if not clock.is_open:
    print("Market is closed. Positions NOT closed.")
    exit()

trading_client.close_all_positions()