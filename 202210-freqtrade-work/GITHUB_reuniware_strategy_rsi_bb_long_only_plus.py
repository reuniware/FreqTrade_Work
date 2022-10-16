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
    stoploss = -0.25/16

    # Trailing stoploss
    trailing_stop = False
    # trailing_only_offset_is_reached = False
    trailing_stop_positive = 0.01
    # trailing_stop_positive_offset = 0.0  # Disabled / not configured

    # Optimal timeframe for the strategy.
    timeframe = '1h'

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
        dataframe['rsi'] = ta.RSI(dataframe, timeperiod=14)

        # Définition de l'indicateur Bollinger
        bollinger = qtpylib.bollinger_bands(qtpylib.typical_price(dataframe), window=20, stds=2)
        # Ajout de la bande supérieure
        dataframe['bb_lowerband'] = bollinger['lower'] 

        return dataframe

    def populate_entry_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:

        dataframe.loc[
            (
                # Lorsque le RSI est inférieur à 30
                (dataframe['rsi'] < 30) &
                # Lorsque la clôture du cours est sous la bande inférieure
                (dataframe['close'] < dataframe['bb_lowerband'])
            ),
            'enter_long'] = 1

        #log_to_results(str(metadata))
        #log_to_results(str(dataframe))

        #dataframe.loc[
            #( -
            #    (qtpylib.crossed_above(dataframe['ICH_KS'], dataframe['ICH_TS']))
            #),
            #'enter_short'] = 1

        return dataframe

    def populate_exit_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe.loc[
            (
                # Sortie lorsque le RSI est supérieur à 70
                (dataframe['rsi'] > 70)
            ),
            'exit_long'] = 1

        #dataframe.loc[
        #    (
                # Signal: RSI crosses above 70
        #        (qtpylib.crossed_above(dataframe['ICH_TS'], dataframe['ICH_KS']))
        #    ),

        #    'exit_short'] = 1


        return dataframe

# =================== SUMMARY METRICS ===================
# | Metric                      | Value                 |
# |-----------------------------+-----------------------|
# | Backtesting from            | 2022-07-01 00:00:00   |
# | Backtesting to              | 2022-10-06 00:00:00   |
# | Max open trades             | 2                     |
# |                             |                       |
# | Total/Daily Avg Trades      | 364 / 3.75            |
# | Starting balance            | 1000 USDT             | ***
# | Final balance               | 4104.658 USDT         | ***
# | Absolute profit             | 3104.658 USDT         | ***
# | Total profit %              | 310.47%               |
# | CAGR %                      | 20209.14%             |
# | Profit factor               | 1.93                  |
# | Trades per day              | 3.75                  |
# | Avg. daily profit %         | 3.20%                 |
# | Avg. stake amount           | 1080.33 USDT          |
# | Total trade volume          | 393240.089 USDT       |
# |                             |                       |
# | Best Pair                   | ROOK/USDT:USDT 45.61% |
# | Worst Pair                  | ALCX/USDT:USDT -9.83% |
# | Best trade                  | WSB/USDT:USDT 16.22%  |
# | Worst trade                 | WSB/USDT:USDT -5.64%  |
# | Best day                    | 275.836 USDT          |
# | Worst day                   | -159.5 USDT           |
# | Days win/draw/lose          | 67 / 5 / 26           |
# | Avg. Duration Winners       | 10:30:00              |
# | Avg. Duration Loser         | 8:44:00               |
# | Rejected Entry signals      | 493286                |
# | Entry/Exit Timeouts         | 166 / 333             |
# |                             |                       |
# | Min balance                 | 992.397 USDT          |
# | Max balance                 | 4105.452 USDT         |
# | Max % of account underwater | 12.24%                |
# | Absolute Drawdown (Account) | 12.24%                |
# | Absolute Drawdown           | 295.254 USDT          |
# | Drawdown high               | 1412.892 USDT         |
# | Drawdown low                | 1117.639 USDT         |
# | Drawdown Start              | 2022-08-18 18:00:00   |
# | Drawdown End                | 2022-08-19 21:00:00   |
# | Market change               | -1.21%                |
# =======================================================

# freqtrade backtesting -c config-gateio.json -s SampleStrategy --timeframe=1h --timerange=20220701-20221006

# Good stoploss !! = 0.015625 !!
