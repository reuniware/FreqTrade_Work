import numpy as np  # noqa
import pandas as pd  # noqa
from pandas import DataFrame
from freqtrade.strategy import IntParameter

from freqtrade.strategy import IStrategy

import talib.abstract as ta
import freqtrade.vendor.qtpylib.indicators as qtpylib


class b_low(IStrategy):
  
    INTERFACE_VERSION = 2

    minimal_roi = {
        "0": 0.27,
        "1619": 0.224,
        "4489": 0.101,
        "5136": 0
    }

    stoploss = -0.27

    # Trailing stoploss
    trailing_stop = True
    trailing_only_offset_is_reached = True
    trailing_stop_positive = 0.01
    trailing_stop_positive_offset = 0.071

    # Optimal timeframe for the strategy.
    timeframe = '4h'
    sell_r_14 = IntParameter(low=-30, high=0, default=-10, space='sell', optimize=True, load=True)
    buy_adx = IntParameter(low=25, high=50, default=40, space='buy', optimize=True, load=True)
    sell_rsi = IntParameter(low=70, high=85, default=80, space='sell', optimize=True, load=True)
    # Run "populate_indicators()" only for new candle.
    process_only_new_candles = False

    # These values can be overridden in the "ask_strategy" section in the config.
    use_exit_signal = True
    exit_profit_only = False
    ignore_roi_if_entry_signal = False

    # Optional order type mapping.
    order_types = {
        'entry': 'limit',
        'exit': 'limit',
        'stoploss': 'market',
        'stoploss_on_exchange': False
    }
    buy_params ={
        buy_adx: 32,
    }
    sell_params ={
        sell_r_14: -8,
    }
    # Optional order time in force.
    order_time_in_force = {
        'entry': 'gtc',
        'exit': 'gtc'
    }
    
    plot_config = {
        # Main plot indicators (Moving averages, ...)
        'main_plot': {
            'tema': {},
            'sar': {'color': 'white'},
        },
        'subplots': {
            # Subplots - each dict defines one additional plot
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
        
        # Momentum Indicators
        # ------------------------------------

        bollinger = qtpylib.bollinger_bands(qtpylib.typical_price(dataframe), window=20, stds=2)
        dataframe['bb_lowerband'] = bollinger['lower']
        dataframe['bb_middleband'] = bollinger['mid']
        dataframe['bb_upperband'] = bollinger['upper']

        # # EMA - Exponential Moving Average
        dataframe['r14'] = ta.WILLR(dataframe, timeperiod=28)
        dataframe['ema50'] = ta.EMA(dataframe['close'], timeperiod=50)
        dataframe['tema25'] = ta.TEMA(dataframe['close'], timeperiod=25)
        dataframe['adx'] = ta.ADX(dataframe, timeperiod=14)
        return dataframe
 

    def populate_entry_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:

        dataframe.loc[
            (
                (qtpylib.crossed_above(dataframe['tema25'], dataframe['bb_middleband']))
                &
                (dataframe['ema50'] > dataframe['bb_middleband'])  
                &
                (dataframe['adx'] > self.buy_adx.value)
            ),
            'enter_long'] = 1

        return dataframe

    def populate_exit_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:

        dataframe.loc[
            (
                (
                    (qtpylib.crossed_above(dataframe['tema25'], dataframe['ema50'])) |
                    (qtpylib.crossed_below(dataframe['tema25'], dataframe['bb_middleband'])) |
                    (qtpylib.crossed_below(dataframe['close'], dataframe['bb_middleband']))
                )   
            ),
            'exit_long'] = 1
        return dataframe
