'''
9/3/2024
This will trade out of the specified json file and flip the bot_executed flag to True
 - this is working, it flips the flag as intended. Now, we need to run this in a loop.
 - We need to add logic that does not trade if we are already in position

9/4/24
Line 86: Added functionality to catch piling into a position we're already in
    - I DONT KNOW if it works. Check this
'''

import json
import time
import nice_funcs as n
from datetime import datetime, timedelta
from py_clob_client.exceptions import PolyApiException
from py_clob_client.clob_types import OrderArgs, OrderType


# Function to execute trade using create_order
def create_order(client, price, size, side, asset):
    order_args = OrderArgs(
        price=price,
        # make 1 for now
        size=size,
        side=side,
        token_id=asset
    )

    signed_order = client.create_order(order_args)
    resp = client.post_order(signed_order, OrderType.GTC)
    print(resp)

def kill_switch():
    pass

# Function to process trades
def process_trades(json_file_path, client, sleep_duration=60, too_long_ago_hours=24):
    # Load trades from JSON file
    with open(json_file_path, 'r') as file:
        trades = json.load(file)

    # NOTE: I dont think we need this anymore now that the trades are being written inside the loop
    # # Flag to track if any trades were executed
    # trades_updated = False

    # Calculate the cutoff timestamp
    cutoff_time = datetime.now() - timedelta(hours=too_long_ago_hours)
    cutoff_timestamp = int(cutoff_time.timestamp())

    # Iterate over each trade in the JSON data
    for trade in reversed(trades):
        # print(trade)
        # Check if the bot_executed flag is False
                # Check if the trade is recent enough and bot_executed flag is False and trade type is 'TRADE'
        if (
            trade['timestamp'] >= cutoff_timestamp and
            'bot_executed' in trade and
            trade['bot_executed'] is False and 
            trade['type'] == 'TRADE'
        ):
        # if 'bot_executed' in trade and trade['bot_executed'] is False and trade['type'] == 'TRADE':
        # if not trade.get('bot_executed', False):  # Default to True if key is missing

            my_balance = n.get_wallet_balance('0x90e9bF6c345B68eE9fd8D4ECFAddb7Ee4F14c8f4')
            trade_risk = 0.15
            risk_size = my_balance * trade_risk
            print(f'Risk Size USD is: {risk_size}')
            # Extract trade details
            price = client.get_last_trade_price(trade['asset'])
            price = float(price['price'])
            print(f"Market Title: {trade['title']}")
            print(f"current market price is {price}")
            # price = trade['price']
            size = risk_size / price
            side = trade['side']
            asset = trade['asset']

            user_address='0x90e9bF6c345B68eE9fd8D4ECFAddb7Ee4F14c8f4'
            active_positions = n.get_active_positions(n.fetch_user_positions(user_address, limit = 500))
            try:
                if price >= .90 or price <= 0.05:
                    print('not enough movement range to validate position, passing on trade')
                    # Update the trade status to prevent re-execution
                    trade['bot_executed'] = True
                # NOTE: I dont know if this will work correctly, but i can fix it tomorrow
                elif asset in active_positions:
                    print('already in position, skipping trade') 
                    # Update the trade status to prevent re-execution
                    trade['bot_executed'] = True
                else:
                    # Attempt to execute the trade
                    create_order(client, price, size, side, asset)

                    # Update the trade status to prevent re-execution
                    trade['bot_executed'] = True

                # trades_updated = True
                # Save the immediate update back to JSON file
                with open(json_file_path, 'w') as file:
                    json.dump(trades, file, indent=4)

            except PolyApiException as e:
                
                error_message = str(e)

                # Check if the error message matches the specific insufficient balance/allowance error
                if "not enough balance / allowance" in error_message:
                    print(f"Error: {e}. Sleeping for {sleep_duration} seconds.")
                    time.sleep(sleep_duration)
                    # Continue to monitor trades without stopping the function
                    continue
                
                                # Check if the error message matches the minimum size requirement error
                elif "lower than the minimum" in error_message:
                    print("Current risk parameters do not allow you to make this trade.")
                    # Continue to the next trade without executing
                    continue

                else:
                    # Re-raise the exception if it's not an error we're handling
                    raise

        # Save the JSON file if bot_executed is already True or trade type is not 'TRADE'
        else:
            with open(json_file_path, 'w') as file:
                json.dump(trades, file, indent=4)

    print("All trades scanned, and updated or passed. Sleeping for 30 seconds.")
    print('----------------------------------------------------------------------')
    time.sleep(30)  # Pause before the next iteration

## This is working as intended. it will tail the trade. Now we need to stop adding to a position we already have open

# Example usage
if __name__ == "__main__":
    # Replace with the path to your JSON file
    json_file_path = '/Users/joshbazz/Desktop/Bootcamp/Capstone_Project/tail_trades.json'
    
    # my_balance = n.get_wallet_balance('0x90e9bF6c345B68eE9fd8D4ECFAddb7Ee4F14c8f4')
    # print(my_balance)
    # Replace with your ClobClient instance
    client = n.create_clob_client('0x90e9bF6c345B68eE9fd8D4ECFAddb7Ee4F14c8f4')

    # # Process the trades
    # process_trades(json_file_path, client)

    # Run the process_trades function continuously in a loop
    while True:
        process_trades(json_file_path, client)