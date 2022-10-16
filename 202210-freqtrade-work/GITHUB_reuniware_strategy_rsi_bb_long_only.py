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
    stoploss = -0.25

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

#=================== SUMMARY METRICS ===================
#| Metric                      | Value                 |
#|-----------------------------+-----------------------|
#| Backtesting from            | 2022-07-01 00:00:00   |
#| Backtesting to              | 2022-10-06 00:00:00   |
#| Max open trades             | 2                     |
#|                             |                       |
#| Total/Daily Avg Trades      | 131 / 1.35            |
#| Starting balance            | 1000 USDT             |
#| Final balance               | 2698.751 USDT         |
#| Absolute profit             | 1698.751 USDT         |
#| Total profit %              | 169.88%               |
#| CAGR %                      | 4091.96%              |
#| Profit factor               | 2.22                  |
#| Trades per day              | 1.35                  |
#| Avg. daily profit %         | 1.75%                 |
#| Avg. stake amount           | 918.419 USDT          |
#| Total trade volume          | 120312.861 USDT       |
#|                             |                       |
#| Best Pair                   | DEFI/USDT:USDT 41.84% |
#| Worst Pair                  | TRB/USDT:USDT -23.00% |
#| Best trade                  | WSB/USDT:USDT 16.22%  |
#| Worst trade                 | TRB/USDT:USDT -25.01% |
#| Best day                    | 238.663 USDT          |
#| Worst day                   | -258.538 USDT         |
#| Days win/draw/lose          | 48 / 41 / 9           |
#| Avg. Duration Winners       | 15:53:00              |
#| Avg. Duration Loser         | 5 days, 10:17:00      |
#| Rejected Entry signals      | 551992                |
#| Entry/Exit Timeouts         | 60 / 359              |
#|                             |                       |
#| Min balance                 | 1010.034 USDT         |
#| Max balance                 | 2699.274 USDT         |
#| Max % of account underwater | 24.46%                |
#| Absolute Drawdown (Account) | 24.46%                |
#| Absolute Drawdown           | 587.996 USDT          |
#| Drawdown high               | 1404.339 USDT         |
#| Drawdown low                | 816.343 USDT          |
#| Drawdown Start              | 2022-08-11 04:00:00   |
#| Drawdown End                | 2022-08-30 16:00:00   |
#| Market change               | -1.21%                |
#=======================================================
#
#freqtrade backtesting -c config-gateio.json -s SampleStrategy --timeframe=1h --timerange=20220701-20221006

