'''
holds all the relevant functions for working with polymarket
'''

import os
import csv
import json
import time
import requests
import pandas as pd
from datetime import datetime
from dotenv import load_dotenv
from web3 import Web3, exceptions
from py_clob_client.client import ClobClient
from py_clob_client.constants import POLYGON
from py_clob_client.order_builder.constants import BUY
from py_clob_client.clob_types import ApiCreds, OrderArgs, OrderType

user_address = '0x9d84ce0306f8551e02efef1680475fc0f1dc1344'

# returns proxy wallet dictionary / saves to proxy_wallets.py
def fetch_leaderboard() -> list:
    # The URL to fetch the leaderboard data - the URL will change from time to time
    #NOTE: the URL Changes -- Should probably look into this
    url = 'https://polymarket.com/_next/data/Qiek3ZtiJbjD_PULr6g8h/en/leaderboard.json'

    # Making the GET request to fetch the leaderboard data
    response = requests.get(url)

    # Check if the request was successful
    if response.status_code == 200:
        # Parse the JSON data
        leaderboard_data = response.json()
        data_list = leaderboard_data['pageProps']['dehydratedState']['queries'][6]['state']['data']

        # Extract proxy wallet addresses, amounts, and names
        proxy_wallets = [{'proxyWallet': entry['proxyWallet'], 'amount': entry['amount'], 'name': entry['name']} for entry in data_list]

        # Save the proxy_wallets list to a Python file as a variable
        with open('proxy_wallets.py', 'w') as f:
            f.write(f"proxy_wallets = {proxy_wallets}")
        print(type(proxy_wallets))
        print("Proxy wallets saved to proxy_wallets.py")
        return proxy_wallets

    else:
        print(f"Request failed with status code: {response.status_code}")

# fetch_leaderboard()

# returns dictionary of user address and the USDC value of their account
def fetch_user_value(user_address: str) -> dict[str, float]:
    # The URL with the query parameter
    url = f"https://data-api.polymarket.com/value?user={user_address}"

    # Make the GET request
    response = requests.get(url)

    # Check if the request was successful
    if response.status_code == 200:
        # Print the data received
        print(response.json()[0])
        user_value = response.json()[0]
        # returns a dictionary of 'user' and 'value'
        return user_value
    else:
        print(f"Request failed with status code: {response.status_code}")


# fetches ALL positions associated with a wallet address, returns the dataframe
def fetch_user_positions(user_address: str, limit: int = 10000, offset: int = 0) -> pd.DataFrame:
    # global all_positions_df
    
    # Define the API endpoint with parameters
    url = f"https://data-api.polymarket.com/positions?user={user_address}&limit={limit}&offset={offset}"
    
    # Initialize an empty DataFrame to store all positions
    all_positions_df = pd.DataFrame()

    try:
        # Make the GET request to fetch the user activity data
        response = requests.get(url)
        
        # Check if the request was successful
        if response.status_code == 200:
            # Parse the JSON data
            data = response.json()

            # Convert the list of dictionaries to a DataFrame
            positions_df = pd.DataFrame(data)
            
            # Append to the global DataFrame
            all_positions_df = pd.concat([all_positions_df, positions_df], ignore_index=True)
                
        else:
            print(f"Request failed with status code: {response.status_code}")
    except Exception as e:
        print(f"An error occurred: {e}")
    
    return all_positions_df


# takes ALL user positions DF as input, outputs only active positions
def get_active_positions(all_positions: pd.DataFrame) -> pd.DataFrame:
    
    all_positions['endDate'] = pd.to_datetime(all_positions['endDate'])

    today = datetime.now()

    # Filter the dataframe for active positions where 'endDate' is in the future
    active_positions_df = all_positions[all_positions['endDate'] >= today]

    # Now `active_positions_df` contains only the active positions
    return active_positions_df


# return the dictionary of a user's most recent trade
def fetch_most_recent_trade(user_address: str) -> dict:

    # Define the API endpoint with parameters
    url = f"https://data-api.polymarket.com/activity?user={user_address}&limit=1&offset=0"

    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()[0]
        return data
    
    else:
        print(f"Request failed with status code: {response.status_code}")
        return None
    

