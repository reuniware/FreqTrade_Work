# pragma pylint: disable=missing-docstring, invalid-name, pointless-string-statement
# flake8: noqa: F401
# isort: skip_file
# --- Do not remove these libs ---
import numpy as np  # noqa
import pandas as pd  # noqa
from pandas import DataFrame
import os
from datetime import datetime

from freqtrade.strategy import (BooleanParameter, CategoricalParameter, DecimalParameter,
                                IStrategy, IntParameter, RealParameter)

from freqtrade.strategy import merge_informative_pair

# --------------------------------
# Add your lib to import here
import talib.abstract as ta
import freqtrade.vendor.qtpylib.indicators as qtpylib
import ta as taichi

pd.set_option('display.max_columns', 100)
pd.set_option('display.max_rows', None)
pd.set_option('display.expand_frame_repr', True)

def delete_log_results():
    if os.path.exists("mylogs.txt"):
        os.remove("mylogs.txt")

def log_to_results(str_to_log):
    fr = open("mylogs.txt", "a")
    #fr.write(str(datetime.now()) + " : " + str_to_log + "\n")
    fr.write(str_to_log + "\n")
    fr.close()

# This class is a sample. Feel free to customize it.
class StratIchimoku008Binance(IStrategy):
    delete_log_results()

    # Strategy interface version - allow new iterations of the strategy interface.
    # Check the documentation or the Sample strategy to get the latest version.
    INTERFACE_VERSION = 3

    # Can this strategy go short?
    can_short: bool = False

    #roi0 = RealParameter(0.01, 0.09, decimals=1, default=0.04, space="buy")

    # Minimal ROI designed for the strategy.
    # This attribute will be overridden if the config file contains "minimal_roi".
    minimal_roi = {
        #"60": 0.01,
        #"30": 0.01,
        "0": 0.01
    }

    # Optimal stoploss designed for the strategy.
    # This attribute will be overridden if the config file contains "stoploss".
    stoploss = -0.005

    # Trailing stoploss
    trailing_stop = False
    # trailing_only_offset_is_reached = False
    trailing_stop_positive = 0.0025
    # trailing_stop_positive_offset = 0.0  # Disabled / not configured

    # Optimal timeframe for the strategy.
    timeframe = '1m'

    # Run "populate_indicators()" only for new candle.
    process_only_new_candles = False

    # These values can be overridden in the config.
    use_exit_signal = True
    exit_profit_only = False
    ignore_roi_if_entry_signal = False

    # Number of candles the strategy requires before producing valid signals
    startup_candle_count: int = 26

    # Optional order type mapping.
    order_types = {
        'entry': 'limit',
        'exit': 'limit',
        'stoploss': 'market',
        'stoploss_on_exchange': False
    }

    # Optional order time in force.
    order_time_in_force = {
        'entry': 'gtc',
        'exit': 'gtc'
    }

    def informative_pairs(self):
        # get access to all pairs available in whitelist.
        pairs = self.dp.current_whitelist()
        # Assign tf to each pair so they can be downloaded and cached for strategy.
        #informative_pairs = [(pair, '1m') for pair in pairs]
        informative_pairs = [(pair, '5m') for pair in pairs]
        informative_pairs += [(pair, '15m') for pair in pairs]
        #informative_pairs += [(pair, '30m') for pair in pairs]
        #informative_pairs += [(pair, '1h') for pair in pairs]
        #informative_pairs += [(pair, '4h') for pair in pairs]
        # Optionally Add additional "static" pairs
        #informative_pairs += [("BTC/USDT", "1m"), ("BTC/USDT", "15m"), ("BTC/USDT", "30m"), ("BTC/USDT", "1h"), ("BTC/USDT", "4h"),]
        informative_pairs += [("BTC/USDT", "1m"), ("BTC/USDT", "5m"),]
        return informative_pairs

    informativeBTC1M : DataFrame
    informativeBTC5M : DataFrame
    #informativeBTC15M : DataFrame
    #informativeBTC30M : DataFrame
    #informativeBTC1H : DataFrame
    #informativeBTC4H : DataFrame
    #informative1M : DataFrame
    informative5M : DataFrame
    informative15M : DataFrame
    #informative30M : DataFrame
    #informative1H : DataFrame
    #informative4H : DataFrame

    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:

        global informativeBTC1M
        global informativeBTC5M
        #global informativeBTC15M
        #global informativeBTC30M
        #global informativeBTC1H
        #global informativeBTC4H
        #global informative1M
        global informative5M
        global informative15M
        #global informative30M
        #global informative1H
        #global informative4H

        #log_to_results(metadata['pair'])
        currentPair = str(metadata['pair'])

        inf_tf = '1m'
        informativeBTC1M = self.dp.get_pair_dataframe(pair="BTC/USDT", timeframe=inf_tf)
        inf_tf = '5m'
        informativeBTC5M = self.dp.get_pair_dataframe(pair="BTC/USDT", timeframe=inf_tf)
        #inf_tf = '15m'
        #informativeBTC15M = self.dp.get_pair_dataframe(pair="BTC/USDT", timeframe=inf_tf)
        #inf_tf = '30m'
        #informativeBTC30M = self.dp.get_pair_dataframe(pair="BTC/USDT", timeframe=inf_tf)
        #inf_tf = '1h'
        #informativeBTC1H = self.dp.get_pair_dataframe(pair="BTC/USDT", timeframe=inf_tf)
        #inf_tf = '4h'
        #informativeBTC4H = self.dp.get_pair_dataframe(pair="BTC/USDT", timeframe=inf_tf)
        #inf_tf = '1m'
        #informative1M = self.dp.get_pair_dataframe(pair=currentPair, timeframe=inf_tf)
        inf_tf = '5m'
        informative5M = self.dp.get_pair_dataframe(pair=currentPair, timeframe=inf_tf)
        inf_tf = '15m'
        informative15M = self.dp.get_pair_dataframe(pair=currentPair, timeframe=inf_tf)
        #inf_tf = '30m'
        #informative30M = self.dp.get_pair_dataframe(pair=currentPair, timeframe=inf_tf)
        #inf_tf = '1h'
        #informative1H = self.dp.get_pair_dataframe(pair=currentPair, timeframe=inf_tf)
        #inf_tf = '4h'
        #informative4H = self.dp.get_pair_dataframe(pair=currentPair, timeframe=inf_tf)

        #log_to_results(informative15M.to_string())

        #Ichimoku calculations for the BTC in 1m
        informativeBTC1M['BTC_ICH_SSB_1M'] = taichi.trend.ichimoku_b(informativeBTC1M['high'], informativeBTC1M['low'], window2=26, window3=52).shift(26)
        informativeBTC1M['BTC_ICH_SSA_1M'] = taichi.trend.ichimoku_a(informativeBTC1M['high'], informativeBTC1M['low'], window1=9, window2=26).shift(26)
        informativeBTC1M['BTC_ICH_KS_1M'] = taichi.trend.ichimoku_base_line(informativeBTC1M['high'], informativeBTC1M['low'])
        informativeBTC1M['BTC_ICH_TS_1M'] = taichi.trend.ichimoku_conversion_line(informativeBTC1M['high'], informativeBTC1M['low'])
        informativeBTC1M['BTC_ICH_CS_1M'] = informativeBTC1M['close']
        informativeBTC1M['BTC_ICH_CS_HIGH_1M'] = informativeBTC1M['high'].shift(26)
        informativeBTC1M['BTC_ICH_CS_LOW_1M'] = informativeBTC1M['low'].shift(26)
        informativeBTC1M['BTC_ICH_CS_KS_1M'] = informativeBTC1M['BTC_ICH_KS_1M'].shift(26)
        informativeBTC1M['BTC_ICH_CS_TS_1M'] = informativeBTC1M['BTC_ICH_TS_1M'].shift(26)
        informativeBTC1M['BTC_ICH_CS_SSA_1M'] = informativeBTC1M['BTC_ICH_SSA_1M'].shift(26)
        informativeBTC1M['BTC_ICH_CS_SSB_1M'] = informativeBTC1M['BTC_ICH_SSB_1M'].shift(26)

        #Ichimoku calculations for the BTC in 5m
        informativeBTC5M['BTC_ICH_SSB_5M'] = taichi.trend.ichimoku_b(informativeBTC5M['high'], informativeBTC5M['low'], window2=26, window3=52).shift(26)
        informativeBTC5M['BTC_ICH_SSA_5M'] = taichi.trend.ichimoku_a(informativeBTC5M['high'], informativeBTC5M['low'], window1=9, window2=26).shift(26)
        informativeBTC5M['BTC_ICH_KS_5M'] = taichi.trend.ichimoku_base_line(informativeBTC5M['high'], informativeBTC5M['low'])
        informativeBTC5M['BTC_ICH_TS_5M'] = taichi.trend.ichimoku_conversion_line(informativeBTC5M['high'], informativeBTC5M['low'])
        informativeBTC5M['BTC_ICH_CS_5M'] = informativeBTC5M['close']
        informativeBTC5M['BTC_ICH_CS_HIGH_5M'] = informativeBTC5M['high'].shift(26)
        informativeBTC5M['BTC_ICH_CS_LOW_5M'] = informativeBTC5M['low'].shift(26)
        informativeBTC5M['BTC_ICH_CS_KS_5M'] = informativeBTC5M['BTC_ICH_KS_5M'].shift(26)
        informativeBTC5M['BTC_ICH_CS_TS_5M'] = informativeBTC5M['BTC_ICH_TS_5M'].shift(26)
        informativeBTC5M['BTC_ICH_CS_SSA_5M'] = informativeBTC5M['BTC_ICH_SSA_5M'].shift(26)
        informativeBTC5M['BTC_ICH_CS_SSB_5M'] = informativeBTC5M['BTC_ICH_SSB_5M'].shift(26)

        #Ichimoku calculations for the BTC in 15m
        #informativeBTC15M['BTC_ICH_SSB_15M'] = taichi.trend.ichimoku_b(informativeBTC15M['high'], informativeBTC15M['low'], window2=26, window3=52).shift(26)
        #informativeBTC15M['BTC_ICH_SSA_15M'] = taichi.trend.ichimoku_a(informativeBTC15M['high'], informativeBTC15M['low'], window1=9, window2=26).shift(26)
        #informativeBTC15M['BTC_ICH_KS_15M'] = taichi.trend.ichimoku_base_line(informativeBTC15M['high'], informativeBTC15M['low'])
        #informativeBTC15M['BTC_ICH_TS_15M'] = taichi.trend.ichimoku_conversion_line(informativeBTC15M['high'], informativeBTC15M['low'])
        #informativeBTC15M['BTC_ICH_CS_15M'] = informativeBTC15M['close']
        #informativeBTC15M['BTC_ICH_CS_HIGH_15M'] = informativeBTC15M['high'].shift(26)
        #informativeBTC15M['BTC_ICH_CS_LOW_15M'] = informativeBTC15M['low'].shift(26)
        #informativeBTC15M['BTC_ICH_CS_KS_15M'] = informativeBTC15M['BTC_ICH_KS_15M'].shift(26)
        #informativeBTC15M['BTC_ICH_CS_TS_15M'] = informativeBTC15M['BTC_ICH_TS_15M'].shift(26)
        #informativeBTC15M['BTC_ICH_CS_SSA_15M'] = informativeBTC15M['BTC_ICH_SSA_15M'].shift(26)
        #informativeBTC15M['BTC_ICH_CS_SSB_15M'] = informativeBTC15M['BTC_ICH_SSB_15M'].shift(26)

        #Ichimoku calculations for the BTC in 30m
        #informativeBTC30M['BTC_ICH_SSB_30M'] = taichi.trend.ichimoku_b(informativeBTC30M['high'], informativeBTC30M['low'], window2=26, window3=52).shift(26)
        #informativeBTC30M['BTC_ICH_SSA_30M'] = taichi.trend.ichimoku_a(informativeBTC30M['high'], informativeBTC30M['low'], window1=9, window2=26).shift(26)
        #informativeBTC30M['BTC_ICH_KS_30M'] = taichi.trend.ichimoku_base_line(informativeBTC30M['high'], informativeBTC30M['low'])
        #informativeBTC30M['BTC_ICH_TS_30M'] = taichi.trend.ichimoku_conversion_line(informativeBTC30M['high'], informativeBTC30M['low'])
        #informativeBTC30M['BTC_ICH_CS_30M'] = informativeBTC30M['close']
        #informativeBTC30M['BTC_ICH_CS_HIGH_30M'] = informativeBTC30M['high'].shift(26)
        #informativeBTC30M['BTC_ICH_CS_LOW_30M'] = informativeBTC30M['low'].shift(26)
        #informativeBTC30M['BTC_ICH_CS_KS_30M'] = informativeBTC30M['BTC_ICH_KS_30M'].shift(26)
        #informativeBTC30M['BTC_ICH_CS_TS_30M'] = informativeBTC30M['BTC_ICH_TS_30M'].shift(26)
        #informativeBTC30M['BTC_ICH_CS_SSA_30M'] = informativeBTC30M['BTC_ICH_SSA_30M'].shift(26)
        #informativeBTC30M['BTC_ICH_CS_SSB_30M'] = informativeBTC30M['BTC_ICH_SSB_30M'].shift(26)

        #Ichimoku calculations for the BTC in 1h
        #informativeBTC1H['BTC_ICH_SSB_1H'] = taichi.trend.ichimoku_b(informativeBTC1H['high'], informativeBTC1H['low'], window2=26, window3=52).shift(26)
        #informativeBTC1H['BTC_ICH_SSA_1H'] = taichi.trend.ichimoku_a(informativeBTC1H['high'], informativeBTC1H['low'], window1=9, window2=26).shift(26)
        #informativeBTC1H['BTC_ICH_KS_1H'] = taichi.trend.ichimoku_base_line(informativeBTC1H['high'], informativeBTC1H['low'])
        #informativeBTC1H['BTC_ICH_TS_1H'] = taichi.trend.ichimoku_conversion_line(informativeBTC1H['high'], informativeBTC1H['low'])
        #informativeBTC1H['BTC_ICH_CS_1H'] = informativeBTC1H['close']
        #informativeBTC1H['BTC_ICH_CS_HIGH_1H'] = informativeBTC1H['high'].shift(26)
        #informativeBTC1H['BTC_ICH_CS_LOW_1H'] = informativeBTC1H['low'].shift(26)
        #informativeBTC1H['BTC_ICH_CS_KS_1H'] = informativeBTC1H['BTC_ICH_KS_1H'].shift(26)
        #informativeBTC1H['BTC_ICH_CS_TS_1H'] = informativeBTC1H['BTC_ICH_TS_1H'].shift(26)
        #informativeBTC1H['BTC_ICH_CS_SSA_1H'] = informativeBTC1H['BTC_ICH_SSA_1H'].shift(26)
        #informativeBTC1H['BTC_ICH_CS_SSB_1H'] = informativeBTC1H['BTC_ICH_SSB_1H'].shift(26)

        #Ichimoku calculations for the BTC in 4h
        #informativeBTC4H['BTC_ICH_SSB_4H'] = taichi.trend.ichimoku_b(informativeBTC4H['high'], informativeBTC4H['low'], window2=26, window3=52).shift(26)
        #informativeBTC4H['BTC_ICH_SSA_4H'] = taichi.trend.ichimoku_a(informativeBTC4H['high'], informativeBTC4H['low'], window1=9, window2=26).shift(26)
        #informativeBTC4H['BTC_ICH_KS_4H'] = taichi.trend.ichimoku_base_line(informativeBTC4H['high'], informativeBTC4H['low'])
        #informativeBTC4H['BTC_ICH_TS_4H'] = taichi.trend.ichimoku_conversion_line(informativeBTC4H['high'], informativeBTC4H['low'])
        #informativeBTC4H['BTC_ICH_CS_4H'] = informativeBTC4H['close']
        #informativeBTC4H['BTC_ICH_CS_HIGH_4H'] = informativeBTC4H['high'].shift(26)
        #informativeBTC4H['BTC_ICH_CS_LOW_4H'] = informativeBTC4H['low'].shift(26)
        #informativeBTC4H['BTC_ICH_CS_KS_4H'] = informativeBTC4H['BTC_ICH_KS_4H'].shift(26)
        #informativeBTC4H['BTC_ICH_CS_TS_4H'] = informativeBTC4H['BTC_ICH_TS_4H'].shift(26)
        #informativeBTC4H['BTC_ICH_CS_SSA_4H'] = informativeBTC4H['BTC_ICH_SSA_4H'].shift(26)
        #informativeBTC4H['BTC_ICH_CS_SSB_4H'] = informativeBTC4H['BTC_ICH_SSB_4H'].shift(26)

        #Ichimoku calculations for the current pair in 1m
        #informative1M['ICH_SSB_1M'] = taichi.trend.ichimoku_b(informative1M['high'], informative1M['low'], window2=26, window3=52).shift(26)
        #informative1M['ICH_SSA_1M'] = taichi.trend.ichimoku_a(informative1M['high'], informative1M['low'], window1=9, window2=26).shift(26)
        #informative1M['ICH_KS_1M'] = taichi.trend.ichimoku_base_line(informative1M['high'], informative1M['low'])
        #informative1M['ICH_TS_1M'] = taichi.trend.ichimoku_conversion_line(informative1M['high'], informative1M['low'])
        #informative1M['ICH_CS_1M'] = informative1M['close']
        #informative1M['ICH_CS_HIGH_1M'] = informative1M['high'].shift(26)
        #informative1M['ICH_CS_LOW_1M'] = informative1M['low'].shift(26)
        #informative1M['ICH_CS_KS_1M'] = informative1M['ICH_KS_1M'].shift(26)
        #informative1M['ICH_CS_TS_1M'] = informative1M['ICH_TS_1M'].shift(26)
        #informative1M['ICH_CS_SSA_1M'] = informative1M['ICH_SSA_1M'].shift(26)
        #informative1M['ICH_CS_SSB_1M'] = informative1M['ICH_SSB_1M'].shift(26)

        #Ichimoku calculations for the current pair in 5m
        informative5M['ICH_SSB_5M'] = taichi.trend.ichimoku_b(informative5M['high'], informative5M['low'], window2=26, window3=52).shift(26)
        informative5M['ICH_SSA_5M'] = taichi.trend.ichimoku_a(informative5M['high'], informative5M['low'], window1=9, window2=26).shift(26)
        informative5M['ICH_KS_5M'] = taichi.trend.ichimoku_base_line(informative5M['high'], informative5M['low'])
        informative5M['ICH_TS_5M'] = taichi.trend.ichimoku_conversion_line(informative5M['high'], informative5M['low'])
        informative5M['ICH_CS_5M'] = informative5M['close']
        informative5M['ICH_CS_HIGH_5M'] = informative5M['high'].shift(26)
        informative5M['ICH_CS_LOW_5M'] = informative5M['low'].shift(26)
        informative5M['ICH_CS_KS_5M'] = informative5M['ICH_KS_5M'].shift(26)
        informative5M['ICH_CS_TS_5M'] = informative5M['ICH_TS_5M'].shift(26)
        informative5M['ICH_CS_SSA_5M'] = informative5M['ICH_SSA_5M'].shift(26)
        informative5M['ICH_CS_SSB_5M'] = informative5M['ICH_SSB_5M'].shift(26)

        #Ichimoku calculations for the current pair in 15m
        informative15M['ICH_SSB_15M'] = taichi.trend.ichimoku_b(informative15M['high'], informative15M['low'], window2=26, window3=52).shift(26)
        informative15M['ICH_SSA_15M'] = taichi.trend.ichimoku_a(informative15M['high'], informative15M['low'], window1=9, window2=26).shift(26)
        informative15M['ICH_KS_15M'] = taichi.trend.ichimoku_base_line(informative15M['high'], informative15M['low'])
        informative15M['ICH_TS_15M'] = taichi.trend.ichimoku_conversion_line(informative15M['high'], informative15M['low'])
        informative15M['ICH_CS_15M'] = informative15M['close']
        informative15M['ICH_CS_HIGH_15M'] = informative15M['high'].shift(26)
        informative15M['ICH_CS_LOW_15M'] = informative15M['low'].shift(26)
        informative15M['ICH_CS_KS_15M'] = informative15M['ICH_KS_15M'].shift(26)
        informative15M['ICH_CS_TS_15M'] = informative15M['ICH_TS_15M'].shift(26)
        informative15M['ICH_CS_SSA_15M'] = informative15M['ICH_SSA_15M'].shift(26)
        informative15M['ICH_CS_SSB_15M'] = informative15M['ICH_SSB_15M'].shift(26)

        #Ichimoku calculations for the current pair in 30m
        #informative30M['ICH_SSB_30M'] = taichi.trend.ichimoku_b(informative30M['high'], informative30M['low'], window2=26, window3=52).shift(26)
        #informative30M['ICH_SSA_30M'] = taichi.trend.ichimoku_a(informative30M['high'], informative30M['low'], window1=9, window2=26).shift(26)
        #informative30M['ICH_KS_30M'] = taichi.trend.ichimoku_base_line(informative30M['high'], informative30M['low'])
        #informative30M['ICH_TS_30M'] = taichi.trend.ichimoku_conversion_line(informative30M['high'], informative30M['low'])
        #informative30M['ICH_CS_30M'] = informative30M['close']
        #informative30M['ICH_CS_HIGH_30M'] = informative30M['high'].shift(26)
        #informative30M['ICH_CS_LOW_30M'] = informative30M['low'].shift(26)
        #informative30M['ICH_CS_KS_30M'] = informative30M['ICH_KS_30M'].shift(26)
        #informative30M['ICH_CS_TS_30M'] = informative30M['ICH_TS_30M'].shift(26)
        #informative30M['ICH_CS_SSA_30M'] = informative30M['ICH_SSA_30M'].shift(26)
        #informative30M['ICH_CS_SSB_30M'] = informative30M['ICH_SSB_30M'].shift(26)

        #Ichimoku calculations for the current pair in 1h
        #informative1H['ICH_SSB_1H'] = taichi.trend.ichimoku_b(informative1H['high'], informative1H['low'], window2=26, window3=52).shift(26)
        #informative1H['ICH_SSA_1H'] = taichi.trend.ichimoku_a(informative1H['high'], informative1H['low'], window1=9, window2=26).shift(26)
        #informative1H['ICH_KS_1H'] = taichi.trend.ichimoku_base_line(informative1H['high'], informative1H['low'])
        #informative1H['ICH_TS_1H'] = taichi.trend.ichimoku_conversion_line(informative1H['high'], informative1H['low'])
        #informative1H['ICH_CS_1H'] = informative1H['close']
        #informative1H['ICH_CS_HIGH_1H'] = informative1H['high'].shift(26)
        #informative1H['ICH_CS_LOW_1H'] = informative1H['low'].shift(26)
        #informative1H['ICH_CS_KS_1H'] = informative1H['ICH_KS_1H'].shift(26)
        #informative1H['ICH_CS_TS_1H'] = informative1H['ICH_TS_1H'].shift(26)
        #informative1H['ICH_CS_SSA_1H'] = informative1H['ICH_SSA_1H'].shift(26)
        #informative1H['ICH_CS_SSB_1H'] = informative1H['ICH_SSB_1H'].shift(26)

        #Ichimoku calculations for the current pair in 4h
        #informative4H['ICH_SSB_4H'] = taichi.trend.ichimoku_b(informative4H['high'], informative4H['low'], window2=26, window3=52).shift(26)
        #informative4H['ICH_SSA_4H'] = taichi.trend.ichimoku_a(informative4H['high'], informative4H['low'], window1=9, window2=26).shift(26)
        #informative4H['ICH_KS_4H'] = taichi.trend.ichimoku_base_line(informative4H['high'], informative4H['low'])
        #informative4H['ICH_TS_4H'] = taichi.trend.ichimoku_conversion_line(informative4H['high'], informative4H['low'])
        #informative4H['ICH_CS_4H'] = informative4H['close']
        #informative4H['ICH_CS_HIGH_4H'] = informative4H['high'].shift(26)
        #informative4H['ICH_CS_LOW_4H'] = informative4H['low'].shift(26)
        #informative4H['ICH_CS_KS_4H'] = informative4H['ICH_KS_4H'].shift(26)
        #informative4H['ICH_CS_TS_4H'] = informative4H['ICH_TS_4H'].shift(26)
        #informative4H['ICH_CS_SSA_4H'] = informative4H['ICH_SSA_4H'].shift(26)
        #informative4H['ICH_CS_SSB_4H'] = informative4H['ICH_SSB_4H'].shift(26)

        #Ichimoku calculations for the strategy's timeframe
        dataframe['ICH_SSB'] = taichi.trend.ichimoku_b(dataframe['high'], dataframe['low'], window2=26, window3=52).shift(26)
        dataframe['ICH_SSA'] = taichi.trend.ichimoku_a(dataframe['high'], dataframe['low'], window1=9, window2=26).shift(26)
        dataframe['ICH_KS'] = taichi.trend.ichimoku_base_line(dataframe['high'], dataframe['low'])
        dataframe['ICH_TS'] = taichi.trend.ichimoku_conversion_line(dataframe['high'], dataframe['low'])
        dataframe['ICH_CS'] = dataframe['close']
        dataframe['ICH_CS_HIGH'] = dataframe['high'].shift(26)
        dataframe['ICH_CS_LOW'] = dataframe['low'].shift(26)
        dataframe['ICH_CS_KS'] = dataframe['ICH_KS'].shift(26)
        dataframe['ICH_CS_TS'] = dataframe['ICH_TS'].shift(26)
        dataframe['ICH_CS_SSA'] = dataframe['ICH_SSA'].shift(26)
        dataframe['ICH_CS_SSB'] = dataframe['ICH_SSB'].shift(26)

        # RSI
        dataframe['rsi'] = ta.RSI(dataframe)

        #log_to_results(dataframe.to_string())

        return dataframe
    
    def populate_entry_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:

        global informativeBTC1M
        global informativeBTC5M
        #global informativeBTC15M
        #global informativeBTC30M
        #global informativeBTC1H
        #global informativeBTC4H
        #global informative1M
        global informative5M
        global informative15M
        #global informative30M
        #global informative1H
        #global informative4H

        dataframe.loc[
            (   
                #Conditions for the current asset being calculated in the strategy's timeframe
                (dataframe['close'] > dataframe['open'])
                & (dataframe['close'] > dataframe['ICH_SSA'])
                & (dataframe['close'] > dataframe['ICH_SSB'])
                & (dataframe['close'] > dataframe['ICH_KS'])
                & (dataframe['close'] > dataframe['ICH_TS'])
                & (dataframe['open'] > dataframe['ICH_SSA'])
                & (dataframe['open'] > dataframe['ICH_SSB'])
                & (dataframe['open'] > dataframe['ICH_KS'])
                & (dataframe['open'] > dataframe['ICH_TS'])
                & (dataframe['ICH_CS'] > dataframe['ICH_CS_HIGH'])
                & (dataframe['ICH_CS'] > dataframe['ICH_CS_SSA'])
                & (dataframe['ICH_CS'] > dataframe['ICH_CS_SSB'])
                & (dataframe['ICH_CS'] > dataframe['ICH_CS_TS'])
                & (dataframe['ICH_CS'] > dataframe['ICH_CS_KS'])

                & (informative5M['close'] > informative5M['open'])
                & (informative5M['close'] > informative5M['ICH_SSA_5M'])
                & (informative5M['close'] > informative5M['ICH_SSB_5M'])
                & (informative5M['close'] > informative5M['ICH_TS_5M'])
                & (informative5M['close'] > informative5M['ICH_KS_5M'])
                & (informative5M['ICH_CS_5M'] > informative5M['ICH_CS_HIGH_5M'])
                & (informative5M['ICH_CS_5M'] > informative5M['ICH_CS_SSA_5M'])
                & (informative5M['ICH_CS_5M'] > informative5M['ICH_CS_SSB_5M'])
                & (informative5M['ICH_CS_5M'] > informative5M['ICH_CS_TS_5M'])
                & (informative5M['ICH_CS_5M'] > informative5M['ICH_CS_KS_5M'])

                & (informative15M['close'] > informative15M['open'])
                & (informative15M['close'] > informative15M['ICH_SSA_15M'])
                & (informative15M['close'] > informative15M['ICH_SSB_15M'])
                & (informative15M['close'] > informative15M['ICH_TS_15M'])
                & (informative15M['close'] > informative15M['ICH_KS_15M'])
                & (informative15M['ICH_CS_15M'] > informative15M['ICH_CS_HIGH_15M'])
                & (informative15M['ICH_CS_15M'] > informative15M['ICH_CS_SSA_15M'])
                & (informative15M['ICH_CS_15M'] > informative15M['ICH_CS_SSB_15M'])
                & (informative15M['ICH_CS_15M'] > informative15M['ICH_CS_TS_15M'])
                & (informative15M['ICH_CS_15M'] > informative15M['ICH_CS_KS_15M'])

                & (informativeBTC1M['close'] > informativeBTC1M['open'])
                & (informativeBTC1M['close'] > informativeBTC1M['BTC_ICH_SSA_1M'])
                & (informativeBTC1M['close'] > informativeBTC1M['BTC_ICH_SSB_1M'])
                & (informativeBTC1M['close'] > informativeBTC1M['BTC_ICH_TS_1M'])
                & (informativeBTC1M['close'] > informativeBTC1M['BTC_ICH_KS_1M'])
                & (informativeBTC1M['BTC_ICH_CS_1M'] > informativeBTC1M['BTC_ICH_CS_KS_1M'])
                & (informativeBTC1M['BTC_ICH_CS_1M'] > informativeBTC1M['BTC_ICH_CS_TS_1M'])
                & (informativeBTC1M['BTC_ICH_CS_1M'] > informativeBTC1M['BTC_ICH_CS_SSA_1M'])
                & (informativeBTC1M['BTC_ICH_CS_1M'] > informativeBTC1M['BTC_ICH_CS_SSB_1M'])
                & (informativeBTC1M['BTC_ICH_CS_1M'] > informativeBTC1M['BTC_ICH_CS_HIGH_1M'])

                & (informativeBTC5M['close'] > informativeBTC5M['open'])
                & (informativeBTC5M['close'] > informativeBTC1M['BTC_ICH_CS_SSA_5M'])
                & (informativeBTC5M['close'] > informativeBTC1M['BTC_ICH_CS_SSB_5M'])
                & (informativeBTC5M['close'] > informativeBTC1M['BTC_ICH_CS_TS_5M'])
                & (informativeBTC5M['close'] > informativeBTC1M['BTC_ICH_CS_KS_5M'])
                & (informativeBTC5M['BTC_ICH_CS_5M'] > informativeBTC5M['BTC_ICH_CS_KS_5M'])
                & (informativeBTC5M['BTC_ICH_CS_5M'] > informativeBTC5M['BTC_ICH_CS_TS_5M'])
                & (informativeBTC5M['BTC_ICH_CS_5M'] > informativeBTC5M['BTC_ICH_CS_SSA_5M'])
                & (informativeBTC5M['BTC_ICH_CS_5M'] > informativeBTC5M['BTC_ICH_CS_SSB_5M'])
                & (informativeBTC5M['BTC_ICH_CS_5M'] > informativeBTC5M['BTC_ICH_CS_HIGH_5M'])
            ),
            'enter_long'] = 1

        dataframe.loc[
            (   
                (dataframe['close'] < dataframe['open'])
                & (dataframe['close'] < dataframe['ICH_SSA'])
                & (dataframe['close'] < dataframe['ICH_SSB'])
                & (dataframe['close'] < dataframe['ICH_KS'])
                & (dataframe['close'] < dataframe['ICH_TS'])
                & (dataframe['open'] < dataframe['ICH_SSA'])
                & (dataframe['open'] < dataframe['ICH_SSB'])
                & (dataframe['open'] < dataframe['ICH_KS'])
                & (dataframe['open'] < dataframe['ICH_TS'])
                & (dataframe['ICH_CS'] < dataframe['ICH_CS_LOW'])
                & (dataframe['ICH_CS'] < dataframe['ICH_CS_SSA'])
                & (dataframe['ICH_CS'] < dataframe['ICH_CS_SSB'])
                & (dataframe['ICH_CS'] < dataframe['ICH_CS_TS'])
                & (dataframe['ICH_CS'] < dataframe['ICH_CS_KS'])

                & (informative5M['close'] < informative5M['open'])
                & (informative5M['close'] < informative5M['ICH_SSA_5M'])
                & (informative5M['close'] < informative5M['ICH_SSB_5M'])
                & (informative5M['close'] < informative5M['ICH_TS_5M'])
                & (informative5M['close'] < informative5M['ICH_KS_5M'])

                & (informative5M['ICH_CS_5M'] < informative5M['ICH_CS_LOW_5M'])
                & (informative5M['ICH_CS_5M'] < informative5M['ICH_CS_SSA_5M'])
                & (informative5M['ICH_CS_5M'] < informative5M['ICH_CS_SSB_5M'])
                & (informative5M['ICH_CS_5M'] < informative5M['ICH_CS_TS_5M'])
                & (informative5M['ICH_CS_5M'] < informative5M['ICH_CS_KS_5M'])

                & (informative15M['close'] < informative15M['open'])
                & (informative15M['close'] < informative15M['ICH_SSA_15M'])
                & (informative15M['close'] < informative15M['ICH_SSB_15M'])
                & (informative15M['close'] < informative15M['ICH_TS_15M'])
                & (informative15M['close'] < informative15M['ICH_KS_15M'])
                & (informative15M['ICH_CS_15M'] < informative15M['ICH_CS_LOW_15M'])
                & (informative15M['ICH_CS_15M'] < informative15M['ICH_CS_SSA_15M'])
                & (informative15M['ICH_CS_15M'] < informative15M['ICH_CS_SSB_15M'])
                & (informative15M['ICH_CS_15M'] < informative15M['ICH_CS_TS_15M'])
                & (informative15M['ICH_CS_15M'] < informative15M['ICH_CS_KS_15M'])

                & (informativeBTC1M['close'] < informativeBTC1M['open'])
                & (informativeBTC1M['BTC_ICH_CS_1M'] < informativeBTC1M['BTC_ICH_CS_KS_1M'])
                & (informativeBTC1M['BTC_ICH_CS_1M'] < informativeBTC1M['BTC_ICH_CS_TS_1M'])
                & (informativeBTC1M['BTC_ICH_CS_1M'] < informativeBTC1M['BTC_ICH_CS_SSA_1M'])
                & (informativeBTC1M['BTC_ICH_CS_1M'] < informativeBTC1M['BTC_ICH_CS_SSB_1M'])
                & (informativeBTC1M['BTC_ICH_CS_1M'] < informativeBTC1M['BTC_ICH_CS_LOW_1M'])

                & (informativeBTC5M['close'] < informativeBTC5M['open'])
                & (informativeBTC5M['BTC_ICH_CS_5M'] < informativeBTC5M['BTC_ICH_CS_KS_5M'])
                & (informativeBTC5M['BTC_ICH_CS_5M'] < informativeBTC5M['BTC_ICH_CS_TS_5M'])
                & (informativeBTC5M['BTC_ICH_CS_5M'] < informativeBTC5M['BTC_ICH_CS_SSA_5M'])
                & (informativeBTC5M['BTC_ICH_CS_5M'] < informativeBTC5M['BTC_ICH_CS_SSB_5M'])
                & (informativeBTC5M['BTC_ICH_CS_5M'] < informativeBTC5M['BTC_ICH_CS_LOW_5M'])

            ),
            'enter_short'] = 1

        return dataframe

    def populate_exit_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:

        global informativeBTC1M
        global informativeBTC5M
        #global informativeBTC15M
        #global informativeBTC30M
        #global informativeBTC1H
        #global informativeBTC4H
        #global informative1M
        global informative5M
        global informative15M
        #global informative30M
        #global informative1H
        #global informative4H

        """
        dataframe.loc[
            (
                #(dataframe['close'] < dataframe['open'])
                #(dataframe['close'] < dataframe['ICH_SSA'])
                #| (dataframe['close'] < dataframe['ICH_SSB'])
                (dataframe['close'] < dataframe['ICH_KS'])
                #| (dataframe['close'] < dataframe['ICH_TS'])
            ),
            'exit_long'] = 1

        dataframe.loc[
            (
                #(dataframe['close'] > dataframe['open'])
                #(dataframe['close'] > dataframe['ICH_SSA'])
                #| (dataframe['close'] > dataframe['ICH_SSB'])
                (dataframe['close'] > dataframe['ICH_KS'])
                #| (dataframe['close'] > dataframe['ICH_TS'])
            ),
            'exit_short'] = 1
        """

        return dataframe
