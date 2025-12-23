from alpaca.trading.client import TradingClient
from alpaca.trading.requests import MarketOrderRequest
from alpaca.trading.enums import OrderSide, TimeInForce
from alpaca.data.historical import StockHistoricalDataClient
from alpaca.data.requests import StockBarsRequest
from alpaca.data.timeframe import TimeFrame
from datetime import datetime, timezone
from datetime import timedelta
import xgboost as xgb
import pandas as pd
import numpy as np
import os

nas100data = pd.read_json("Here should be the path of the 'Nasdaq 100 (NDX).csv' file", orient="index")
ticker = nas100data["symbol"]
ticker = ticker[ticker !="n/a"]
ticker_array = ticker.to_numpy()

client = StockHistoricalDataClient("Here enter your own alpaca trading API key", "Here enter your own alpaca trading API secret key")
numeric_cols = ["open", "high", "low", "close", "volume", "trade_count", "vwap"]
data = []
model_accuracy_data=[]
good_symbols=[]
booster = xgb.Booster()
booster.load_model(r"The path of the model ( 'xgboost_model1.json' file) ")

for symbol in ticker_array:
    request_params = StockBarsRequest(
        symbol_or_symbols=symbol,
        timeframe=TimeFrame.Day,
        start=datetime.now(timezone.utc) - timedelta(days=120),
        end=datetime.now(timezone.utc) - timedelta(days=1),
        limit=21
    )
    bars = client.get_stock_bars(request_params)
    values = bars[symbol]
    df=pd.DataFrame([dict(values) for values in values])
    df["datetime"]=pd.to_datetime(df["timestamp"])
    df[numeric_cols] = df[numeric_cols].astype(float)
    df=df.set_index("datetime")
    df=df.sort_values("datetime")
    df["log_return"]=np.log(df["close"]/df["close"].shift(1))
    df["high_low_range"] = (df["high"] - df["low"]) / df["close"]
    df["close_open_return"] = (df["close"] - df["open"]) / df["open"]
    df["candle_size"] = (df["close"] - df["open"]).abs()
    df["upper_wick"] = df["high"] - df[["open", "close"]].max(axis=1)
    df["lower_wick"] = df[["open", "close"]].min(axis=1) - df["low"]
    df["volatility_20"] = df["log_return"].rolling(20).std()
    df["mean_return_10"] = df["log_return"].rolling(10).mean()
    df["mean_return_20"] = df["log_return"].rolling(20).mean()
    df["price_vs_ma20"] = df["close"] / df["close"].rolling(20).mean() - 1
    df["range_mean_20"] = df["high_low_range"].rolling(20).mean()
    df["volume_mean_20"] = df["volume"].rolling(20).mean()
    df["volume_ratio"] = df["volume"] / df["volume_mean_20"]
    df=df.dropna()
    df=df.drop(columns=numeric_cols)
    df=df.drop(columns="timestamp")
    data.append(df)

pooled_data=pd.concat(data, axis=0)
sorted_data=pooled_data.groupby("symbol")
for symbol, stock_df in sorted_data:
    stock_df=stock_df.drop(columns="symbol")
    dmat = xgb.DMatrix(stock_df)
    preds=booster.predict(dmat)
    prob=float(preds[-1])
    if prob> 0.65:
        model_accuracy_data.append({"symbol": symbol, "probability": preds, "action": 1})
        good_symbols.append(symbol)
    else:
        model_accuracy_data.append({"symbol": symbol, "probability": preds, "action": 0})

Trading_client = TradingClient("Here enter your own alpaca trading API key", "Here enter your own alpaca trading API secret key")
for symbol in good_symbols:
    market_order_data = MarketOrderRequest(symbol=symbol,
                                           notional=500,
                                           side=OrderSide.BUY,
                                           time_in_force=TimeInForce.DAY
                                           )
    market_order = Trading_client.submit_order(order_data=market_order_data)


date_str = datetime.now().strftime("%Y-%m-%d")
file_name = f"{date_str}.json"
accuracy_file=pd.DataFrame(model_accuracy_data)
path = os.path.join("data", "model_performance", file_name)

accuracy_file.to_json(path, orient="index", indent=2)