# prints out stats related to the most recent trade
def get_recent_trade_stats(new_trade: dict) -> None:

    print("#########TRADE STATS#####################")
    print(f"TITLE: {new_trade['title']}")
    print(f"OUTCOME: {new_trade['outcome']}")
    print(f"OUTCOME INDEX: {new_trade['outcomeIndex']}")
    print("------------------")
    print(f"SIDE: {new_trade['side']}")
    print(f"SIZE: {new_trade['size']}")
    print(f"PRICE: {new_trade['price']}")
    print(f"SIZE USD: {new_trade['usdcSize']}")
    print("#########TRADE STATS#####################")


# saves incoming trade from api into CSV
def save_trade_to_csv(trade, filename='UPDATED_new_trades.csv'):
    # Define the header and the row to be written
    header = ['proxyWallet', 'timestamp', 'conditionId', 'type', 'size', 'usdcSize', 'transactionHash', 'price', 'asset', 'side', 'outcomeIndex', 'title', 'slug', 'icon', 'eventSlug', 'outcome', 'name', 'pseudonym', 'bio', 'profileImage', 'profileImageOptimized', 'bot_executed']
    
    file_exists = os.path.isfile(filename)
    
    with open(filename, mode='a', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=header)
        
        # Write the header if the file does not exist
        if not file_exists:
            writer.writeheader()
        
        # Write the trade data
        writer.writerow(trade)


# Gets User trade data. Default is 20 most recent trades. Returns a List of Dictionaries
def fetch_user_activity(user_address: str, limit: int = 20) -> list[dict]:
    # Define the API endpoint with parameters
    url = f"https://data-api.polymarket.com/activity?user={user_address}&limit={limit}&offset=0"
    
    try:
        # Make the GET request to fetch the user activity data
        response = requests.get(url)
        
        # Check if the request was successful
        if response.status_code == 200:
            # Parse the JSON data
            data = response.json()
            return data
        else:
            print(f"Request failed with status code: {response.status_code}")
            return None
    except Exception as e:
        print(f"An error occurred: {e}")
        return None


def is_in_position(new_trade: dict, open_positions: pd.DataFrame) -> bool:
    # Extract the asset from the new trade
    new_trade_asset = new_trade.get('asset')
    asset_exists = open_positions[open_positions['asset'] == new_trade_asset]
    opposite_exists = open_positions[open_positions['oppositeAsset'] == new_trade_asset]
    if not asset_exists.empty:
        print(f"Asset {new_trade['asset']} is already a position in the open positions.")
        return True
    elif not opposite_exists.empty:
        print(f"Asset {new_trade['asset']} is the oppositeAsset of an open position.")
        return True
    else:
        print(f"Asset {new_trade['asset']} is not found in the open positions.")


# returns a printout and dataframe of the position stats associated with the position
def get_open_position_stats(new_trade: dict, open_positions: pd.DataFrame) -> pd.DataFrame:
    # returns a printout and dataframe of the position stats associated with the position 
    new_trade_asset = new_trade.get('asset')
    open_position = open_positions[open_positions['asset'] == new_trade_asset].copy()
    open_position['endDate'] = pd.to_datetime(open_position['endDate'])

    # Calculate 'timeToExpiry' as the difference between today and 'endDate'
    today = pd.to_datetime(datetime.now().date())
    
    # Calculate the difference in days
    open_position['timeToExpiry'] = (open_position['endDate'] - today).dt.days
    open_position['sharesSold'] = open_position['totalBought'] - open_position['size']
    open_position['pnlPerShare'] = open_position['realizedPnl'] / open_position['sharesSold']

    print(f"TITLE: {open_position['title'].iloc[0]}")
    print(f"OUTCOME: {open_position['outcome'].iloc[0]}")
    print(f"EXPIRES: {open_position['endDate'].iloc[0]}")
    print(f"TIME UNTIL EXPIRY: {open_position['timeToExpiry'].iloc[0]} DAYS")
    print("------------------")
    print(f"CURRENT POSITION SIZE: {round(open_position['size'].iloc[0], 3)}")
    print(f"AVG PRICE: {open_position['avgPrice'].iloc[0]}")
    print(f"CURRENT PRICE: ${open_position['curPrice'].iloc[0]}")
    print(f"INITIAL POS VALUE: ${round(open_position['initialValue'].iloc[0], 2)}")
    print(f"CURRENT POS VALUE: ${round(open_position['currentValue'].iloc[0], 2)}")
    print(f"CURRENT POS PnL: ${round(open_position['cashPnl'].iloc[0], 2)}")
    print(f"CURRENT POS ROI: {round(open_position['percentPnl'].iloc[0], 4)}%")
    print("------------------")
    print(f"TOTAL SHARES BOUGHT: {round(open_position['totalBought'].iloc[0], 5)}")
    print(f"SHARES SOLD OFF: {round(open_position['sharesSold'].iloc[0], 5)}")
    print(f"AVG PnL PER SHARE: ${round(open_position['pnlPerShare'].iloc[0], 4)}")
    print(f"REALIZED PnL: ${round(open_position['realizedPnl'].iloc[0], 2)}")
    print(f"REALIZED ROI: {round(open_position['percentRealizedPnl'].iloc[0], 4)}%")

    return open_position


