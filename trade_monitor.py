import nice_funcs as n
import requests
import time
import csv
import os
from proxy_wallets import proxy_wallets
from threading import Thread

proxy_wallets = proxy_wallets

# def fetch_user_activity(user_address, limit=1, offset=0):
#     # Define the API endpoint with parameters
#     url = f"https://data-api.polymarket.com/activity?user={user_address}&limit={limit}&offset={offset}"
    
#     try:
#         # Make the GET request to fetch the user activity data
#         response = requests.get(url)
        
#         # Check if the request was successful
#         if response.status_code == 200:
#             # Parse the JSON data
#             data = response.json()
#             return data
#         else:
#             print(f"Request failed with status code: {response.status_code}")
#             return None
#     except Exception as e:
#         print(f"An error occurred: {e}")
#         return None

# def save_trade_to_csv(trade, filename='UPDATED_new_trades.csv'):
#     # Define the header and the row to be written
#     header = ['proxyWallet', 'timestamp', 'conditionId', 'type', 'size', 'usdcSize', 'transactionHash', 'price', 'asset', 'side', 'outcomeIndex', 'title', 'slug', 'icon', 'eventSlug', 'outcome', 'name', 'pseudonym', 'bio', 'profileImage', 'profileImageOptimized']
    
#     file_exists = os.path.isfile(filename)
    
#     with open(filename, mode='a', newline='') as file:
#         writer = csv.DictWriter(file, fieldnames=header)
        
#         # Write the header if the file does not exist
#         if not file_exists:
#             writer.writeheader()
        
#         # Write the trade data
#         writer.writerow(trade)

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
