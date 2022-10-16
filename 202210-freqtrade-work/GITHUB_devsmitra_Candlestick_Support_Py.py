import numpy as np
from statistics import mean


def support(df, index, n1, n2, col):  # n1 n2 before and after candle index
    for i in range(index - n1 + 1, index + 1):
        if(df[col][i] > df[col][i - 1]):
            return False
    for i in range(index + 1, index + n2 + 1):
        if(df[col][i] < df[col][i - 1]):
            return False
    return True


def is_Support_Level(df, i):
    return support(df, i, 2, 2, 'low')


def is_Resistance_Level(df, i):
    return support(df, i, 2, 2, 'high')


def find_levels(n):
    if n > 1:
        return n.round(2)

    s = '{:.20f}'.format(n % 1)
    zeros = (len(s) - len(s.lstrip('0.').lstrip('0')))
    return n.round(zeros + 1)


def support_resistance(df, dataframe):

    levels = []
    mean = np.mean(df['high'] - df['low'])
    # This function, given a price value, returns True or False depending on if it
    # is too near to some previously discovered key level.

    def distance_from_mean(level, levels):
        return np.sum([abs(level - y) < mean for y in levels]) == 0

    supports = []
    resistances = []
    for i in range(2, df.shape[0] - 2):
        if is_Support_Level(df, i):
            level = find_levels(df['low'][i])
            if distance_from_mean(level, levels):
                levels.append(level)
                supports.append(level)

        elif is_Resistance_Level(df, i):
            level = find_levels(df['high'][i])
            if distance_from_mean(level, levels):
                levels.append(level)
                resistances.append(level)

    supports.sort()
    for i in range(11):
        s = len(supports) - i - 1
        r = len(resistances) - i - 1

        support = "s" + str(i + 1)
        resistance = "r" + str(i + 1)
        dataframe[support] = supports[s] if s >= 0 else np.nan
        dataframe[resistance] = resistances[r] if r >= 0 else np.nan


# ----------------------------------------------------------------------------------------------------------------------

def get_up_trend(results):
    up_trends = list()
    for up in results['Up Trend']:
        flag = True

        for down in results['Down Trend']:
            if down['from'] < up['from'] < down['to'] or down['from'] < up['to'] < down['to']:
                if (up['to'] - up['from']) > (down['to'] - down['from']):
                    flag = True
                else:
                    flag = False
            else:
                flag = True

        if flag is True:
            up_trends.append(up)
    return up_trends


def get_down_trend(results):
    down_trends = list()
    for down in results['Down Trend']:
        flag = True

        for up in results['Up Trend']:
            if up['from'] < down['from'] < up['to'] or up['from'] < down['to'] < up['to']:
                if (up['to'] - up['from']) < (down['to'] - down['from']):
                    flag = True
                else:
                    flag = False
            else:
                flag = True

        if flag is True:
            down_trends.append(down)
    return down_trends


def identify_df_trends(df, column, window_size=5):
    objs = list()
    df['Trend'] = 0

    up_trend = {
        'name': 'Up Trend',
        'element': np.negative(df[column])
    }

    down_trend = {
        'name': 'Down Trend',
        'element': df[column]
    }

    objs.append(up_trend)
    objs.append(down_trend)
    results = dict()

    for obj in objs:
        limit = None
        values = list()
        trends = list()

        from_trend = 0
        for index, value in enumerate(obj['element'], 0):
            if limit and limit > value:
                values.append(value)
                limit = mean(values)
            elif limit and limit < value:
                if len(values) > window_size:
                    min_value = min(values)

                    for counter, item in enumerate(values, 0):
                        if item == min_value:
                            break

                    to_trend = from_trend + counter

                    trend = {
                        'from': df.index.tolist()[from_trend],
                        'to': df.index.tolist()[min(to_trend, len(df.index.tolist()) - 1)],
                    }

                    trends.append(trend)

                limit = None
                values = list()
            else:
                from_trend = index
                values.append(value)
                limit = mean(values)

        results[obj['name']] = trends

    up_trends = get_up_trend(results)
    for up_trend in up_trends:
        for index, row in df[up_trend['from']:up_trend['to']].iterrows():
            df.loc[index, 'Trend'] = 1

    down_trends = get_down_trend(results)
    for down_trend in down_trends:
        for index, row in df[down_trend['from']:down_trend['to']].iterrows():
            df.loc[index, 'Trend'] = -1

    return df
