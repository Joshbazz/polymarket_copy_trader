project: Polymarket, a decentralized 'information market' (read: betting platform), running on Polymarket,
has a leaderboard. These bettors are pretty good. So, we want to copy their trades in smaller size from our 
own account.

a proxy wallet is the wallet that holds your balance on poly market.
    -> This is what we should be looking against
    -> for future reference:
        -> the proxy wallet, its public address, and the private key are what you need
        -> these are used for creating api keys and setting allowances for
        -> i had to send the public address MATIC so i could cover the gas fees for setting allowances
    -> thoughts:
        -> there should (not right now, later) be a feature for ID'ing a trade as building into a position
        or cutting out of one [DONE]
        -> blindly following trades from the leaderboard doesnt provide enough context

erc1155 represent the shares of the long/short position
    -> these will be from a contract, to our proxy address
    -> The inverse will be a transfer of ERC20 from our proxy address to exchange contract


workflow:
    -> get the proxy wallets from the leaderboard [done]
    -> monitor the polygon blockchain for transactions related to the proxy wallets [done]
        -> we need to rank or follow wallets by their ROI on positions i think, not on raw PnL
        -> you could be leading because you lucked out, not because you're good at betting
    -> identify the market they are trading [done]
        -> assetAddress seems to be the polygon address of the contract [correct]
    -> copy the trade from personal proxy wallet [working]
    -> log trades to a database [TODO]
    -> create streamlit front end [TODO]
    -> connect front end to the database [TODO]


NOTE: positions data gets ALL positions. Not Just ACTIVE ones

To do:
-> connect leaderboard trades to my account, trade that
    -> grab by condition ID, or asset/tokenID [DONE]
    -> place similar order through my account [working]

-> create data frame or SQLite DB from new_trades CSV
    -> filter by tx ID or something close to cut out double counts
        -> ALL_new_trades from terminal will be saved in a different directory -- move csv to project directory and clean
    -> move trade monitor to backup to SQLite DB

[NOTE] => can i scrape discord for the new polymarket markets?

[NOTE] => does the amount of trades change the formula for following the quality of an address's trades?

8/20/24 -> [TODO]
-> add WORKING_leaderboard_updated.py function to nice_funcs [DONE]
-> Get monitor_wallet to return the right data
    -> get threads to combine correctly
        -> 8/26/24 [UPDATE] => not important, pushing to json file
-> filter monitor_wallet trade data for miniscule USDC size [DONE]
    -> slightly -- we are getting this handled with filter_trade_by_size
-> compare monitor_wallet data with open_positions [DONE]
    -> check NEW_BUY, NEW_SELL, TAKE_PROFIT, STOP_LOSS
        -> Have ADDING done
-> GOAL: Get trades, copy with minimum size (~0.50% of capital) [WORKING]

8/23/24:
-> Goal remains the same
-> Monitor_wallet function is too difficult to work with in its current state -- it's better to build out the functionality in nice_funcs, and combine later on
-> trade_type is the operative function right now -- this will determine if we are copying or not
    -> trade_type returns a tail_trade bool
        -> if the bool is True, we should use this bool in another function that handles our personal trading

DO NOT FUCK WITH TESTING_USER_ACTIVITY. THAT IS THE WORKING COPY

8/24/24 [TODO]
1. Get tail_trade to eval to True if not already in position [DONE]
2. Turn trading script.md into code

8/27/24 [TODO]
GOAL: Get trades, copy with minimum size (~0.50% of capital)
NOTE: tail_trade is eval'ing to TRUE if the trade hits all params, but isnt a BUY or SELL
1. Need to look at this. We dont want to tail a MERGE, if that's even possible
2. Turn trading_script.md into code
 - read in tail_trades.json, create orders, and flip bot_executed to True