# NOTE: working --> gets a specific position size relative to total position size
def position_over_value(user_address: str, asset: str) -> None:

    open_positions = fetch_user_positions(user_address)
    active_positions = get_active_positions(open_positions)

    active_positions_mean = active_positions['currentValue'].mean()
    active_positions_sum = active_positions['currentValue'].sum()

    specific_open_position = active_positions[active_positions['asset'] == asset].copy()
    specific_open_position_value = specific_open_position['currentValue'].iloc[0]
    position_over_total_percent = specific_open_position_value / active_positions_sum

    print(active_positions_sum)
    print(active_positions_mean)
    print(specific_open_position_value)
    print(position_over_total_percent)
    pass


def filter_trade_by_size(new_trade: dict, usd_size: int) -> bool:
    
    # throws out the trade if the size is too small
    size = new_trade['usdcSize']

    if size < usd_size:
        print(f'Trade size of {size} is too small, ignoring')
        return False
    else:
        print(f'Trade size of {size} large enough for consideration')
        return True


def trade_type(new_trade: dict, active_positions: pd.DataFrame, usd_size: int = 75) -> bool:

    tail_trade = False

    new_trade_asset = new_trade.get('asset')
    active_positions = active_positions[active_positions['asset'] == new_trade_asset].copy()

    if is_in_position(new_trade, active_positions):

        # NOTE: keep in mind, the open positions may reflect the incoming trade already
        position_value = active_positions["currentValue"].iloc[0]
        trade_value = new_trade["usdcSize"]
        position_pnl = active_positions["percentPnl"].iloc[0]

        if new_trade['side'] == 'BUY':
            print(f'current_pos value is: {position_value}')
            print(f'trade value is: {trade_value}')
            print(f'position unrealized PnL: {position_pnl}')
            added_percent = (trade_value / position_value)
            if position_pnl > 0:
                # we want this trade
                print(f'user is ADDING to WINNING position')
                print(f'Size ADDED relative to open position: {round((added_percent * 100), 3)}%')
                if filter_trade_by_size(new_trade, usd_size):
                    tail_trade = True
                else:
                    tail_trade = False
                print(f'tail_trade is: {tail_trade}')
            else:
                # not really sure if we want this trade.. for now, we dont
                print(f'user is ADDING to LOSING position')
                print(f'Size ADDED relative to open position: {round((added_percent * 100), 3)}%')
                tail_trade = False
                print(f'tail_trade is: {tail_trade}')

        elif new_trade['side'] == 'SELL':
            print(f'current_pos value is: {position_value}')
            print(f'trade value is: {trade_value}')
            print(f'position unrealized PnL: {position_pnl}')
            subtracted_percent = (- trade_value) / position_value

            if position_pnl > 0:
                # we want to filter this out
                print(f'user is SELLING WINNING position')
                print(f'Size SOLD relative to open position: {round((subtracted_percent * 100), 3)}%')
                tail_trade = False
                print(f'tail_trade is: {tail_trade}')
            else:
                # we want to filter this out
                print(f'user is SELLING LOSING position')
                print(f'Size SOLD relative to open position: {round((subtracted_percent * 100), 3)}%')
                tail_trade = False
                print(f'tail_trade is: {tail_trade}')

        else:
            print('Side not specified, probably a merge or other non-trade action')

    else:
        print('This is an opening of a new position, checking Size Filter...')
        # if the trade is not an open position already, we should take it, if it's over our size threshold
        if filter_trade_by_size(new_trade, usd_size):
            tail_trade = True
            print(f'tail_trade is: {tail_trade}')
        else:
            tail_trade = False
            print(f'tail_trade is: {tail_trade}')

    return tail_trade


