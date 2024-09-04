'''
Can run bot this way, however console printouts wont make sense

Additionally, you can run every script seperately in it's own dedicated terminal
'''

import multiprocessing
import trade_tailer as trader
import risk_manager
import trade_monitor

user_address = '0x90e9bF6c345B68eE9fd8D4ECFAddb7Ee4F14c8f4'

def run_trade_monitor():
    trade_monitor.main()

def run_trader():
    trader.run_trade_tailer()

def run_risk_manager():
    risk_manager.run_risk_manager(user_address)

if __name__ == "__main__":
    # Create separate processes for each function
    processes = [
        multiprocessing.Process(target=run_trade_monitor),
        multiprocessing.Process(target=run_trader),
        multiprocessing.Process(target=run_risk_manager)
    ]

    # Start each process
    for process in processes:
        process.start()