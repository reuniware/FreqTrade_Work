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
class TenkanBollinger03(IStrategy):
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
        "0": 0.50
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
    timeframe = '12h'

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
        return []


    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:

        if self.dp.runmode.value in ('live', 'dry_run'):
            ticker = self.dp.ticker(metadata['pair'])
            dataframe['last_open'] = ticker['open']
            dataframe['last_high'] = ticker['high']
            dataframe['last_low'] = ticker['low']
            dataframe['last_close'] = ticker['close']
            #log_to_results(str(ticker))

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

        # Définition de l'indicateur Bollinger
        bollinger = qtpylib.bollinger_bands(qtpylib.typical_price(dataframe), window=20, stds=2)
        # Ajout de la bande supérieure
        dataframe['bb_lowerband'] = bollinger['lower'] 
        dataframe['bb_middleband'] = bollinger['mid']
        dataframe['bb_upperband'] = bollinger['upper']
        #log_to_results(dataframe.to_string())

        return dataframe
    
    def populate_entry_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:

        dataframe.loc[
            (   
                (dataframe['last_close'] > dataframe['last_open']) &
                (qtpylib.crossed_above(dataframe['ICH_TS'], dataframe['bb_middleband']))
            ),
            'enter_long'] = 1

        dataframe.loc[
            (   
                (dataframe['last_close'] < dataframe['last_open']) &
                (qtpylib.crossed_below(dataframe['ICH_TS'], dataframe['bb_middleband']))
            ),
            'enter_short'] = 1

        return dataframe

    def populate_exit_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:

        #dataframe.loc[
        #    (
        #        (qtpylib.crossed_below(dataframe['close'], dataframe['bb_lowerband']))
        #    ),
        #    'exit_long'] = 1

        #dataframe.loc[
        #    (
        #        (qtpylib.crossed_above(dataframe['close'], dataframe['bb_upperband']))
        #    ),
        #    'exit_short'] = 1

        return dataframe
