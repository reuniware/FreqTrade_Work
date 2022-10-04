# pragma pylint: disable=missing-docstring, invalid-name, pointless-string-statement
# flake8: noqa: F401
# isort: skip_file
# --- Do not remove these libs ---
import numpy as np  # noqa
import pandas as pd  # noqa
from pandas import DataFrame

from freqtrade.strategy import (BooleanParameter, CategoricalParameter, DecimalParameter,
                                IStrategy, IntParameter)

# --------------------------------
# Add your lib to import here
import talib.abstract as ta
import freqtrade.vendor.qtpylib.indicators as qtpylib
import ta as taichi


# This class is a sample. Feel free to customize it.
class SampleStrategy(IStrategy):
    """
    This is a sample strategy to inspire you.
    More information in https://www.freqtrade.io/en/latest/strategy-customization/

    You can:
        :return: a Dataframe with all mandatory indicators for the strategies
    - Rename the class name (Do not forget to update class_name)
    - Add any methods you want to build your strategy
    - Add any lib you need to build your strategy

    You must keep:
    - the lib in the section "Do not remove these libs"
    - the methods: populate_indicators, populate_entry_trend, populate_exit_trend
    You should keep:
    - timeframe, minimal_roi, stoploss, trailing_*
    """
    # Strategy interface version - allow new iterations of the strategy interface.
    # Check the documentation or the Sample strategy to get the latest version.
    INTERFACE_VERSION = 3

    # Can this strategy go short?
    can_short: bool = False

    # Minimal ROI designed for the strategy.
    # This attribute will be overridden if the config file contains "minimal_roi".
    minimal_roi = {
        "60": 0.01,
        "30": 0.02,
        "0": 0.04
    }

    # Optimal stoploss designed for the strategy.
    # This attribute will be overridden if the config file contains "stoploss".
    stoploss = -0.10

    # Trailing stoploss
    trailing_stop = False
    # trailing_only_offset_is_reached = False
    # trailing_stop_positive = 0.01
    # trailing_stop_positive_offset = 0.0  # Disabled / not configured

    # Optimal timeframe for the strategy.
    timeframe = '5m'

    # Run "populate_indicators()" only for new candle.
    process_only_new_candles = True

    # These values can be overridden in the config.
    use_exit_signal = True
    exit_profit_only = False
    ignore_roi_if_entry_signal = False

    # Hyperoptable parameters
    buy_rsi = IntParameter(low=1, high=50, default=30, space='buy', optimize=True, load=True)
    sell_rsi = IntParameter(low=50, high=100, default=70, space='sell', optimize=True, load=True)
    short_rsi = IntParameter(low=51, high=100, default=70, space='sell', optimize=True, load=True)
    exit_short_rsi = IntParameter(low=1, high=50, default=30, space='buy', optimize=True, load=True)

    # Number of candles the strategy requires before producing valid signals
    startup_candle_count: int = 52+26

    # Optional order type mapping.
    order_types = {
        'entry': 'limit',
        'exit': 'limit',
        'stoploss': 'market',
        'stoploss_on_exchange': False
    }

    # Optional order time in force.
    order_time_in_force = {
        'entry': 'GTC',
        'exit': 'GTC'
    }

    plot_config = {
        'main_plot': {
            'tema': {},
            'sar': {'color': 'white'},
        },
        'subplots': {
            "MACD": {
                'macd': {'color': 'blue'},
                'macdsignal': {'color': 'orange'},
            },
            "RSI": {
                'rsi': {'color': 'red'},
            }
        }
    }

    def informative_pairs(self):
        return []

    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:

        #print("populate_indicators", dataframe)

        dataframe['ICH_SSB'] = taichi.trend.ichimoku_b(dataframe['high'], dataframe['low'], window2=26, window3=52).shift(26)
        dataframe['ICH_SSA'] = taichi.trend.ichimoku_a(dataframe['high'], dataframe['low'], window1=9, window2=26).shift(26)
        # print(dataframe['ICH_SSA'])
        dataframe['ICH_KS'] = taichi.trend.ichimoku_base_line(dataframe['high'], dataframe['low'])
        # print(dataframe['ICH_KS'])
        dataframe['ICH_TS'] = taichi.trend.ichimoku_conversion_line(dataframe['high'], dataframe['low'])
        # print(dataframe['ICH_TS'])
        dataframe['ICH_CS'] = dataframe['close'].shift(-26)
        # print(dataframe['ICH_CS'])

        # RSI
        dataframe['rsi'] = ta.RSI(dataframe)

        return dataframe

    def populate_entry_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:

        dataframe.loc[
            (
                (qtpylib.crossed_above(dataframe['ICH_TS'], dataframe['ICH_KS']))
            ),
            'enter_long'] = 1

        dataframe.loc[
            (
                (qtpylib.crossed_above(dataframe['ICH_KS'], dataframe['ICH_TS']))
            ),
            'enter_short'] = 1

        return dataframe

    def populate_exit_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe.loc[
            (
                # Signal: RSI crosses above 70
                (qtpylib.crossed_above(dataframe['ICH_KS'], dataframe['ICH_TS']))
            ),

            'exit_long'] = 1

        dataframe.loc[
            (
                # Signal: RSI crosses above 70
                (qtpylib.crossed_above(dataframe['ICH_TS'], dataframe['ICH_KS']))
            ),

            'exit_short'] = 1


        return dataframe
