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
    stoploss = -0.25/8

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
        dataframe['rsi'] = ta.RSI(dataframe, timeperiod=14)

        # Définition de l'indicateur Bollinger
        bollinger = qtpylib.bollinger_bands(qtpylib.typical_price(dataframe), window=20, stds=2)
        # Ajout de la bande supérieure
        dataframe['bb_lowerband'] = bollinger['lower'] 
        dataframe['bb_middleband'] = bollinger['mid']
        dataframe['bb_upperband'] = bollinger['upper']
        return dataframe

    def populate_entry_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:

        dataframe.loc[
            (
                # Entrée long Lorsque le RSI est inférieur à 30
                (dataframe['rsi'] < 30) &
                # Lorsque la clôture du cours est sous la bande inférieure
                (dataframe['close'] < dataframe['bb_lowerband'])
            ),
            'enter_long'] = 1

        dataframe.loc[
            (
                # Entrée short lorsque le RSI est supérieur à 70
                (dataframe['rsi'] > 70) &
                # Lorsque la clôture du cours est au-dessus de la bande supérieure
                (dataframe['close'] > dataframe['bb_upperband'])
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
        dataframe.loc[
            (
                # Sortie du long lorsque le RSI est supérieur à 70
                (dataframe['close'] >= dataframe['bb_middleband'] )
            ),
            'exit_long'] = 1

        dataframe.loc[
            (
                # Sortie du short lorsque le RSI est inférieur à 30
                (dataframe['close'] <= dataframe['bb_middleband'])
            ),
            'exit_short'] = 1

        #dataframe.loc[
        #    (
                # Signal: RSI crosses above 70
        #        (qtpylib.crossed_above(dataframe['ICH_TS'], dataframe['ICH_KS']))
        #    ),

        #    'exit_short'] = 1


        return dataframe
      
# =================== SUMMARY METRICS ====================
# | Metric                      | Value                  |
# |-----------------------------+------------------------|
# | Backtesting from            | 2022-07-01 00:00:00    |
# | Backtesting to              | 2022-10-06 00:00:00    |
# | Max open trades             | 2                      |
# |                             |                        |
# | Total/Daily Avg Trades      | 635 / 6.55             |
# | Starting balance            | 1000 USDT              |
# | Final balance               | 2564.876 USDT          |
# | Absolute profit             | 1564.876 USDT          |
# | Total profit %              | 156.49%                |
# | CAGR %                      | 3361.55%               |
# | Profit factor               | 1.31                   |
# | Trades per day              | 6.55                   |
# | Avg. daily profit %         | 1.61%                  |
# | Avg. stake amount           | 740.614 USDT           |
# | Total trade volume          | 470290.002 USDT        |
# |                             |                        |
# | Long / Short                | 237 / 398              |
# | Total profit Long %         | 100.56%                |
# | Total profit Short %        | 55.92%                 |
# | Absolute profit Long        | 1005.638 USDT          |
# | Absolute profit Short       | 559.239 USDT           |
# |                             |                        |
# | Best Pair                   | ROOK/USDT:USDT 38.91%  |
# | Worst Pair                  | OOKI/USDT:USDT -23.52% |
# | Best trade                  | WSB/USDT:USDT 16.22%   |
# | Worst trade                 | WSB/USDT:USDT -12.60%  |
# | Best day                    | 170.957 USDT           |
# | Worst day                   | -142.559 USDT          |
# | Days win/draw/lose          | 62 / 1 / 35            |
# | Avg. Duration Winners       | 5:33:00                |
# | Avg. Duration Loser         | 6:04:00                |
# | Rejected Entry signals      | 592626                 |
# | Entry/Exit Timeouts         | 180 / 386              |
# |                             |                        |
# | Min balance                 | 992.518 USDT           |
# | Max balance                 | 2564.998 USDT          |
# | Max % of account underwater | 15.46%                 |
# | Absolute Drawdown (Account) | 12.55%                 |
# | Absolute Drawdown           | 291.42 USDT            |
# | Drawdown high               | 1321.307 USDT          |
# | Drawdown low                | 1029.887 USDT          |
# | Drawdown Start              | 2022-09-14 15:00:00    |
# | Drawdown End                | 2022-09-17 13:00:00    |
# | Market change               | -1.21%                 |
# ========================================================

#freqtrade backtesting -c config-gateio.json -s SampleStrategy --timeframe=1h --timerange=20220701-20221006

#very good because of short stoploss (0.03125)
