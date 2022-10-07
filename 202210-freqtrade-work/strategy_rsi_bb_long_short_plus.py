# pragma pylint: disable=missing-docstring, invalid-name, pointless-string-statement
# flake8: noqa: F401
# isort: skip_file
# --- Do not remove these libs ---
import numpy as np  # noqa
import pandas as pd  # noqa
from pandas import DataFrame

from freqtrade.strategy import (BooleanParameter, CategoricalParameter, DecimalParameter,
                                IStrategy, IntParameter, RealParameter)

from freqtrade.strategy import merge_informative_pair

# --------------------------------
# Add your lib to import here
import talib.abstract as ta
import freqtrade.vendor.qtpylib.indicators as qtpylib

# This class is a sample. Feel free to customize it.
class SampleStrategy(IStrategy):

    # Strategy interface version - allow new iterations of the strategy interface.
    # Check the documentation or the Sample strategy to get the latest version.
    INTERFACE_VERSION = 3

    # Can this strategy go short?
    can_short: bool = True

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
        'entry': 'gtc',
        'exit': 'gtc'
    }

    def informative_pairs(self):
        return []

    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:

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

        #dataframe.loc[
            #( -
            #    (qtpylib.crossed_above(dataframe['ICH_KS'], dataframe['ICH_TS']))
            #),
            #'enter_short'] = 1

        return dataframe

    def populate_exit_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe.loc[
            (
                # Sortie du long lorsque la bb du milieu est atteinte
                (dataframe['close'] >= dataframe['bb_middleband'] )
            ),
            'exit_long'] = 1

        dataframe.loc[
            (
                # Sortie du short lorsque la bb du milieu est atteinte
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
# | Backtesting from            | 2022-01-01 00:00:00    |
# | Backtesting to              | 2022-10-07 00:00:00    |
# | Max open trades             | 2                      |
# |                             |                        |
# | Total/Daily Avg Trades      | 5677 / 20.35           |
# | Starting balance            | 1000 USDT              |
# | Final balance               | 399596.382 USDT        |
# | Absolute profit             | 398596.382 USDT        |
# | Total profit %              | 39859.64%              |
# | CAGR %                      | 253153.28%             |
# | Profit factor               | 1.47                   |
# | Trades per day              | 20.35                  |
# | Avg. daily profit %         | 142.87%                |
# | Avg. stake amount           | 23922.218 USDT         |
# | Total trade volume          | 135806434.268 USDT     |
# |                             |                        |
# | Long / Short                | 2529 / 3148            |
# | Total profit Long %         | 18984.89%              |
# | Total profit Short %        | 20874.75%              |
# | Absolute profit Long        | 189848.911 USDT        |
# | Absolute profit Short       | 208747.471 USDT        |
# |                             |                        |
# | Best Pair                   | BIT/USDT:USDT 198.68%  |
# | Worst Pair                  | ZEC/USDT:USDT -28.48%  |
# | Best trade                  | WSB/USDT:USDT 20.81%   |
# | Worst trade                 | LUNA/USDT:USDT -20.00% |
# | Best day                    | 32629.272 USDT         |
# | Worst day                   | -18411.57 USDT         |
# | Days win/draw/lose          | 202 / 2 / 75           |
# | Avg. Duration Winners       | 2:18:00                |
# | Avg. Duration Loser         | 1:38:00                |
# | Rejected Entry signals      | 6071333                |
# | Entry/Exit Timeouts         | 1170 / 3304            |
# |                             |                        |
# | Min balance                 | 989.506 USDT           |
# | Max balance                 | 399596.382 USDT        |
# | Max % of account underwater | 40.74%                 |
# | Absolute Drawdown (Account) | 11.73%                 |
# | Absolute Drawdown           | 44030.514 USDT         |
# | Drawdown high               | 374463.064 USDT        |
# | Drawdown low                | 330432.549 USDT        |
# | Drawdown Start              | 2022-09-18 13:45:00    |
# | Drawdown End                | 2022-09-26 06:30:00    |
# | Market change               | -65.58%                |
# ========================================================

# freqtrade backtesting -c config-gateio.json --strategy SampleStrategy --timerange=20220101-20221007 --timeframe="15m"
