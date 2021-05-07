import pandas as pd

# def calculate_long_scalping_for_one_point(_df, open_position_iloc, profit: float, risk: float, period: int):
#     #logger.msg("Calculate", data=data[open_position_index]['date'] )
#     open_position_price = _df.iloc[open_position_iloc ]['high']
#     stop_loss_price = open_position_price - open_position_price * risk
#     take_profit_price = open_position_price + open_position_price * profit
#
#     close_position_max_index = min(len(_df), open_position_iloc + period)
#     for close_position_index in range(open_position_iloc + 1, close_position_max_index):
#         current_row = _df.iloc[close_position_index]
#
#         # check stop_loss
#         low_price = current_row['low']
#         if low_price <= stop_loss_price:
#             return -1
#
#         # check take profit
#         high_price = current_row['high']
#         if high_price >= take_profit_price:
#             return 1
#
#     return 0
#
# def calculate_short_scalping_for_one_point(_df, open_position_iloc, profit: float, risk: float, period: int):
#     # logger.msg("Calculate", data=data[open_position_index]['date'] )
#     open_position_price = _df.iloc[open_position_iloc]['low']
#     stop_loss_price = open_position_price + open_position_price * risk
#     take_profit_price = open_position_price - open_position_price * profit
#
#     close_position_max_index = min(len(_df), open_position_iloc + period)
#     for close_position_index in range(open_position_iloc + 1, close_position_max_index):
#         current_row = _df.iloc[close_position_index]
#         # check stop_loss
#         high_price = current_row['high']
#         if high_price >= stop_loss_price:
#             return -1
#
#         # check take profit
#         low_price = current_row['low']
#         if low_price <= take_profit_price:
#             return 1
#
#     return 0
#
#
# def calculate_scalping_for_long(_df, profit: float, risk: float, period: int):
#     result = {}
#     for open_position_index in range(len(_df) - 1):
#         data = _df.iloc[open_position_index]
#         result[data.date] = calculate_long_scalping_for_one_point(_df, open_position_index, profit, risk, period)
#     return pd.Series(result)
#
#
#
# def calculate_scalping_for_short(_df, profit: float, risk: float, period: int):
#     result = {}
#     for open_position_index in range(len(_df) - 1):
#         data = _df.iloc[open_position_index]
#         result[data.date] = calculate_short_scalping_for_one_point(_df, open_position_index, profit, risk, period)
#     return pd.Series(result)



def calculate_scalping_for_long_fast(_df, profit: float, risk: float, period: int):
    df = _df.copy()
    df['long_rate'] = 0
    #df['result_long_position'] = 0
    data = df.to_dict('records')
    for open_position_index in range(len(data) - 1):
        #logger.msg("Calculate", data=data[open_position_index]['date'] )
        open_position_price = data[open_position_index]['high']
        stop_loss_price = open_position_price - open_position_price * risk
        take_profit_price = open_position_price + open_position_price * profit

        close_position_max_index = min(len(data), open_position_index + period)
        position = 0
        for close_position_index in range(open_position_index + 1, close_position_max_index):
            # update shared vars
            position = position + 1

            # check stop_loss
            low_price = data[close_position_index]['low']
            if low_price <= stop_loss_price:
                data[open_position_index]['long_rate'] = -1
                break

            # check take profit
            high_price = data[close_position_index]['high']
            if high_price >= take_profit_price:
                data[open_position_index]['long_rate'] = 1
                break

    df_ = pd.DataFrame(data)
    df_.set_index('date', inplace=True, drop=False)
    return df_['long_rate']

def calculate_scalping_for_short_fast(_df, profit: float, risk: float, period: int):
    df = _df.copy()
    df['short_rate'] = 0
    #df['result_short_position'] = 0
    data = df.to_dict('records')
    for open_position_index in range(len(data) - 1):
        #logger.msg("Calculate", data=data[open_position_index]['date'] )
        open_position_price = data[open_position_index ]['low']
        stop_loss_price = open_position_price + open_position_price * risk
        take_profit_price = open_position_price - open_position_price * profit

        close_position_max_index = min(len(data), open_position_index + period)
        position = 0
        for close_position_index in range(open_position_index + 1, close_position_max_index):
            # update shared vars
            position = position + 1

            # check stop_loss
            high_price = data[close_position_index]['high']
            if high_price >= stop_loss_price:
                data[open_position_index]['short_rate'] = -1
                break

            # check take profit
            low_price = data[close_position_index]['low']
            if low_price <= take_profit_price:
                data[open_position_index]['short_rate'] = 1
                break

    df_ = pd.DataFrame(data)
    df_.set_index('date', inplace=True, drop=False)
    return df_['short_rate']
