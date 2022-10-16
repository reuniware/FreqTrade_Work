# --- Do not remove these libs ---
from datetime import datetime
from typing import Any, Optional
from freqtrade.strategy import IStrategy, stoploss_from_absolute
from pandas import DataFrame
import talib.abstract as ta
import freqtrade.vendor.qtpylib.indicators as qtpylib
from freqtrade.persistence import Trade

from support import identify_df_trends

# --------------------------------

"""
The best strategy for freqtrade I found today searching on GitHub.
Strategy found at : https://github.com/devsmitra/trading/tree/183ff838830742ff6a13cafb1e8d7bd8ada26fea/user_data/strategies
It needs the "support.py" file found in the same directory.
It performs very well on the 20221001-20221014 timerange (in backtest !).
On 20220901-20221014 timerange : +347.61% and Drawdown = 2.44%
"""

class Candlestick(IStrategy):
    cache: Any = {}

    INTERFACE_VERSION: int = 3
    process_only_new_candles: bool = False
    # Optimal timeframe for the strategy
    timeframe = '15m'

    minimal_roi = {
        "0": 1
    }

    # Optimal stoploss designed for the strategy
    stoploss = -0.1
    use_custom_stoploss = True

    def custom_stoploss(self, pair: str, trade: Trade, current_time: datetime,
                        current_rate: float, current_profit: float, **kwargs) -> float:
        sl = 4.1
        dataframe, _ = self.dp.get_analyzed_dataframe(pair, self.timeframe)
        candle = dataframe.iloc[-1].squeeze()   
        def get_stoploss(atr):
            return stoploss_from_absolute(current_rate - (candle['atr'] * atr), current_rate, is_short=trade.is_short)

        if current_rate > (trade.open_rate + (candle['atr'] * 1.5 * sl)):
            return -.0001
        return get_stoploss(sl) * -1

    def custom_stake_amount(self, pair: str, current_time: datetime, current_rate: float,
                            proposed_stake: float, min_stake: Optional[float], max_stake: float,
                            leverage: float, entry_tag: Optional[str], side: str,
                            **kwargs) -> float:
        if self.wallets is None:
            return proposed_stake
        return self.wallets.get_total_stake_amount() * .06

    def get_trend(self, dataframe: DataFrame, metadata: dict):
        pair = metadata['pair']
        prev = self.cache.get(pair,  {'date': dataframe.iloc[-2]['date'], 'Trend': 0})
        date = dataframe.iloc[-1]['date']
        if (date != prev['date']):
            df = identify_df_trends(dataframe, 'close', window_size=3)
            self.cache[pair] = {'date': date, 'Trend': df['Trend']}
        else:
            dataframe['Trend'] = prev['Trend']

    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        self.get_trend(dataframe, metadata)
        dataframe['adx'] = ta.ADX(dataframe, timeperiod=14)
        dataframe['atr'] = ta.ATR(dataframe)
        return dataframe

    def populate_entry_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        crossed = False
        for i in range(0, 2):
            crossed = crossed | (
                qtpylib.crossed_above(dataframe.shift(i)['Trend'], 0) &
                (dataframe.shift(i)['adx'] > 20)
            )

        dataframe.loc[
            crossed,
            'enter_long'
        ] = 1
        return dataframe

    def populate_exit_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe.loc[
            (
                (qtpylib.crossed_below(dataframe['adx'], 25) & (dataframe['Trend'] == -1)) |
                (qtpylib.crossed_below(dataframe['Trend'], 0) & (dataframe['adx'] < 25)) |
                (qtpylib.crossed_below(dataframe.shift()['Trend'], 0) & (dataframe['adx'] < 25))
            ),
            'exit_long'] = 1
        return dataframe

    def confirm_trade_exit(self, pair: str, trade: Trade, order_type: str, amount: float,
                           rate: float, time_in_force: str, exit_reason: str,
                           current_time: datetime, **kwargs) -> bool:
        profit = trade.calc_profit_ratio(rate)
        if (((exit_reason == 'force_exit') | (exit_reason == 'exit_signal')) and (profit < 0)):
            return False
        return True
