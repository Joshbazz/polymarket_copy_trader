'''
The Risk Manager handles the parameters set by the User for defining Take Profit and Stop Loss Levels

Future iterations will include more complex Risk Management

Some markets in Polymarket will not allow you to submit Orders for less than a Limit of 5
    - You can either increase your Risk Parameters, or let the error handling pass over this 
        error without breaking the loop while testing
'''
import time
import nice_funcs as n
from py_clob_client.exceptions import PolyApiException

user_address = '0x90e9bF6c345B68eE9fd8D4ECFAddb7Ee4F14c8f4'

# Set Take Profit and Stop Loss Parameters
take_profit = 10
stop_loss = -7


def risk_management_looper(user_address: str):

    client = n.create_clob_client('0x90e9bF6c345B68eE9fd8D4ECFAddb7Ee4F14c8f4')
    user_positions = n.fetch_user_positions(user_address, limit = 500)
    # 1. Get Active Positions
    # active_positions = n.get_active_positions(n.fetch_user_positions(user_address, limit = 500))
    print(len(user_positions))
    # will this skip the last active position?
    for i in range(0, len(user_positions)):
        # print(f"Loop {i + 1}: Position = {active_positions.iloc[i]}")
        trade_title = user_positions.iloc[i]['title']
        trade_pnl = user_positions.iloc[i]['percentPnl']
        outcome = user_positions.iloc[i]['outcome']

        print(f"trade pnl is {round(trade_pnl,4)}%")
        if trade_pnl >= take_profit:

            print(f"take profit % of {take_profit} hit, submitting order to SELL asset: {trade_title} with outcome of [[ {outcome} ]]")

            price = client.get_last_trade_price(user_positions.iloc[i]['asset'])
            price = float(price['price'])
            print(f"current market price is {price}")
            size = user_positions.iloc[i]['size']
            side = 'SELL' # this should always be sell because we'll already be in position
            asset = user_positions.iloc[i]['asset']

            try:

                n.create_order(client, price, size, side, asset)

            except PolyApiException as e:
                
                error_message = str(e)

                if "lower than the minimum" in error_message: 
                    print("Current risk parameters do not allow you to make this trade.")
                    # Continue to the next trade without executing
                    continue

        elif trade_pnl <= stop_loss:

            print(f"stop loss % of {stop_loss} hit, submitting order to SELL asset: {trade_title} with outcome of [[{outcome}]]")

            price = client.get_last_trade_price(user_positions.iloc[i]['asset'])
            price = float(price['price'])
            print(f"current market price is {price}")
            size = user_positions.iloc[i]['size']
            side = 'SELL' # this should always be sell because we'll already be in position
            asset = user_positions.iloc[i]['asset']

            try:

                n.create_order(client, price, size, side, asset)

            except PolyApiException as e:
                
                error_message = str(e)

                if "lower than the minimum" in error_message: 
                    print("Current risk parameters do not allow you to make this trade.")
                    # Continue to the next trade without executing
                    continue

        else:
            print(f"neither take profit or stop loss hit for asset: {trade_title} with outcome of [[ {outcome} ]]")
            print(f"current PnL is: {round((trade_pnl), 4)}%")
    print('')
    print("------------------------------------")
    print("All positions checked. Ending Loop. ")
    print("------------------------------------")
    print('')

def run_risk_manager(user_address):
    while True:
        risk_management_looper(user_address)
        time.sleep(30)
        
if __name__ == "__main__":

    while True:
        risk_management_looper(user_address)
        time.sleep(30)