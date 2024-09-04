'''
The operative script for monitoring wallets and their respective transactions. 
All wallets are put into a separate Thread so they can run concurrently and rejoined at the end of the monitoring period.

From the nice_funcs file, the brain of this script is pulled from trade_type()
    - trade type filters out trades we dont want. Please visit nice_funcs for more details

If trades pass the filtering, they are appended to a JSON file called tail_trades.json
    - they will then be scanned by the trade_tailer for further filtering
'''

import time
import nice_funcs as n
from threading import Thread
from proxy_wallets import proxy_wallets


proxy_wallets = proxy_wallets

def monitor_wallet(user_address):
    print(f"Monitoring trades for wallet: {user_address}")

    # I think we want to check the positions, sleep, then check the trades.     
    active_positions = n.get_active_positions(n.fetch_user_positions(user_address))

    # Fetch the initial user activity
    last_trade = n.fetch_user_activity(user_address)
    
    if not last_trade or not isinstance(last_trade, list) or len(last_trade) == 0:
        print(f"No initial trade data available for wallet: {user_address}")
        return
    
    last_trade = last_trade[0]  # Assume the most recent trade is the first item

    print(f"Initial trade detected for wallet {user_address}:", last_trade)
    
    while True:
        time.sleep(30)  # Sleep for 60 seconds

        # Fetch the latest user activity
        current_trades = n.fetch_user_activity(user_address)
        
        # Fetch active positions before processing the trade
        new_active_positions = n.get_active_positions(n.fetch_user_positions(user_address))

        if current_trades and isinstance(current_trades, list) and len(current_trades) > 0:
            current_trade = current_trades[0]  # Assume the most recent trade is the first item
            
            # Check if the most recent trade has changed
            if current_trade != last_trade:
                print('----------------------BEGIN MONITORED TRADE------------------------------------------')
                print(f"New trade detected for wallet {user_address}:")
                n.get_recent_trade_stats(current_trade)
                
                # n.filter_trade_by_size(current_trade)
                tail_trade = n.trade_type(current_trade, active_positions)
                if tail_trade:
                    n.send_to_tail_trades(tail_trade, current_trade)
                print('----------------------END MONITORED TRADE------------------------------------------')
                # Save the new trade to CSV
                # n.save_trade_to_csv(current_trade)
                
                # Update last_trade to the new trade
                last_trade = current_trade
                active_positions = new_active_positions
        else:
            print(f"No new trades found for wallet {user_address} or unexpected data format.")

def main():
    # # List of wallet addresses
    # proxy_wallets = proxy_wallets
    
    # Create and start a thread for each wallet address
    threads = []
    for wallet_info in proxy_wallets:
        wallet = wallet_info['proxyWallet']
        thread = Thread(target=monitor_wallet, args=(wallet,))
        thread.start()
        threads.append(thread)
    
    # Join all threads to ensure they complete
    for thread in threads:
        thread.join()

if __name__ == "__main__":
    main()
