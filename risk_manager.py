'''
9/3/24
Where we will monitor active positions and submit orders when our risk params are hit
'''
import time
import nice_funcs as n

user_address = '0x90e9bF6c345B68eE9fd8D4ECFAddb7Ee4F14c8f4'
client = n.create_clob_client('0x90e9bF6c345B68eE9fd8D4ECFAddb7Ee4F14c8f4')
# 1. Get Active Positions
active_positions = n.get_active_positions(n.fetch_user_positions(user_address))
# print(active_positions.iloc[0][['asset', 'title', 'percentPnl']])
# print(active_positions.columns)

# 2. Set Take Profit and Stop Loss Parameters
take_profit = 20
stop_loss = -4

# 3. Loop through active positions and check whether your parameters have been hit
    # if they have, create an order

# NOTE: This is counting sub $1 positions... this is fine, we shouldnt have those anyway
def risk_management_looper(user_address: str):

    client = n.create_clob_client('0x90e9bF6c345B68eE9fd8D4ECFAddb7Ee4F14c8f4')
    # 1. Get Active Positions
    active_positions = n.get_active_positions(n.fetch_user_positions(user_address, limit = 500))

    # will this skip the last active position?
    for i in range(0, len(active_positions)):
        # print(f"Loop {i + 1}: Position = {active_positions.iloc[i]}")
        trade_title = active_positions.iloc[i]['title']
        trade_pnl = active_positions.iloc[i]['percentPnl']
        outcome = active_positions.iloc[i]['outcome']

        print(f"trade pnl is {round(trade_pnl,4)}%")
        if trade_pnl >= take_profit:

            print(f"take profit % of {take_profit} hit, submitting order to SELL asset: {trade_title} with outcome of [[ {outcome} ]]")

            price = client.get_last_trade_price(active_positions.iloc[i]['asset'])
            print(f"current market price is {price['price']}")
            size = active_positions.iloc[i]['size']
            side = 'SELL' # this should always be sell because we'll already be in position
            asset = active_positions.iloc[i]['asset']

            n.create_order(client, price, size, side, asset)
        elif trade_pnl <= stop_loss:

            print(f"stop loss % of {stop_loss} hit, submitting order to SELL asset: {trade_title} with outcome of [[{outcome}]]")

            price = client.get_last_trade_price(active_positions.iloc[i]['asset'])
            print(f"current market price is {price['price']}")
            size = active_positions.iloc[i]['size']
            side = 'SELL' # this should always be sell because we'll already be in position
            asset = active_positions.iloc[i]['asset']

            n.create_order(client, price, size, side, asset)
        else:
            print(f"neither take profit or stop loss hit for asset: {trade_title} with outcome of [[ {outcome} ]]")
            print(f"current PnL is: {round((trade_pnl), 4)}%")
    print('')
    print("------------------------------------")
    print("All positions checked. Ending Loop. ")
    print("------------------------------------")
    print('')

if __name__ == "__main__":

    while True:
        risk_management_looper(user_address)
        time.sleep(30)