def send_to_tail_trades(tail_trade: bool, trade_data: dict, file_path: str = 'tail_trades.json'):
    if tail_trade:
        # Check if the file already exists
        if os.path.exists(file_path):
            # Load existing trades from the file
            with open(file_path, 'r') as file:
                trades = json.load(file)
        else:
            # Start with an empty list if the file doesn't exist
            trades = []

        trade_data['bot_executed'] = False
        # Append the new trade data
        trades.append(trade_data)

        # Write the updated list back to the file
        with open(file_path, 'w') as file:
            json.dump(trades, file, indent=4)

        print(f"Trade added to {file_path}: {trade_data}")


def connect_to_polygon() -> Web3:
    # Connect to Polygon via an Infura or Alchemy endpoint (or other RPC provider)
    polygon_rpc_url = "https://polygon-rpc.com"  # You can use Infura or Alchemy URLs as well
    web3 = Web3(Web3.HTTPProvider(polygon_rpc_url))

    if web3.is_connected():
        print("Connected to Polygon")
    else:
        print("Connection failed")

    return web3


def get_wallet_balance(user_address: str, max_retries=5, retry_delay=10) -> float:
    web3 = connect_to_polygon()

    retries = 0
    while retries < max_retries:
        try:
            # Get the balance in Wei (the smallest unit of MATIC)
            balance_wei = web3.eth.get_balance(user_address)

            # Convert the balance to MATIC (1 MATIC = 1e18 Wei)
            balance_matic = web3.from_wei(balance_wei, 'ether')
            print(f"Balance for wallet {user_address}: {balance_matic} MATIC")

            # USDC contract address on Polygon
            usdc_contract_address = "0x2791Bca1f2de4661ED88A30C99A7a9449Aa84174"

            # ABI for ERC-20 token balanceOf function
            erc20_abi = [
                {
                    "constant": True,
                    "inputs": [{"name": "_owner", "type": "address"}],
                    "name": "balanceOf",
                    "outputs": [{"name": "balance", "type": "uint256"}],
                    "type": "function",
                }
            ]

            # Create a contract object
            usdc_contract = web3.eth.contract(address=usdc_contract_address, abi=erc20_abi)

            # Get the balance of USDC for the wallet
            balance_wei = usdc_contract.functions.balanceOf(user_address).call()

            # Convert the balance to the appropriate decimal (USDC has 6 decimals)
            balance_usdc = balance_wei / 10**6
            print(f"USDC Balance for wallet {user_address}: {balance_usdc} USDC")

            return balance_usdc

        except exceptions.BadResponseFormat as e:
            print(f"Error fetching balance: {e}")
            print("Retrying...")

            # Optional: Exponential backoff logic or constant delay
            retries += 1
            time.sleep(retry_delay)
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            # Handle other exceptions if needed
            break

    print(f"Failed to fetch balance after {max_retries} retries.")
    return 0.0  # Return a default value or handle accordingly


def create_clob_client(funder_address: str) -> ClobClient:

    load_dotenv()

    host = "https://clob.polymarket.com"
    key = os.getenv("WPK")
    funder=funder_address
    creds = ApiCreds(
        api_key=os.getenv("WPK_CLOB_API_KEY"),
        api_secret=os.getenv("WPK_CLOB_SECRET"),
        api_passphrase=os.getenv("WPK_CLOB_PASS_PHRASE"),
    )
    chain_id = POLYGON
    client = ClobClient(host, key=key, chain_id=chain_id, creds=creds, signature_type=1, funder=funder)

    return client


def create_order(client: ClobClient, price: float, size: float, side: str, asset: str) -> None:
    order_args = OrderArgs(
        price=price,
        size=size,
        side=side,
        token_id=asset
    )

    signed_order = client.create_order(order_args)
    resp = client.post_order(signed_order, OrderType.GTC)
    print(resp)


def process_tail_trades():
    with open("tail_trades.json", "r") as file:
        for line in file:
            trade_info = json.loads(line.strip())
            # Process the trade
            print(f"Processing tail trade: {trade_info}")