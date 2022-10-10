# pragma pylint: disable=missing-docstring, invalid-name, pointless-string-statement
# flake8: noqa: F401
# isort: skip_file
# --- Do not remove these libs ---
import numpy as np  # noqa
import pandas as pd  # noqa
from pandas import DataFrame
import os

from freqtrade.strategy import (BooleanParameter, CategoricalParameter, DecimalParameter,
                                IStrategy, IntParameter, RealParameter)

from freqtrade.strategy import merge_informative_pair

# --------------------------------
# Add your lib to import here
import talib.abstract as ta
import freqtrade.vendor.qtpylib.indicators as qtpylib

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
class STRAT001(IStrategy):
    delete_log_results()

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
    inf_1h = '1h'

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
        pairs = self.dp.current_whitelist()
        # Assign tf to each pair so they can be downloaded and cached for strategy.
        informative_pairs = [(pair, '1h') for pair in pairs]
        return informative_pairs

    def informative_1h_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        assert self.dp, "DataProvider is required for multiple timeframes."
        # Get the informative pair
        informative_1h = self.dp.get_pair_dataframe(pair=metadata['pair'], timeframe=self.inf_1h)

        # EMA
        informative_1h['ema_12'] = ta.EMA(informative_1h, timeperiod=12)
        informative_1h['ema_15'] = ta.EMA(informative_1h, timeperiod=15)

        return informative_1h

    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        # The indicators for the 1h informative timeframe
        #informative_1h = self.informative_1h_indicators(dataframe, metadata)
        #dataframe = merge_informative_pair(dataframe, informative_1h, self.timeframe, self.inf_1h, ffill=True)

        # RSI
        dataframe['rsi'] = ta.RSI(dataframe, timeperiod=14)

        # Définition de l'indicateur Bollinger
        bollinger = qtpylib.bollinger_bands(qtpylib.typical_price(dataframe), window=20, stds=2)
        # Ajout de la bande supérieure
        dataframe['bb_lowerband'] = bollinger['lower'] 
        dataframe['bb_middleband'] = bollinger['mid']
        dataframe['bb_upperband'] = bollinger['upper']

        #log_to_results(dataframe.to_string())

        return dataframe

    def populate_entry_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        #print("populate_entry_trend")
        dataframe.loc[
            (
                # Entrée long Lorsque le RSI est inférieur à 30
                (dataframe['rsi'] < 30) &
                # Lorsque la clôture du cours est sous la bande inférieure
                (dataframe['close'] < dataframe['bb_lowerband']) 
                #& (dataframe['ema_12_1h'].shift(12) < dataframe['ema_15_1h'].shift(12))
            ),
            'enter_long'] = 1

        dataframe.loc[
            (
                # Entrée short lorsque le RSI est supérieur à 70
                (dataframe['rsi'] > 70) &
                # Lorsque la clôture du cours est au-dessus de la bande supérieure
                (dataframe['close'] > dataframe['bb_upperband'])
                #& (dataframe['ema_12_1h'].shift(12) > dataframe['ema_15_1h'].shift(12))
            ),
            'enter_short'] = 1

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

