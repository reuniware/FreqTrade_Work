# pragma pylint: disable=missing-docstring, invalid-name, pointless-string-statement
# flake8: noqa: F401
# isort: skip_file
# --- Do not remove these libs ---
import numpy as np  # noqa
import pandas as pd  # noqa
from pandas import DataFrame
import os
from datetime import datetime
#import ccxt
#import sys

from freqtrade.strategy import (BooleanParameter, CategoricalParameter, DecimalParameter,
                                IStrategy, IntParameter, RealParameter)

from freqtrade.strategy import merge_informative_pair

# --------------------------------
# Add your lib to import here
#import talib.abstract as ta
#import freqtrade.vendor.qtpylib.indicators as qtpylib
#import ta as taichi
#from ta.volatility import BollingerBands
#from ta.utils import dropna

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
class Holding(IStrategy):
    delete_log_results()

    # Strategy interface version - allow new iterations of the strategy interface.
    # Check the documentation or the Sample strategy to get the latest version.
    INTERFACE_VERSION = 3

    # Can this strategy go short?
    can_short: bool = False

    # Minimal ROI designed for the strategy.
    # This attribute will be overridden if the config file contains "minimal_roi".
    minimal_roi = {
        #"60": 0.01,
        #"30": 0.01,
        "0": 0.99
    }

    # Optimal stoploss designed for the strategy.
    # This attribute will be overridden if the config file contains "stoploss".
    stoploss = -0.99

    # Trailing stoploss
    trailing_stop = False
    # trailing_only_offset_is_reached = False
    trailing_stop_positive = 0.0025
    # trailing_stop_positive_offset = 0.0  # Disabled / not configured

    # Optimal timeframe for the strategy.
    timeframe = '1d'

    # Run "populate_indicators()" only for new candle.
    process_only_new_candles = True

    # These values can be overridden in the config.
    use_exit_signal = True
    exit_profit_only = False
    ignore_roi_if_entry_signal = False

    # Number of candles the strategy requires before producing valid signals
    startup_candle_count: int = 0

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
        return []


    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:

        return dataframe
    
    def populate_entry_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:

        dataframe.loc[
            (   
                (dataframe['close'] != dataframe['close']) 
            ),
            'enter_long'] = 1

        dataframe.loc[
            (   
                (dataframe['close'] != dataframe['close']) 
            ),
            'enter_short'] = 1

        return dataframe

    def populate_exit_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:

        return dataframe
