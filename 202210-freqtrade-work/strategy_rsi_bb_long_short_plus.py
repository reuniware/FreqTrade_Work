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
        return

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
# | Total/Daily Avg Trades      | 762 / 7.86             |
# | Starting balance            | 1000 USDT              | ****
# | Final balance               | 3763.527 USDT          | ****
# | Absolute profit             | 2763.527 USDT          | ****
# | Total profit %              | 276.35%                |
# | CAGR %                      | 14552.07%              |
# | Profit factor               | 1.47                   |
# | Trades per day              | 7.86                   |
# | Avg. daily profit %         | 2.85%                  |
# | Avg. stake amount           | 977.711 USDT           |
# | Total trade volume          | 745015.487 USDT        |
# |                             |                        |
# | Long / Short                | 287 / 475              |
# | Total profit Long %         | 168.12%                |
# | Total profit Short %        | 108.24%                |
# | Absolute profit Long        | 1681.177 USDT          |
# | Absolute profit Short       | 1082.35 USDT           |
# |                             |                        |
# | Best Pair                   | ROOK/USDT:USDT 36.73%  |
# | Worst Pair                  | OOKI/USDT:USDT -13.64% |
# | Best trade                  | WSB/USDT:USDT 16.22%   |
# | Worst trade                 | WSB/USDT:USDT -12.60%  |
# | Best day                    | 195.848 USDT           |
# | Worst day                   | -225.438 USDT          |
# | Days win/draw/lose          | 66 / 1 / 30            |
# | Avg. Duration Winners       | 5:00:00                |
# | Avg. Duration Loser         | 4:03:00                |
# | Rejected Entry signals      | 584367                 |
# | Entry/Exit Timeouts         | 211 / 476              |
# |                             |                        |
# | Min balance                 | 1002.177 USDT          |
# | Max balance                 | 3781.891 USDT          |
# | Max % of account underwater | 14.06%                 |
# | Absolute Drawdown (Account) | 13.76%                 |
# | Absolute Drawdown           | 464.726 USDT           |
# | Drawdown high               | 2377.731 USDT          |
# | Drawdown low                | 1913.005 USDT          |
# | Drawdown Start              | 2022-09-14 17:00:00    |
# | Drawdown End                | 2022-09-18 19:00:00    |
# | Market change               | -1.21%                 |
# ========================================================

# freqtrade backtesting -c config-gateio.json -s SampleStrategy --timeframe=1h --timerange=20220701-20221006

# Awesome !! Stoploss = 0.015625 !!!

=================== SUMMARY METRICS ===================
# | Metric                      | Value                 |
# |-----------------------------+-----------------------|
# | Backtesting from            | 2022-07-01 00:00:00   |
# | Backtesting to              | 2022-10-06 00:00:00   |
# | Max open trades             | 2                     |
# |                             |                       |
# | Total/Daily Avg Trades      | 1437 / 14.81          |
# | Starting balance            | 1000 USDT             |
# | Final balance               | 14789.013 USDT        |
# | Absolute profit             | 13789.013 USDT        |
# | Total profit %              | 1378.90%              |
# | CAGR %                      | 2525406.26%           |
# | Profit factor               | 1.60                  |
# | Trades per day              | 14.81                 |
# | Avg. daily profit %         | 14.22%                |
# | Avg. stake amount           | 2775.369 USDT         |
# | Total trade volume          | 3988205.454 USDT      |
# |                             |                       |
# | Long / Short                | 591 / 846             |
# | Total profit Long %         | 728.75%               |
# | Total profit Short %        | 650.15%               |
# | Absolute profit Long        | 7287.543 USDT         |
# | Absolute profit Short       | 6501.47 USDT          |
# |                             |                       |
# | Best Pair                   | BIT/USDT:USDT 54.37%  |
# | Worst Pair                  | ZEC/USDT:USDT -9.15%  |
# | Best trade                  | DEFI/USDT:USDT 19.20% |
# | Worst trade                 | RON/USDT:USDT -7.98%  |
# | Best day                    | 1212.418 USDT         |
# | Worst day                   | -660.631 USDT         |
# | Days win/draw/lose          | 77 / 0 / 21           |
# | Avg. Duration Winners       | 2:52:00               |
# | Avg. Duration Loser         | 2:43:00               |
# | Rejected Entry signals      | 2438404               |
# | Entry/Exit Timeouts         | 515 / 1830            |
# |                             |                       |
# | Min balance                 | 986.243 USDT          |
# | Max balance                 | 15169.875 USDT        |
# | Max % of account underwater | 12.19%                |
# | Absolute Drawdown (Account) | 12.19%                |
# | Absolute Drawdown           | 1666.479 USDT         |
# | Drawdown high               | 12674.029 USDT        |
# | Drawdown low                | 11007.55 USDT         |
# | Drawdown Start              | 2022-09-18 13:45:00   |
# | Drawdown End                | 2022-09-21 13:15:00   |
# | Market change               | 4.53%                 |
# =======================================================

# freqtrade backtesting -c config-gateio.json -s SampleStrategy --timerange=20220701-20221006 --timeframe=15m
