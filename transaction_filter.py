# Import necessary libraries
from requests import get
import sys
import csv
import argparse
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()


# Get input from user using commend line
def positive_int(value):
    ivalue = int(value)
    if ivalue <= 0:
        raise argparse.ArgumentTypeError(f"{value} is not a positive integer")
    return ivalue


parser = argparse.ArgumentParser(description="inputs")
parser.add_argument("-a", "--amount", type=positive_int, default=1, help="Amount used to filter transactions")
parser.add_argument("-c", "--currency", choices=["USD", "ETH"], default="ETH", help="currency to filter by(USD or ETH)")
parser.add_argument("-b", "--block", type=positive_int, default=-1, help="Last block number to get information")
parser.add_argument("-n", "--num_blocks", type=positive_int, default=1,
                    help="Number of blocks to retrieve information from")
parser.add_argument("-o", "--output", default='out', help="Output file name")

args = parser.parse_args()

# API parameters
api_url = "https://api.etherscan.io/api"
api_key = os.getenv("API_KEY")  # Get API key from environment varia


def make_api_url(module, action, query_prames={}):
    """
    Creates the API URL with the specified module, action, and optional keyword arguments.

    Args:
        module (str): The module for the API.
        action (str): The action to perform within the module.
        query_prames: Optional dictionary with additional arguments for the API.

    Returns:
        str: The constructed API URL.
    """
    url = api_url + f"?module={module}&action={action}&apikey={api_key}"

    for key, value in query_prames.items():
        url += f"&{key}={value}"
    # print(url)
    return url


def get_currnt_block_num():
    """
    Retrieves the current block number using the Etherscan API.

    Returns:
        str: The current block number (Hex).
    """
    eth_blockNumber_url = make_api_url("proxy", "eth_blockNumber")
    response = get(eth_blockNumber_url)
    data = response.json()
    try:
        if (data["status"] == '0'):
            print('ERROR:' + data["result"])
            sys.exit()
    except:
        pass
    return data["result"]


def get_block_info(block_num):
    """
    Retrieves block information for the specified block number using the Etherscan API.

    Args:
        block_num (str): The block number (Hex).

    Returns:
        dict: The block information.
    """
    eth_getBlockByNumber_url = make_api_url("proxy", "eth_getBlockByNumber", {'tag': block_num, 'boolean': 'true'})
    response = get(eth_getBlockByNumber_url)
    data = response.json()

    try:
        if (data["status"] == '0'):
            print('ERROR:' + data["result"])
            sys.exit()
    except:
        pass

    return data["result"]


def export_list_of_dicts_to_csv(data, keys, filename):
    """
    Exports a list of dictionaries to a CSV file.

    Args:
        data (list): The list of dictionaries.
        keys (list): The keys of the dictionaries to be included in the CSV.
        filename (str): The name of the output CSV file.
    """
    with open(filename, 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=keys)
        writer.writeheader()
        for item in data:
            row = {key: item[key] for key in keys}
            writer.writerow(row)


def add_high_tx_to_list(transactions, high_tx_list, min_transaction_val, currency_to_filter_by):
    """
    Filters and adds high-value transactions to a list based on the specified amount and filter type.

    Args:
        transactions (list): The list of transactions.
        high_tx_list (list): The list to store the high-value transactions.
        min_transaction_val (int): The minimum value of transactions that will be exported.
        currency_to_filter_by ('str'): Determines whether the filtering is based on USD or ETH.
    """
    # Get the current ETH price in USD
    response = get(make_api_url('stats', 'ethprice'))
    data = response.json()
    if (data["status"] == '0'):
        print('ERROR:' + data["result"])
        sys.exit()
    ETHER_VALUE_USD = float(data['result']['ethusd'])
    ETHER_VALUE_wei = 10 ** 18
    ETHER_VALUE_Gwei = 10 ** 9

    for tx in transactions:
        tx_val = float.fromhex(tx["value"])
        tx['Value (ETH)'] = tx_val / ETHER_VALUE_wei
        tx['Value (USD)'] = tx_val / ETHER_VALUE_wei * ETHER_VALUE_USD
        tx_is_high = False

        if currency_to_filter_by == 'USD':  # filter by USD
            if tx['Value (USD)'] >= min_transaction_val:
                tx_is_high = True
        elif currency_to_filter_by == 'ETH':  # filter by ETH
            if tx['Value (ETH)'] >= min_transaction_val:
                tx_is_high = True

        if tx_is_high:
            tx['Block number'] = float.fromhex(tx["blockNumber"])
            tx['Gas price (Gwei)'] = float.fromhex(tx['gasPrice']) / ETHER_VALUE_Gwei
            tx['Gas price (USD)'] = tx['Gas price (Gwei)'] / ETHER_VALUE_Gwei * ETHER_VALUE_USD

            response = get(make_api_url('proxy', 'eth_getTransactionReceipt', {'txhash': tx['hash']}))
            data = response.json()
            try:
                if (data["status"] == '0'):
                    print('ERROR:' + data["result"])
                    sys.exit()
            except:
                pass
            gas_used = float.fromhex(data['result']['gasUsed'])

            tx['Transaction fee (ETH)'] = gas_used * tx['Gas price (Gwei)'] / ETHER_VALUE_Gwei
            tx['Transaction fee (USD)'] = tx['Transaction fee (ETH)'] * ETHER_VALUE_USD

            high_tx_list.append(tx)


def main(min_transaction_val=1, currency_to_filter_by='USD', last_block_to_extract=-1, num_of_blocks=1, out_name='out'):
    """
    Main function to execute the program.

    Args:
        min_transaction_val (int): The minimum value of transactions that will be exported.
        currency_to_filter_by (str): Determines whether the filtering is based on USD or ETH.
        last_block_to_extract (int): The last block number to get information from.
        num_of_blocks (int): The number of blocks to retrieve information from.
        out_name (str): The name of the output file.
    """
    high_tx_list = []
    current_block_num = int(get_currnt_block_num(), 16)

    assert last_block_to_extract <= current_block_num, "Block number does not exist yet"

    if last_block_to_extract == -1:
        last_block_to_extract = current_block_num

    for i in range(last_block_to_extract - num_of_blocks + 1, last_block_to_extract + 1):
        transactions = get_block_info(hex(i))["transactions"]
        add_high_tx_to_list(transactions, high_tx_list, min_transaction_val, currency_to_filter_by)

    keys_to_export = ['Block number', 'hash', 'from', 'to', 'Value (ETH)', 'Value (USD)',
                      'Gas price (Gwei)', 'Gas price (USD)', 'Transaction fee (ETH)', 'Transaction fee (USD)']
    export_list_of_dicts_to_csv(high_tx_list, keys_to_export, out_name + '.csv')
    print('DONE!')


# Run the script with user input
main(args.amount, args.currency, args.block, args.num_blocks, args.output)
