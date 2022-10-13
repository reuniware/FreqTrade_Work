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
class StratIchimoku003(IStrategy):
    delete_log_results()

    # Strategy interface version - allow new iterations of the strategy interface.
    # Check the documentation or the Sample strategy to get the latest version.
    INTERFACE_VERSION = 3

    # Can this strategy go short?
    can_short: bool = True

    #roi0 = RealParameter(0.01, 0.09, decimals=1, default=0.04, space="buy")

    # Minimal ROI designed for the strategy.
    # This attribute will be overridden if the config file contains "minimal_roi".
    minimal_roi = {
        #"60": 0.01,
        #"30": 0.01,
        "0": 0.02
    }

    # Optimal stoploss designed for the strategy.
    # This attribute will be overridden if the config file contains "stoploss".
    stoploss = -0.25

    # Trailing stoploss
    trailing_stop = False
    # trailing_only_offset_is_reached = False
    trailing_stop_positive = 0.0025
    # trailing_stop_positive_offset = 0.0  # Disabled / not configured

    # Optimal timeframe for the strategy.
    timeframe = '15m'

    # Run "populate_indicators()" only for new candle.
    process_only_new_candles = True

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
        #pairs = self.dp.current_whitelist()
        # Assign tf to each pair so they can be downloaded and cached for strategy.
        #informative_pairs = [(pair, '1h') for pair in pairs]
        # Optionally Add additional "static" pairs
        informative_pairs = [("BTC/USDT:USDT", "1h"), ("BTC/USDT:USDT", "4h"),]
        return informative_pairs

    informative1H : DataFrame
    informative4H : DataFrame

    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:

        global informative1H
        global informative4H

        #if not self.dp:
            # Don't do anything if DataProvider is not available.
            #return dataframe

        inf_tf = '1h'
        informative1H = self.dp.get_pair_dataframe(pair="BTC/USDT:USDT", timeframe=inf_tf)
        inf_tf = '4h'
        informative4H = self.dp.get_pair_dataframe(pair="BTC/USDT:USDT", timeframe=inf_tf)

        #Ichimoku calculations for the BTC in 1h
        informative1H['BTC_ICH_SSB_1H'] = taichi.trend.ichimoku_b(informative1H['high'], informative1H['low'], window2=26, window3=52).shift(26)
        informative1H['BTC_ICH_SSA_1H'] = taichi.trend.ichimoku_a(informative1H['high'], informative1H['low'], window1=9, window2=26).shift(26)
        informative1H['BTC_ICH_KS_1H'] = taichi.trend.ichimoku_base_line(informative1H['high'], informative1H['low'])
        informative1H['BTC_ICH_TS_1H'] = taichi.trend.ichimoku_conversion_line(informative1H['high'], informative1H['low'])
        informative1H['BTC_ICH_CS_1H'] = informative1H['close']
        informative1H['BTC_ICH_CS_HIGH_1H'] = informative1H['high'].shift(26)
        informative1H['BTC_ICH_CS_LOW_1H'] = informative1H['low'].shift(26)
        informative1H['BTC_ICH_CS_KS_1H'] = informative1H['BTC_ICH_KS_1H'].shift(26)
        informative1H['BTC_ICH_CS_TS_1H'] = informative1H['BTC_ICH_TS_1H'].shift(26)
        informative1H['BTC_ICH_CS_SSA_1H'] = informative1H['BTC_ICH_SSA_1H'].shift(26)
        informative1H['BTC_ICH_CS_SSB_1H'] = informative1H['BTC_ICH_SSB_1H'].shift(26)

        #Ichimoku calculations for the BTC in 4h
        informative4H['BTC_ICH_SSB_4H'] = taichi.trend.ichimoku_b(informative4H['high'], informative4H['low'], window2=26, window3=52).shift(26)
        informative4H['BTC_ICH_SSA_4H'] = taichi.trend.ichimoku_a(informative4H['high'], informative4H['low'], window1=9, window2=26).shift(26)
        informative4H['BTC_ICH_KS_4H'] = taichi.trend.ichimoku_base_line(informative4H['high'], informative4H['low'])
        informative4H['BTC_ICH_TS_4H'] = taichi.trend.ichimoku_conversion_line(informative4H['high'], informative4H['low'])
        informative4H['BTC_ICH_CS_4H'] = informative4H['close']
        informative4H['BTC_ICH_CS_HIGH_4H'] = informative4H['high'].shift(26)
        informative4H['BTC_ICH_CS_LOW_4H'] = informative4H['low'].shift(26)
        informative4H['BTC_ICH_CS_KS_4H'] = informative4H['BTC_ICH_KS_4H'].shift(26)
        informative4H['BTC_ICH_CS_TS_4H'] = informative4H['BTC_ICH_TS_4H'].shift(26)
        informative4H['BTC_ICH_CS_SSA_4H'] = informative4H['BTC_ICH_SSA_4H'].shift(26)
        informative4H['BTC_ICH_CS_SSB_4H'] = informative4H['BTC_ICH_SSB_4H'].shift(26)

        #log_to_results(informative4H.to_string())

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

        global informative1H
        global informative4H

        dataframe.loc[
            (   
                (dataframe['ICH_CS'] > dataframe['ICH_CS_HIGH'])
                & (dataframe['ICH_CS'] > dataframe['ICH_CS_KS'])
                & (dataframe['ICH_CS'] > dataframe['ICH_CS_TS'])
                & (dataframe['ICH_CS'] > dataframe['ICH_CS_SSA'])
                & (dataframe['ICH_CS'] > dataframe['ICH_CS_SSB'])

                & (informative1H['BTC_ICH_CS_1H'] > informative1H['BTC_ICH_CS_HIGH_1H'])
                & (informative1H['BTC_ICH_CS_1H'] > informative1H['BTC_ICH_CS_KS_1H'])
                & (informative1H['BTC_ICH_CS_1H'] > informative1H['BTC_ICH_CS_TS_1H'])
                & (informative1H['BTC_ICH_CS_1H'] > informative1H['BTC_ICH_CS_SSA_1H'])
                & (informative1H['BTC_ICH_CS_1H'] > informative1H['BTC_ICH_CS_SSB_1H'])

                & (informative4H['BTC_ICH_CS_4H'] > informative4H['BTC_ICH_CS_HIGH_4H'])
                & (informative4H['BTC_ICH_CS_4H'] > informative4H['BTC_ICH_CS_KS_4H'])
                & (informative4H['BTC_ICH_CS_4H'] > informative4H['BTC_ICH_CS_TS_4H'])
                & (informative4H['BTC_ICH_CS_4H'] > informative4H['BTC_ICH_CS_SSA_4H'])
                & (informative4H['BTC_ICH_CS_4H'] > informative4H['BTC_ICH_CS_SSB_4H'])

                & (
                    (informative4H['BTC_ICH_SSB_4H'] > informative4H['BTC_ICH_SSA_4H'])
                    & (informative4H['open'] < informative4H['BTC_ICH_SSB_4H'])
                    & (informative4H['close'] > informative4H['BTC_ICH_SSB_4H'])
                    & (informative4H['close'] > informative4H['BTC_ICH_KS_4H'])
                    & (informative4H['close'] > informative4H['BTC_ICH_TS_4H'])
                )

            ),
            'enter_long'] = 1

        dataframe.loc[
            (   
                (dataframe['ICH_CS'] < dataframe['ICH_CS_LOW'])
                & (dataframe['ICH_CS'] < dataframe['ICH_CS_KS'])
                & (dataframe['ICH_CS'] < dataframe['ICH_CS_TS'])
                & (dataframe['ICH_CS'] < dataframe['ICH_CS_SSA'])
                & (dataframe['ICH_CS'] < dataframe['ICH_CS_SSB'])
                & (
                    (dataframe['ICH_SSB'] < dataframe['ICH_SSA'])
                    & (dataframe['open'] > dataframe['ICH_SSB'])
                    & (dataframe['close'] < dataframe['ICH_SSB'])
                    & (dataframe['close'] < dataframe['ICH_KS'])
                    & (dataframe['close'] < dataframe['ICH_TS'])
                )
                & (informative1H['BTC_ICH_CS_1H'] < informative1H['BTC_ICH_CS_LOW_1H'])
                & (informative1H['BTC_ICH_CS_1H'] < informative1H['BTC_ICH_CS_KS_1H'])
                & (informative1H['BTC_ICH_CS_1H'] < informative1H['BTC_ICH_CS_TS_1H'])
                & (informative1H['BTC_ICH_CS_1H'] < informative1H['BTC_ICH_CS_SSA_1H'])
                & (informative1H['BTC_ICH_CS_1H'] < informative1H['BTC_ICH_CS_SSB_1H'])

                & (informative4H['BTC_ICH_CS_4H'] < informative4H['BTC_ICH_CS_LOW_4H'])
                & (informative4H['BTC_ICH_CS_4H'] < informative4H['BTC_ICH_CS_KS_4H'])
                & (informative4H['BTC_ICH_CS_4H'] < informative4H['BTC_ICH_CS_TS_4H'])
                & (informative4H['BTC_ICH_CS_4H'] < informative4H['BTC_ICH_CS_SSA_4H'])
                & (informative4H['BTC_ICH_CS_4H'] < informative4H['BTC_ICH_CS_SSB_4H'])

                & (
                    (informative4H['BTC_ICH_SSB_4H'] < informative4H['BTC_ICH_SSA_4H'])
                    & (informative4H['open'] > informative4H['BTC_ICH_SSB_4H'])
                    & (informative4H['close'] < informative4H['BTC_ICH_SSB_4H'])
                    & (informative4H['close'] < informative4H['BTC_ICH_KS_4H'])
                    & (informative4H['close'] < informative4H['BTC_ICH_TS_4H'])
                )

            ),
            'enter_short'] = 1

        return dataframe

    def populate_exit_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        #dataframe.loc[
        #    (
        #        # Signal: RSI crosses above 70
        #        #(qtpylib.crossed_below(dataframe['close'], dataframe['ICH_KS']))
        #        #dataframe['close'] >= dataframe['open'] + dataframe['open']/100*(0.125/2)
        #    ),
        #    'exit_long'] = 1
        
        #dataframe.loc[
        #    (
        #       # Signal: RSI crosses above 70
        #        #(qtpylib.crossed_above(dataframe['ICH_TS'], dataframe['ICH_KS']))
        #        #dataframe['close'] <= dataframe['open'] - dataframe['open']/100*(0.125/2)
        #    ),
        #    'exit_short'] = 1

        return dataframe
