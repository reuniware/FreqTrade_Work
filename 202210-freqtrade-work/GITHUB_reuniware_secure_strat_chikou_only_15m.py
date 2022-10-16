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
class SampleStrategy(IStrategy):
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
        "0": 0.02,
    }

    # Optimal stoploss designed for the strategy.
    # This attribute will be overridden if the config file contains "stoploss".
    stoploss = -0.25/3

    # Trailing stoploss
    trailing_stop = False
    # trailing_only_offset_is_reached = False
    trailing_stop_positive = 0.01
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
        'entry': 'GTC',
        'exit': 'GTC'
    }

    def informative_pairs(self):
        return []

    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:

        #log_to_results("populate_indicators" + str(metadata))

        dataframe['ICH_SSB'] = taichi.trend.ichimoku_b(dataframe['high'], dataframe['low'], window2=26, window3=52).shift(26)
        dataframe['ICH_SSA'] = taichi.trend.ichimoku_a(dataframe['high'], dataframe['low'], window1=9, window2=26).shift(26)
        #print(dataframe['ICH_SSA'])
        dataframe['ICH_KS'] = taichi.trend.ichimoku_base_line(dataframe['high'], dataframe['low'])
        #print(dataframe['ICH_KS'])
        dataframe['ICH_TS'] = taichi.trend.ichimoku_conversion_line(dataframe['high'], dataframe['low'])
        #print(dataframe['ICH_TS'])
        dataframe['ICH_CS'] = dataframe['close'].shift(26)

        # RSI
        dataframe['rsi'] = ta.RSI(dataframe)

        return dataframe

    def populate_entry_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:

        dataframe.loc[
            (   
                (dataframe['ICH_CS'].shift(1) < dataframe['ICH_SSB'].shift(27))
                & (dataframe['ICH_CS']) > dataframe['ICH_SSB'].shift(26)
            ),
            'enter_long'] = 1

        dataframe.loc[
            (   
                (dataframe['close'].shift(1) > dataframe['ICH_SSB'].shift(27))
                & (dataframe['close']) < dataframe['ICH_SSB'].shift(26)
            ),
            'enter_short'] = 1

        #log_to_results(str(metadata))
        #log_to_results(str(dataframe))

        #dataframe.loc[
            #( -
            #    (qtpylib.crossed_above(dataframe['ICH_KS'], dataframe['ICH_TS']))
            #),
            #'enter_short'] = 1

        return dataframe

    def populate_exit_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        #dataframe.loc[
        #    (
        #        # Signal: RSI crosses above 70
        #        (qtpylib.crossed_below(dataframe['close'], dataframe['ICH_KS']))
        #    ),

        #    'exit_long'] = 1

        #dataframe.loc[
        #    (
                # Signal: RSI crosses above 70
        #        (qtpylib.crossed_above(dataframe['ICH_TS'], dataframe['ICH_KS']))
        #    ),

        #    'exit_short'] = 1


        return dataframe

      
#tested from 20220801-20221006
#
#=================== SUMMARY METRICS ====================
#| Metric                      | Value                  |
#|-----------------------------+------------------------|
#| Backtesting from            | 2022-08-01 00:00:00    |
#| Backtesting to              | 2022-10-06 00:00:00    |
#| Max open trades             | 2                      |
#|                             |                        |
#| Total/Daily Avg Trades      | 96 / 1.45              |
#| Starting balance            | 1000 USDT              |
#| Final balance               | 1151.042 USDT          |
#| Absolute profit             | 151.042 USDT           |
#| Total profit %              | 15.10%                 |
#| CAGR %                      | 117.70%                |
#| Profit factor               | 1.22                   |
#| Trades per day              | 1.45                   |
#| Avg. daily profit %         | 0.23%                  |
#| Avg. stake amount           | 497.265 USDT           |
#| Total trade volume          | 47737.449 USDT         |
#|                             |                        |
#| Long / Short                | 2 / 94                 |
#| Total profit Long %         | -3.40%                 |
#| Total profit Short %        | 18.50%                 |
#| Absolute profit Long        | -33.953 USDT           |
#| Absolute profit Short       | 184.995 USDT           |
#|                             |                        |
#| Best Pair                   | TRYB/USDT:USDT 15.09%  |
#| Worst Pair                  | MELON/USDT:USDT -2.07% |
#| Best trade                  | TRYB/USDT:USDT 3.30%   |
#| Worst trade                 | KNC/USDT:USDT -8.59%   |
#| Best day                    | 54.496 USDT            |
#| Worst day                   | -78.671 USDT           |
#| Days win/draw/lose          | 28 / 27 / 12           |
#| Avg. Duration Winners       | 1 day, 3:05:00         |
#| Avg. Duration Loser         | 2 days, 8:26:00        |
#| Rejected Entry signals      | 1697585                |
#| Entry/Exit Timeouts         | 65 / 155               |
#|                             |                        |
#| Min balance                 | 912.141 USDT           |
#| Max balance                 | 1202.695 USDT          |
#| Max % of account underwater | 12.90%                 |
#| Absolute Drawdown (Account) | 12.90%                 |
#| Absolute Drawdown           | 135.05 USDT            |
#| Drawdown high               | 47.192 USDT            |
#| Drawdown low                | -87.859 USDT           |
#| Drawdown Start              | 2022-08-02 09:45:00    |
#| Drawdown End                | 2022-08-24 00:15:00    |
#| Market change               | -20.11%                |
#========================================================
#
# freqtrade backtesting -c config-gateio.json -s SampleStrategy --timeframe=15m --timerange=20220801-20221006
